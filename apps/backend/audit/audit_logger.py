# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Audit Logger (DSGVO Art. 30)
Protokolliert alle KI-Aktionen — ohne personenbezogene Klardaten.

Redaction-Garantie: ALLE Stringwerte in details werden vor dem Schreiben
durch Typ-Platzhalter ersetzt. Kein PII, kein Secret gelangt auf Disk.
"""

import hashlib
import hmac
import json
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(os.getenv("AILIZA_AUDIT_DB_PATH", "data/audit.db"))

# Redaction-Patterns für Audit-Log — bewusst eigenständig (keine Imports aus skills/)
# Reihenfolge: spezifischste Patterns zuerst (Secrets vor generischen PII)
_AUDIT_REDACT = [
    ("[Secret]",          r"(?:gsk_|sk-ant-|sk-|tvly-|ghp_|gho_|xoxb-|xoxp-)[A-Za-z0-9_\-\.]{8,}"),
    # JWT: 3 base64url parts separated by dots; signature may be short in tests → {10,}
    ("[Secret]",          r"eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]{10,}"),
    # Bearer token with space (common HTTP header form)
    ("[Secret]",          r"(?i)\bBearer\s+[A-Za-z0-9_\-\.]{10,}"),
    # Assignment forms: password=, secret=, api_key=, bearer=, token=
    ("[Secret]",          r"(?i)(?:password|passwd|secret|api[_\-]?key|private[_\-]?key|token)\s*[=:]\s*\S+"),
    ("[IBAN]",            r"\bDE\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b"),
    ("[E-Mail-Adresse]",  r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9]{2,}\b"),
    ("[Telefonnummer]",   r"(?<!\w)(?:\+49[\s]?|0049[\s]?|0)[1-9][\d\s/\-]{4,14}(?!\d)"),
]


def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            ip_hash TEXT,
            model TEXT,
            tokens INTEGER DEFAULT 0,
            compliance TEXT,
            details TEXT
        )
    """)
    conn.commit()
    return conn


def _ip_hash(ip: str) -> str:
    # HMAC-SHA256 mit Server-Secret + täglich rotierendem Salt
    # Tägliche Rotation: gleiche IP am selben Tag → gleicher Hash,
    # nach Mitternacht UTC → anderer Hash (verhindert langfristige Profilbildung)
    secret = os.getenv("AILIZA_IP_HASH_SECRET", "ailiza-changeme-in-prod").encode()
    daily_salt = str(int(time.time()) // 86400).encode()
    key = secret + b":" + daily_salt
    return hmac.new(key, ip.encode(), hashlib.sha256).hexdigest()[:16]


def redact_string(text: str) -> str:
    """Ersetzt PII und Secrets in einem String durch Typ-Platzhalter."""
    if not text or not isinstance(text, str):
        return text
    result = text
    for placeholder, pattern in _AUDIT_REDACT:
        result = re.sub(pattern, placeholder, result)
    return result


def _deep_redact(value):
    """Rekursive Redaction: str → redact, dict → alle Werte, list → alle Elemente."""
    if isinstance(value, str):
        return redact_string(value)
    if isinstance(value, dict):
        return {k: _deep_redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_redact(item) for item in value]
    return value


def write_audit_entry(action: str, details: dict):
    ip = details.pop("ip", None)
    ip_hash = _ip_hash(ip) if ip else None

    # Alle String-Werte in details redigieren — kein PII auf Disk
    clean_details = _deep_redact(details)

    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO audit_log (timestamp, action, ip_hash, model, tokens, compliance, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            action,
            ip_hash,
            clean_details.get("model"),
            clean_details.get("tokens", 0),
            json.dumps(clean_details.get("compliance"), ensure_ascii=False)
            if clean_details.get("compliance") else None,
            json.dumps(
                {k: v for k, v in clean_details.items() if k not in ("model", "tokens", "compliance")},
                ensure_ascii=False,
            ),
        ))


def get_audit_entries(limit: int = 50) -> list:
    try:
        with _get_conn() as conn:
            rows = conn.execute("""
                SELECT timestamp, action, ip_hash, model, tokens, compliance, details
                FROM audit_log ORDER BY id DESC LIMIT ?
            """, (limit,)).fetchall()
        return [
            {
                "timestamp": r[0], "action": r[1], "ip_hash": r[2],
                "model": r[3], "tokens": r[4],
                "compliance": json.loads(r[5]) if r[5] else None,
                "details": json.loads(r[6]) if r[6] else None,
            }
            for r in rows
        ]
    except Exception:
        return []
