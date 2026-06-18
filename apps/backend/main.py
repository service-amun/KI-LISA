# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — FastAPI Backend
EU-konformer KI-Assistent für KMU.
"""

import hmac
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# .env laden (lokal: apps/backend/.env, Railway: ENV-Vars)
load_dotenv(Path(__file__).parent / ".env")

# Eigene Module (sys.path damit relative Imports funktionieren)
sys.path.insert(0, str(Path(__file__).parent))

import database
import groq_client
import agent_runtime
import session_manager
from audit.audit_logger import write_audit_entry, get_audit_entries
from skills.guardrail_skill import check_input, restore_tokens
from skills.router_skill import classify as route_query
from skills.reflection_skill import kontext_aufbauen, auto_extrahieren
from compliance.weekly_checker import bericht as compliance_bericht, komplett_check
from compliance.scheduler import starten as compliance_starten
from routers.approvals import router as approvals_router
from routers.datei_upload import router as upload_router
import gateway as tool_gateway

# Compliance-Scheduler beim Start aktivieren (daemon thread)
compliance_starten()

# DSGVO Art. 5(1)(e) — Datenspeicherbegrenzung: alte Sessions beim Start bereinigen
def _dsgvo_retention_loop():
    import threading as _t
    import time as _time
    def _bereinigen():
        try:
            n = session_manager.cleanup_alte_sessions()
            if n:
                print(f"[AILIZA] DSGVO Retention: {n} Session(s) gelöscht (Art. 5).", flush=True)
        except Exception as e:
            print(f"[AILIZA] DSGVO Retention Fehler: {e}", flush=True)
    _bereinigen()  # Einmal beim Start
    def _wochentlich():
        while True:
            _time.sleep(7 * 24 * 60 * 60)
            _bereinigen()
    _t.Thread(target=_wochentlich, daemon=True, name="dsgvo-retention").start()

import threading as _thread_mod
_thread_mod.Thread(target=_dsgvo_retention_loop, daemon=True, name="dsgvo-retention-init").start()

# ── PII-Zwischenspeicher (nur Arbeitsspeicher, nie auf Disk) ─────────────────
# session_id → {token: originalwert}
# Wird gelöscht wenn Session gelöscht wird oder Server neu startet.
_pii_zwischenspeicher: dict[str, dict] = {}

# ── App ──────────────────────────────────────────────────────────────────────

_DEBUG = os.getenv("AILIZA_DEBUG", "false").lower() == "true"

app = FastAPI(
    title="AILIZA",
    description="EU-konformer KI-Assistent für KMU — DSGVO + EU AI Act konform | © 2026 Karola Fromm-Nasreldin",
    version="0.3.0",
    docs_url="/docs" if _DEBUG else None,
    redoc_url=None,
)

# Lokaler Betrieb: nur localhost erlaubt. Railway: AILIZA_ALLOWED_ORIGIN setzen.
_ALLOWED_ORIGIN = os.getenv("AILIZA_ALLOWED_ORIGIN", "http://127.0.0.1:8001")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[_ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(approvals_router)
app.include_router(upload_router)

# Frontend ausliefern
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ── Rate Limiting ─────────────────────────────────────────────────────────────

_rate_store: dict = defaultdict(list)
RATE_LIMIT = 20


def check_rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = [t for t in _rate_store[ip] if now - t < 60]
    if len(window) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Zu viele Anfragen. Bitte warte eine Minute.",
        )
    window.append(now)
    _rate_store[ip] = window


# ── Pydantic Modelle ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=4000)
    model: str = Field(default="standard")
    eigene_anweisungen: str = Field(default="", max_length=1000)


class NewSessionRequest(BaseModel):
    title: str = Field(default="Neuer Chat", max_length=100)


class PinRequest(BaseModel):
    pin: str = Field(..., min_length=1, max_length=50)


class AgentRunRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=2000)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.3.0",
        "ki_konfiguriert": groq_client.is_configured(),
        "compliance": "EU AI Act Art. 52 · DSGVO konform",
        "risikoklasse": "Limited Risk",
    }


# ── Auth (optionaler Zugangscode) ────────────────────────────────────────────

@app.get("/auth/required")
def auth_required():
    """Teilt dem Frontend mit ob ein Zugangscode konfiguriert ist."""
    return {"required": bool(os.getenv("AILIZA_ACCESS_PIN", ""))}


@app.post("/auth/verify")
def auth_verify(body: PinRequest, request: Request):
    """Prüft den Zugangscode. Timing-sicher via hmac.compare_digest."""
    pin = os.getenv("AILIZA_ACCESS_PIN", "")
    if not pin:
        return {"ok": True}
    if not hmac.compare_digest(body.pin.encode(), pin.encode()):
        write_audit_entry("auth.failed", {"ip": request.client.host if request.client else None})
        raise HTTPException(status_code=401, detail="Falscher Zugangscode.")
    write_audit_entry("auth.login", {"ip": request.client.host if request.client else None})
    return {"ok": True}


@app.get("/config/public")
def public_config():
    """Öffentliche Konfiguration für das Frontend — Datenschutzmodaltext."""
    return {
        "company_name": os.getenv("AILIZA_COMPANY_NAME", "Ihr Unternehmen"),
        "dsb_email": os.getenv("AILIZA_DSB_EMAIL", "datenschutz@ihr-unternehmen.de"),
        "retention_days": int(os.getenv("AILIZA_DATA_RETENTION_DAYS", "90")),
    }


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/dashboard")
@app.get("/")
def dashboard():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"info": "AILIZA Backend läuft. Frontend unter apps/frontend/index.html einrichten."})


# ── Sessions (Chat mit Compliance-Kontext) ─────────────────────────────────────

@app.get("/sessions")
def list_sessions(limit: int = 50):
    return session_manager.list_sessions(limit=min(limit, 1000))


@app.post("/sessions")
def create_session(body: NewSessionRequest):
    session = session_manager.create_session(title=body.title)
    return {"session_id": session.session_id, "title": session.title}


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat nicht gefunden.")
    return {
        "session_id": session.session_id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "message_count": len(session.messages),
        "messages": [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp, "warnings": m.warnings}
            for m in session.messages
        ],
        "compliance": {
            "dsgvo_articles": session.active_dsgvo_articles,
            "eu_ai_act_articles": session.active_eu_ai_act_articles,
            "warnings": session.accumulated_warnings,
            "risk_level": session.risk_level,
            "requires_human_oversight": session.requires_human_oversight,
        },
    }


@app.post("/sessions/{session_id}/chat")
def chat_in_session(session_id: str, body: ChatRequest, request: Request):
    check_rate_limit(request)

    if not session_manager.get_session(session_id):
        raise HTTPException(status_code=404, detail="Chat nicht gefunden.")

    # ── Schritt 1: Guardrail — PII tokenisieren ───────────────────────────
    # Bestehendes Token-Mapping der Session übergeben (Konsistenz über Nachrichten)
    bestehendes_mapping = _pii_zwischenspeicher.get(session_id, {})
    guard = check_input(body.message, existing_token_map=bestehendes_mapping)

    if guard.blocked:
        return {
            "text": guard.block_reason,
            "warnings": [],
            "blocked": True,
            "compliance": {},
        }

    # ── Schritt 2: Neues Mapping im Zwischenspeicher ablegen ─────────────
    if guard.token_map:
        _pii_zwischenspeicher[session_id] = guard.token_map

    # Tokenisierter Text geht an LLM — Original bleibt im RAM (nie in SQLite)
    llm_text  = guard.sanitized_text or body.message   # Token-Version für LLM + Speicherung
    user_text = body.message                            # Original nur für Anzeige im Frontend

    # ── Schritt 3: Tokenisierte Nachricht speichern (DSGVO Art. 25 — kein PII auf Disk) ──
    session_manager.add_message(session_id, "user", llm_text, warnings=guard.warnings)

    # ── Human Oversight VOR LLM-Aufruf anlegen (EU AI Act Art. 14) ───────
    session_vor_llm = session_manager.get_session(session_id)
    if session_vor_llm and session_vor_llm.requires_human_oversight:
        database.create_approval(
            run_id=0,
            task=llm_text[:200],   # Tokenisiert — kein PII
            reason="Hochrisiko-Anfrage erkannt (EU AI Act Art. 6, Art. 14)",
        )

    # ── Schritt 4: Routing + Reflection + LLM-Aufruf ─────────────────────
    route = route_query(llm_text)          # Modell, Token-Budget, Temperatur
    system_prompt = session_manager.get_system_prompt(session_id, llm_text)
    if body.eigene_anweisungen:
        guard_anw = check_input(body.eigene_anweisungen)
        anw_text = guard_anw.sanitized_text or body.eigene_anweisungen
        system_prompt = anw_text.strip() + "\n\n" + system_prompt

    # Relevante Erinnerungen aus früheren Gesprächen anhängen
    gedaechtnis = kontext_aufbauen(llm_text)
    if gedaechtnis:
        system_prompt = system_prompt + "\n\n" + gedaechtnis

    # Kontext tokenisieren — nur so viele Nachrichten wie der Router empfiehlt
    kontext_roh = session_manager.get_context_messages(
        session_id, max_messages=route.kontext_nachrichten + 1
    )
    kontext_sauber = [
        {
            "role": m["role"],
            "content": _tokenisiere_kontext(m["content"], guard.token_map),
        }
        for m in kontext_roh[:-1]  # aktuelle Nachricht bereits als `message` übergeben
    ]

    response = groq_client.chat(
        message=llm_text,
        system_prompt=system_prompt,
        context=kontext_sauber,
        model=body.model if body.model != "standard" else route.modell,
        max_tokens=route.max_tokens,
        temperature=route.temperature,
    )

    # ── Schritt 5: Tokens ersetzen + Fakten in Gedächtnis speichern ──────
    aktuelles_mapping = _pii_zwischenspeicher.get(session_id, {})
    antwort_text = restore_tokens(response.text, aktuelles_mapping)

    # Wichtige Fakten aus der restaurierten Antwort merken
    auto_extrahieren(antwort_text, session_id)

    # ── Schritt 6: Wiederhergestellte Antwort speichern ──────────────────
    session_manager.add_message(session_id, "assistant", antwort_text)
    session = session_manager.get_session(session_id)

    # ── Schritt 7: Audit-Log — KEINE Klardaten, nur Metadaten ───────────
    write_audit_entry("session.chat", {
        "session_id": session_id[:8] + "...",
        "model": response.model,
        "tokens": response.tokens_used,
        "ip": request.client.host if request.client else None,
        "pii_typen": guard.pii_found,           # Nur Typ (E-Mail, Telefon...), kein Wert
        "pii_tokens_gesamt": len(aktuelles_mapping),
        "human_oversight": session.requires_human_oversight if session else False,
    })

    return {
        "text": antwort_text,                   # Restaurierter Text — PII-Tokens durch Originalwerte ersetzt
        "platzhalter": aktuelles_mapping,       # Token → Originalwert (für Klick-Einsetzung im Frontend)
        "model": response.model,
        "tokens_used": response.tokens_used,
        "warnings": guard.warnings,
        "blocked": False,
        "compliance": {
            "risk_level": session.risk_level if session else "low",
            "requires_human_oversight": session.requires_human_oversight if session else False,
            "warnings": guard.warnings,
        },
        "is_ai": True,
        "disclaimer": "KI-generiert — AILIZA (EU AI Act Art. 52)",
    }


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """DSGVO Art. 17 — Recht auf Löschung."""
    session_manager.delete_session(session_id)
    # PII-Zwischenspeicher für diese Session ebenfalls löschen
    _pii_zwischenspeicher.pop(session_id, None)
    write_audit_entry("session.deleted", {"session_id": session_id[:8] + "..."})
    return {"status": "gelöscht", "hinweis": "Alle Daten dieser Session wurden entfernt (DSGVO Art. 17)."}


@app.post("/sessions/{session_id}/oversight-confirmed")
def oversight_confirmed(session_id: str, request: Request):
    """EU AI Act Art. 14 — Menschliche Aufsicht: Nutzer bestätigt eigenverantwortliche Prüfung."""
    if not session_manager.get_session(session_id):
        raise HTTPException(status_code=404, detail="Chat nicht gefunden.")
    write_audit_entry("oversight.confirmed", {
        "session_id": session_id[:8] + "...",
        "ip": request.client.host if request.client else None,
        "hinweis": "Nutzer hat Hochrisiko-Antwort eigenverantwortlich geprüft (EU AI Act Art. 14)",
    })
    return {"status": "bestätigt", "compliance": "EU AI Act Art. 14 — Menschliche Aufsicht dokumentiert"}


def _tokenisiere_kontext(text: str, token_map: dict) -> str:
    """Ersetzt im Kontext-Verlauf Originaldaten durch Tokens (für LLM-Aufruf)."""
    if not token_map:
        return text
    result = text
    for token, original in token_map.items():
        result = result.replace(original, token)
    return result


# ── Agent (Web-Suche / URL-Abruf) ─────────────────────────────────────────────

@app.post("/agent/run")
def agent_run(body: AgentRunRequest, request: Request):
    check_rate_limit(request)

    guard = check_input(body.task)
    if guard.blocked:
        return {"status": "blocked", "message": guard.block_reason, "results": []}

    run_id = database.create_run(body.task)
    # Gateway: Guardrails + Audit für jeden Tool-Aufruf
    task_lower = body.task.lower()
    if task_lower.startswith("http://") or task_lower.startswith("https://"):
        from urllib.parse import urlparse
        parsed = urlparse(body.task)
        if parsed.scheme not in ("https",):
            return {"status": "blocked", "message": "Nur HTTPS-URLs erlaubt.", "results": []}
        host = parsed.hostname or ""
        blocked_prefixes = ("127.", "10.", "192.168.", "169.254.", "::1", "localhost")
        if any(host.startswith(p) for p in blocked_prefixes):
            return {"status": "blocked", "message": "Interne Adressen nicht erlaubt.", "results": []}
        results = [tool_gateway.ausfuehren("abruf", body.task)]
    else:
        results = [tool_gateway.ausfuehren("suche", body.task)]

    all_success = all(r.success for r in results)
    database.finish_run(
        run_id,
        result=str([r.summary for r in results]),
        status="completed" if all_success else "failed",
    )

    write_audit_entry("agent.run", {
        "run_id": run_id,
        "task_len": len(body.task),
        "tools_used": [r.tool for r in results],
        "ip": request.client.host if request.client else None,
    })

    return {
        "run_id": run_id,
        "status": "completed" if all_success else "partial",
        "results": [{"tool": r.tool, "success": r.success, "summary": r.summary, "error": r.error} for r in results],
        "warnings": guard.warnings,
    }


@app.get("/agent/runs")
def get_runs():
    return database.get_runs()


@app.get("/agent/runs/{run_id}")
def get_run(run_id: int):
    run = database.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Lauf nicht gefunden.")
    return run


# ── Tools (direkt) ─────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class FetchRequest(BaseModel):
    url: str = Field(..., min_length=10, max_length=2000)


@app.post("/tools/search")
def tool_search(body: SearchRequest, request: Request):
    check_rate_limit(request)
    result = tool_gateway.ausfuehren("suche", body.query)
    return {"success": result.success, "summary": result.summary, "error": result.error}


@app.post("/tools/fetch")
def tool_fetch(body: FetchRequest, request: Request):
    check_rate_limit(request)
    result = tool_gateway.ausfuehren("abruf", body.url)
    return {"success": result.success, "summary": result.summary, "error": result.error}


@app.get("/tools")
def tools_liste():
    """Listet verfügbare Tools mit Beschreibung."""
    from tools.standard_tools import tool_info
    return tool_info()


# ── Audit-Log ─────────────────────────────────────────────────────────────────

@app.get("/audit-logs")
def audit_logs(request: Request, limit: int = 50):
    token = request.headers.get("X-Admin-Token", "")
    admin_token = os.getenv("AILIZA_ADMIN_TOKEN", "")
    if not admin_token or not hmac.compare_digest(token.encode(), admin_token.encode()):
        raise HTTPException(status_code=403, detail="Zugriff verweigert.")
    return get_audit_entries(limit=min(limit, 200))


# ── KI-Status ─────────────────────────────────────────────────────────────────

@app.get("/ai/status")
def ai_status():
    return {
        "konfiguriert": groq_client.is_configured(),
        "anbieter": "Groq",
        "modelle": list(groq_client.MODELS.keys()),
        "compliance": "EU AI Act Art. 52 — AILIZA aktiv",
        "risikoklasse": "Limited Risk",
    }


@app.get("/ai/test")
def ai_test():
    """Testet Groq-Verbindung mit echtem API-Aufruf. Zeigt genauen Fehlercode."""
    import urllib.request, urllib.error, json as _json, os as _os
    key = _os.getenv("GROQ_API_KEY", "")
    if not key:
        return {"ok": False, "fehler": "GROQ_API_KEY nicht gesetzt", "tipp": "apps/backend/.env prüfen"}
    payload = _json.dumps({
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": "Antworte nur mit: OK"}],
        "max_tokens": 10,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = _json.loads(r.read())
        return {"ok": True, "antwort": data["choices"][0]["message"]["content"], "modell": "llama-3.1-8b-instant"}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[AILIZA] /ai/test Fehler — HTTP {e.code}: {body[:300]}", flush=True)
        tipp = {
            401: "Ungültiger API-Key — neuen Key auf console.groq.com erstellen",
            429: "Zu viele Anfragen — kurz warten und erneut versuchen",
            400: "Anfragefehler — Modellname oder Parameter ungültig",
            403: "Zugriff verweigert — Key hat keine Berechtigung",
        }.get(e.code, "Unbekannter Fehler")
        return {"ok": False, "http_code": e.code, "antwort": body[:300], "tipp": tipp}
    except Exception as e:
        print(f"[AILIZA] /ai/test Verbindungsfehler — {e}", flush=True)
        return {"ok": False, "fehler": str(e), "tipp": "Internetverbindung prüfen"}


# ── Compliance ────────────────────────────────────────────────────────────────

def _check_admin_token(request: Request):
    """Shared helper — raises 403 if X-Admin-Token is missing or wrong."""
    token = request.headers.get("X-Admin-Token", "")
    admin_token = os.getenv("AILIZA_ADMIN_TOKEN", "")
    if not admin_token or not hmac.compare_digest(token.encode(), admin_token.encode()):
        raise HTTPException(status_code=403, detail="Zugriff verweigert.")


@app.get("/compliance/status")
def compliance_status():
    """Letzter Compliance-Bericht ohne neuen Netzwerkaufruf. Öffentlich lesbar — keine sensiblen Daten."""
    return compliance_bericht()


@app.post("/compliance/check")
def compliance_check(request: Request):
    """
    Vollständiger Check: EUR-Lex HEAD → ggf. Volltext + LLM-Zusammenfassung
    → RAG-Gedächtnis-Update → Bericht.
    Kann einige Sekunden dauern wenn Gesetze sich geändert haben.
    Admin-geschützt: schreibt ins RAG-Gedächtnis.
    """
    _check_admin_token(request)
    return komplett_check()


@app.get("/compliance/updates")
def compliance_updates():
    """Zeigt gespeicherte Gesetzesänderungen aus dem RAG-Gedächtnis. Öffentlich lesbar."""
    from skills.reflection_skill import erinnern
    erinnerungen = erinnern("gesetzesänderung aktualisierung dsgvo eu ai act pflicht", limit=10)
    return [
        {
            "inhalt": e.inhalt,
            "wichtigkeit": e.wichtigkeit,
            "erstellt": e.erstellt,
        }
        for e in erinnerungen
        if "aktualisierung" in e.stichwörter.lower() or "gesetzesänderung" in e.stichwörter.lower()
    ]
