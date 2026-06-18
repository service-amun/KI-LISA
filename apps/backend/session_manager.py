# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Chat Session Manager
Jeder Chat hat seinen eigenen isolierten Compliance-Kontext.
Sessions beeinflussen sich gegenseitig nicht.
"""

import json
import os
import secrets
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from compliance_context import ComplianceContextManager, ComplianceContext


_BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = Path(os.getenv("AILIZA_SESSION_DB_PATH", str(_BASE_DIR / "data" / "chat_sessions.db")))
_mgr = ComplianceContextManager()


@dataclass
class ChatMessage:
    role: str
    content: str
    timestamp: str = ""
    warnings: list = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ChatSession:
    session_id: str
    title: str = "Neuer Chat"
    created_at: str = ""
    updated_at: str = ""
    messages: list = field(default_factory=list)
    active_dsgvo_articles: list = field(default_factory=list)
    active_eu_ai_act_articles: list = field(default_factory=list)
    accumulated_warnings: list = field(default_factory=list)
    risk_level: str = "low"
    requires_human_oversight: bool = False

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now


def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            title TEXT,
            created_at TEXT,
            updated_at TEXT,
            messages TEXT,
            compliance_state TEXT
        )
    """)
    conn.commit()
    return conn


def _save(session: ChatSession):
    compliance_state = {
        "active_dsgvo_articles": session.active_dsgvo_articles,
        "active_eu_ai_act_articles": session.active_eu_ai_act_articles,
        "accumulated_warnings": session.accumulated_warnings,
        "risk_level": session.risk_level,
        "requires_human_oversight": session.requires_human_oversight,
    }
    with _get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session.session_id, session.title,
            session.created_at, session.updated_at,
            json.dumps([asdict(m) for m in session.messages], ensure_ascii=False),
            json.dumps(compliance_state, ensure_ascii=False),
        ))


def create_session(title: str = "Neuer Chat") -> ChatSession:
    sid = secrets.token_hex(16)
    session = ChatSession(session_id=sid, title=title)
    _save(session)
    return session


def get_session(session_id: str) -> Optional[ChatSession]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
    if not row:
        return None

    state = json.loads(row[5])
    messages = [ChatMessage(**m) for m in json.loads(row[4])]
    return ChatSession(
        session_id=row[0], title=row[1],
        created_at=row[2], updated_at=row[3],
        messages=messages, **state,
    )


def list_sessions(limit: int = 30) -> list:
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT session_id, title, created_at, updated_at
            FROM sessions ORDER BY updated_at DESC LIMIT ?
        """, (limit,)).fetchall()
    return [{"session_id": r[0], "title": r[1], "created_at": r[2], "updated_at": r[3]} for r in rows]


def add_message(session_id: str, role: str, content: str, warnings: list = None) -> tuple[ChatMessage, ComplianceContext]:
    session = get_session(session_id)
    if not session:
        raise ValueError(f"Session nicht gefunden: {session_id}")

    # Nur Nutzer-Nachrichten lösen Risiko-Einstufung aus — die KI-Antwort
    # erklärt oft selbst die Einschränkungen (z.B. "keine Kreditentscheidungen")
    # und würde sonst ihre eigene Sicherheitswarnung als Hochrisiko-Anfrage werten.
    ctx = ComplianceContext()
    if role == "user":
        _, ctx = _mgr.build_system_prompt(content)

        for art in ctx.dsgvo_articles:
            if art not in session.active_dsgvo_articles:
                session.active_dsgvo_articles.append(art)
        for art in ctx.eu_ai_act_articles:
            if art not in session.active_eu_ai_act_articles:
                session.active_eu_ai_act_articles.append(art)
        for w in (ctx.warnings + (warnings or [])):
            if w not in session.accumulated_warnings:
                session.accumulated_warnings.append(w)

        if ctx.risk_level == "high":
            session.risk_level = "high"
        if ctx.requires_human_oversight:
            session.requires_human_oversight = True

    msg = ChatMessage(role=role, content=content, warnings=warnings or [])
    session.messages.append(msg)
    session.updated_at = datetime.now(timezone.utc).isoformat()

    if role == "user" and session.title == "Neuer Chat" and len(session.messages) == 1:
        session.title = content[:50] + ("..." if len(content) > 50 else "")

    _save(session)
    return msg, ctx


def get_system_prompt(session_id: str, current_message: str) -> str:
    session = get_session(session_id)
    session_ctx = None

    if session:
        from compliance_context import ComplianceContext
        session_ctx = ComplianceContext(
            dsgvo_articles=session.active_dsgvo_articles,
            eu_ai_act_articles=session.active_eu_ai_act_articles,
            warnings=session.accumulated_warnings,
            risk_level=session.risk_level,
            requires_human_oversight=session.requires_human_oversight,
        )

    prompt, _ = _mgr.build_system_prompt(current_message, session_ctx)
    return prompt


def get_context_messages(session_id: str, max_messages: int = 10) -> list:
    session = get_session(session_id)
    if not session:
        return []
    return [{"role": m.role, "content": m.content} for m in session.messages[-max_messages:]]


def delete_session(session_id: str) -> bool:
    """DSGVO Art. 17 — vollständige Löschung."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    return True


def cleanup_alte_sessions() -> int:
    """DSGVO Art. 5(1)(e) — Datenspeicherbegrenzung: Sessions älter als Aufbewahrungsfrist löschen."""
    tage = int(os.getenv("AILIZA_DATA_RETENTION_DAYS", "90"))
    grenze = (datetime.now(timezone.utc) - timedelta(days=tage)).isoformat()
    with _get_conn() as conn:
        result = conn.execute(
            "DELETE FROM sessions WHERE updated_at < ?", (grenze,)
        )
    return result.rowcount
