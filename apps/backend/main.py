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
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# .env laden (lokal: apps/backend/.env, Railway: ENV-Vars)
load_dotenv(Path(__file__).parent / ".env")

# Startup: Admin-Token aus ENV oder temporär generieren
import secrets as _secrets
_admin_token_env = os.getenv("AILIZA_ADMIN_TOKEN", "")
if not _admin_token_env:
    _admin_token_env = _secrets.token_hex(16)
    print(f"[AILIZA] WARNUNG: AILIZA_ADMIN_TOKEN nicht gesetzt.", flush=True)
    print(f"[AILIZA] Temporäres Admin-Token: {_admin_token_env}", flush=True)
    print("[AILIZA] Bitte AILIZA_ADMIN_TOKEN in apps/backend/.env dauerhaft setzen.", flush=True)

# Hinweis wenn Firma noch nicht konfiguriert
_company = os.getenv("AILIZA_COMPANY_NAME", "Ihr Unternehmen")
_dsb_email = os.getenv("AILIZA_DSB_EMAIL", "datenschutz@ihr-unternehmen.de")
if _company == "Ihr Unternehmen" or _dsb_email == "datenschutz@ihr-unternehmen.de":
    print("[AILIZA] HINWEIS: AILIZA_COMPANY_NAME und/oder AILIZA_DSB_EMAIL sind noch Platzhalter.", flush=True)
    print("[AILIZA] Bitte in apps/backend/.env mit echten Firmendaten befüllen (DSGVO Art. 13 / DDG §5).", flush=True)

# Fail-closed Status anzeigen — wichtig für Upgrades von älteren Versionen
_llm_env = os.getenv("AILIZA_EXTERNAL_LLM_ENABLED", "")
if not _llm_env or _llm_env.lower().strip() not in {"true", "1", "yes", "on"}:
    print("[AILIZA] KI-CHAT DEAKTIVIERT: AILIZA_EXTERNAL_LLM_ENABLED ist nicht gesetzt oder 'false'.", flush=True)
    print("[AILIZA] Setze AILIZA_EXTERNAL_LLM_ENABLED=true in apps/backend/.env um den KI-Chat zu aktivieren.", flush=True)
else:
    print("[AILIZA] KI-Chat aktiviert (AILIZA_EXTERNAL_LLM_ENABLED=true).", flush=True)

_mem_env = os.getenv("AILIZA_MEMORY_ENABLED", "")
if _mem_env and _mem_env.lower().strip() in {"true", "1", "yes", "on"}:
    print("[AILIZA] Langzeitspeicher aktiviert (AILIZA_MEMORY_ENABLED=true).", flush=True)

# Eigene Module (sys.path damit relative Imports funktionieren)
sys.path.insert(0, str(Path(__file__).parent))

import database
import groq_client
import agent_runtime
import session_manager
from audit.audit_logger import write_audit_entry, get_audit_entries
from ailiza_guard import enforce_policy
from skills.guardrail_skill import restore_tokens
from skills.router_skill import classify as route_query
from skills.reflection_skill import kontext_aufbauen, auto_extrahieren
from compliance.weekly_checker import bericht as compliance_bericht, komplett_check
from compliance.scheduler import starten as compliance_starten
from routers.approvals import router as approvals_router
from routers.datei_upload import router as upload_router
import gateway as tool_gateway

# Compliance-Scheduler beim Start aktivieren (daemon thread)
compliance_starten()

def _dsgvo_retention_loop():
    """DSGVO Art. 5(1)(e) — täglich alte Sessions löschen."""
    import time as _time
    # Einmal beim Start
    try:
        n = session_manager.cleanup_alte_sessions()
        if n:
            print(f"[AILIZA] DSGVO Retention: {n} Session(s) gelöscht.", flush=True)
    except Exception as e:
        print(f"[AILIZA] Retention-Fehler beim Start: {e}", flush=True)
    # Dann täglich
    while True:
        _time.sleep(86400)
        try:
            n = session_manager.cleanup_alte_sessions()
            if n:
                print(f"[AILIZA] DSGVO Retention: {n} Session(s) gelöscht.", flush=True)
        except Exception as e:
            print(f"[AILIZA] Retention-Fehler: {e}", flush=True)

import threading as _thread_mod
_thread_mod.Thread(target=_dsgvo_retention_loop, daemon=True, name="dsgvo-retention").start()

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

# Lokaler Betrieb: nur localhost erlaubt.
# Railway/Cloud: AILIZA_ALLOWED_ORIGIN=* oder kommagetrennte Liste setzen.
_origins_raw = os.getenv("AILIZA_ALLOWED_ORIGIN", "http://127.0.0.1:8001")
_ALLOWED_ORIGINS = [o.strip() for o in _origins_raw.split(",") if o.strip()] or ["http://127.0.0.1:8001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
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
    # 20000: PDF-Text (max 15000) + Dateiname-Header + Trennzeile + Nutzerfrage
    message: str = Field(..., min_length=1, max_length=20000)
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

_CLOUD = bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("AILIZA_CLOUD_MODE"))


def _setup_erforderlich() -> bool:
    """True wenn Firmendaten noch nicht gesetzt sind. Nie im Cloud-Betrieb."""
    if _CLOUD:
        return False
    platzhalter = {"Ihr Unternehmen", "", "datenschutz@ihr-unternehmen.de"}
    name  = os.getenv("AILIZA_COMPANY_NAME", "Ihr Unternehmen").strip()
    email = os.getenv("AILIZA_DSB_EMAIL", "datenschutz@ihr-unternehmen.de").strip()
    return name in platzhalter or email in platzhalter


@app.get("/dashboard")
@app.get("/")
def dashboard():
    if _setup_erforderlich():
        return RedirectResponse(url="/setup", status_code=302)
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"info": "AILIZA Backend läuft. Frontend unter apps/frontend/index.html einrichten."})


@app.get("/setup")
def setup_seite():
    seite = FRONTEND_DIR / "setup.html"
    if seite.exists():
        return FileResponse(str(seite))
    return JSONResponse({"fehler": "setup.html nicht gefunden."}, status_code=404)


class SetupDaten(BaseModel):
    firmenname: str = Field(..., min_length=2, max_length=200)
    adresse:    str = Field(..., min_length=4, max_length=300)
    email:      str = Field(..., min_length=5, max_length=200)
    dsb_name:   str = Field("", max_length=200)
    dsb_email:  str = Field("", max_length=200)
    groq_key:   str = Field("", max_length=200)
    tavily_key: str = Field("", max_length=200)


@app.post("/setup/save")
def setup_speichern(daten: SetupDaten):
    """Schreibt Firmendaten und optionale API-Keys in apps/backend/.env."""
    env_pfad = Path(__file__).parent / ".env"

    # Bestehende .env lesen (damit vorhandene Keys erhalten bleiben)
    zeilen: list[str] = []
    if env_pfad.exists():
        zeilen = env_pfad.read_text(encoding="utf-8").splitlines()

    def _setze(key: str, wert: str):
        escaped = wert.replace('"', '\\"')
        for i, z in enumerate(zeilen):
            if z.startswith(f"{key}=") or z.startswith(f"{key} ="):
                zeilen[i] = f'{key}="{escaped}"'
                return
        zeilen.append(f'{key}="{escaped}"')

    _setze("AILIZA_COMPANY_NAME", daten.firmenname)
    _setze("AILIZA_COMPANY_ADDRESS", daten.adresse)
    _setze("AILIZA_CONTACT_EMAIL", daten.email)
    if daten.dsb_name:
        _setze("AILIZA_DSB_NAME", daten.dsb_name)
    if daten.dsb_email:
        _setze("AILIZA_DSB_EMAIL", daten.dsb_email)
    if daten.groq_key and daten.groq_key.startswith("gsk_"):
        _setze("GROQ_API_KEY", daten.groq_key)
    if daten.tavily_key and daten.tavily_key.startswith("tvly_"):
        _setze("TAVILY_API_KEY", daten.tavily_key)

    if _CLOUD:
        # Im Cloud-Betrieb: ENV-Cache aktualisieren, kein .env schreiben
        pass
    else:
        try:
            env_pfad.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
        except OSError as exc:
            raise HTTPException(status_code=500, detail=f"Konnte .env nicht schreiben: {exc}") from exc

    # ENV-Cache im laufenden Prozess sofort aktualisieren
    os.environ["AILIZA_COMPANY_NAME"] = daten.firmenname
    os.environ["AILIZA_CONTACT_EMAIL"] = daten.email
    if daten.dsb_email:
        os.environ["AILIZA_DSB_EMAIL"] = daten.dsb_email

    return {"ok": True, "firmenname": daten.firmenname}


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

    # ── Schritt 1: Policy-Gate — Kill-Switch, Credentials, PII, Datenklassen ─
    bestehendes_mapping = _pii_zwischenspeicher.get(session_id, {})
    policy = enforce_policy(
        body.message,
        action="call_external_model",
        session_id=session_id,
        existing_token_map=bestehendes_mapping,
    )

    if not policy.allowed:
        if policy.is_credential_block:
            write_audit_entry("session.credential_blocked", {
                "session_id": session_id[:8] + "...",
                "content_stored": False,
            })
            return {
                "text": policy.message,
                "warnings": policy.warnings,
                "blocked": True,
                "compliance": {},
            }

        if policy.decision == "require_approval":
            # Anfrage in DB speichern — Admin kann Freigabe erteilen
            sanitized_preview = (policy.sanitized_text or body.message)[:200]
            approval_id = database.create_approval(
                run_id=0,
                task=sanitized_preview,
                reason=f"Policy-Entscheidung: Freigabe nötig | Datenklassen: {policy.policy.get('data_classes', [])}",
            )
            write_audit_entry("session.approval_required", {
                "session_id": session_id[:8] + "...",
                "approval_id": approval_id,
                "data_classes": policy.policy.get("data_classes", []),
            })
            return {
                "text": (
                    f"Diese Anfrage benötigt eine Admin-Freigabe (Nr. {approval_id}). "
                    "Ihr Admin kann sie im Dashboard unter 'Freigaben' genehmigen oder ablehnen."
                ),
                "warnings": policy.warnings,
                "blocked": False,
                "approval_pending": True,
                "approval_id": approval_id,
                "compliance": {"decision": "require_approval"},
            }

        return {
            "text": policy.message,
            "warnings": policy.warnings,
            "blocked": True,
            "compliance": {},
        }

    # ── Schritt 2: Neues Mapping im Zwischenspeicher ablegen ─────────────
    if policy.token_map:
        _pii_zwischenspeicher[session_id] = policy.token_map

    # Tokenisierter Text geht an LLM — Original bleibt im RAM (nie in SQLite)
    llm_text  = policy.sanitized_text or body.message   # Token-Version für LLM + Speicherung
    user_text = body.message                             # Original nur für Anzeige im Frontend

    # ── Schritt 3: Tokenisierte Nachricht speichern (DSGVO Art. 25 — kein PII auf Disk) ──
    session_manager.add_message(session_id, "user", llm_text, warnings=policy.warnings)

    # ── Human Oversight VOR LLM-Aufruf anlegen (EU AI Act Art. 14) ───────
    session_vor_llm = session_manager.get_session(session_id)
    if session_vor_llm and (session_vor_llm.requires_human_oversight or policy.requires_human_oversight):
        database.create_approval(
            run_id=0,
            task=llm_text[:200],   # Tokenisiert — kein PII
            reason="Hochrisiko-Anfrage erkannt (EU AI Act Art. 6, Art. 14)",
        )

    # ── Schritt 4: Routing + Reflection + LLM-Aufruf ─────────────────────
    route = route_query(llm_text)          # Modell, Token-Budget, Temperatur
    system_prompt = session_manager.get_system_prompt(session_id, llm_text)
    if body.eigene_anweisungen:
        pol_anw = enforce_policy(body.eigene_anweisungen, action="call_external_model", session_id=session_id)
        anw_text = pol_anw.sanitized_text or body.eigene_anweisungen
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
            "content": _tokenisiere_kontext(m["content"], policy.token_map),
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
        "pii_typen": policy.pii_found,           # Nur Typ (E-Mail, Telefon...), kein Wert
        "policy_decision": policy.decision,
        "data_classes": policy.policy.get("data_classes", []),
        "pii_tokens_gesamt": len(aktuelles_mapping),
        "human_oversight": session.requires_human_oversight if session else False,
    })

    return {
        "text": antwort_text,                   # Restaurierter Text — PII-Tokens durch Originalwerte ersetzt
        "platzhalter": {k: k for k in aktuelles_mapping},  # nur Token-Keys, keine Originalwerte
        "model": response.model,
        "tokens_used": response.tokens_used,
        "warnings": policy.warnings,
        "blocked": False,
        "compliance": {
            "risk_level": session.risk_level if session else "low",
            "requires_human_oversight": session.requires_human_oversight if session else False,
            "warnings": policy.warnings,
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

    task_lower = body.task.lower()
    _fetch_schemes = ("http://", "https://", "file://", "ftp://", "ftps://")
    action = "run_fetch" if any(task_lower.startswith(s) for s in _fetch_schemes) else "run_search"
    pol = enforce_policy(body.task, action=action)

    if not pol.allowed:
        return {"status": "blocked", "message": pol.message, "results": []}

    run_id = database.create_run(body.task)
    bereinigt = pol.sanitized_text or body.task
    results = [tool_gateway.ausfuehren("abruf" if action == "run_fetch" else "suche", bereinigt)]

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
        "policy_decision": pol.decision,
        "ip": request.client.host if request.client else None,
    })

    return {
        "run_id": run_id,
        "status": "completed" if all_success else "partial",
        "results": [{"tool": r.tool, "success": r.success, "summary": r.summary, "error": r.error} for r in results],
        "warnings": pol.warnings,
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
    _check_admin_token(request)
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
def ai_test(request: Request):
    """Testet Groq-Verbindung mit echtem API-Aufruf. Zeigt genauen Fehlercode."""
    _check_admin_token(request)
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
    if not hmac.compare_digest(token.encode(), _admin_token_env.encode()):
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
