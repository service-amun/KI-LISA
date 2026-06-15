# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Audit Logger (DSGVO Art. 30)
Protokolliert alle KI-Aktionen — ohne personenbezogene Klardaten.
"""

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(os.getenv("AILIZA_AUDIT_DB_PATH", "data/audit.db"))


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


def write_audit_entry(action: str, details: dict):
    ip = details.pop("ip", None)
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:12] if ip else None

    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO audit_log (timestamp, action, ip_hash, model, tokens, compliance, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            action,
            ip_hash,
            details.get("model"),
            details.get("tokens", 0),
            json.dumps(details.get("compliance"), ensure_ascii=False) if details.get("compliance") else None,
            json.dumps({k: v for k, v in details.items() if k not in ("model", "tokens", "compliance")},
                       ensure_ascii=False),
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
