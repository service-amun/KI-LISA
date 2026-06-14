"""
KI-LISA — FastAPI Backend
EU-konformer KI-Assistent für KMU.
"""

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
from routers.approvals import router as approvals_router

# ── PII-Zwischenspeicher (nur Arbeitsspeicher, nie auf Disk) ─────────────────
# session_id → {token: originalwert}
# Wird gelöscht wenn Session gelöscht wird oder Server neu startet.
_pii_zwischenspeicher: dict[str, dict] = {}

# ── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="KI-LISA",
    description="EU-konformer KI-Assistent für KMU — DSGVO + EU AI Act konform",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(approvals_router)

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


class NewSessionRequest(BaseModel):
    title: str = Field(default="Neuer Chat", max_length=100)


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


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/dashboard")
@app.get("/")
def dashboard():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"info": "KI-LISA Backend läuft. Frontend unter apps/frontend/index.html einrichten."})


# ── Sessions (Chat mit Compliance-Kontext) ─────────────────────────────────────

@app.get("/sessions")
def list_sessions():
    return session_manager.list_sessions()


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

    # Tokenisierter Text geht an LLM — Originaltext wird lokal gespeichert
    llm_text  = guard.sanitized_text or body.message   # Token-Version für LLM
    user_text = body.message                            # Original für Anzeige/Speicherung

    # ── Schritt 3: Originalnachricht (mit PII) lokal speichern ───────────
    session_manager.add_message(session_id, "user", user_text, warnings=guard.warnings)

    # ── Schritt 4: Routing + LLM-Aufruf ──────────────────────────────────
    route = route_query(llm_text)          # Modell, Token-Budget, Temperatur
    system_prompt = session_manager.get_system_prompt(session_id, llm_text)

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

    # ── Schritt 5: Tokens in Antwort durch Originaldaten ersetzen ────────
    aktuelles_mapping = _pii_zwischenspeicher.get(session_id, {})
    antwort_text = restore_tokens(response.text, aktuelles_mapping)

    # ── Schritt 6: Wiederhergestellte Antwort speichern ──────────────────
    session_manager.add_message(session_id, "assistant", antwort_text)

    # Approval anlegen wenn Human Oversight nötig
    session = session_manager.get_session(session_id)
    if session and session.requires_human_oversight:
        database.create_approval(
            run_id=0,
            task=user_text[:200],
            reason="Hochrisiko-Anfrage erkannt (EU AI Act Art. 6, Art. 14)",
        )

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
        "text": response.text,                  # Mit Platzhaltern — Frontend zeigt klickbare Chips
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
        "disclaimer": "KI-generiert — KI-LISA (EU AI Act Art. 52)",
    }


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """DSGVO Art. 17 — Recht auf Löschung."""
    session_manager.delete_session(session_id)
    # PII-Zwischenspeicher für diese Session ebenfalls löschen
    _pii_zwischenspeicher.pop(session_id, None)
    write_audit_entry("session.deleted", {"session_id": session_id[:8] + "..."})
    return {"status": "gelöscht", "hinweis": "Alle Daten dieser Session wurden entfernt (DSGVO Art. 17)."}


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
    results = agent_runtime.run_task(body.task)

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
    result = agent_runtime.run_search(body.query)
    return {"success": result.success, "summary": result.summary, "error": result.error}


@app.post("/tools/fetch")
def tool_fetch(body: FetchRequest, request: Request):
    check_rate_limit(request)
    result = agent_runtime.run_fetch(body.url)
    return {"success": result.success, "summary": result.summary, "error": result.error}


# ── Audit-Log ─────────────────────────────────────────────────────────────────

@app.get("/audit-logs")
def audit_logs(limit: int = 50):
    return get_audit_entries(limit=min(limit, 200))


# ── KI-Status ─────────────────────────────────────────────────────────────────

@app.get("/ai/status")
def ai_status():
    return {
        "konfiguriert": groq_client.is_configured(),
        "anbieter": "Groq",
        "modelle": list(groq_client.MODELS.keys()),
        "compliance": "EU AI Act Art. 52 — KI-System aktiv",
        "risikoklasse": "Limited Risk",
    }
