# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Datenbank-Setup
SQLite für Agent-Runs und Genehmigungen.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(os.getenv("AILIZA_DB_PATH", "data/ailiza.db"))


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'running',
            result TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            task TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            decided_at TEXT
        )
    """)
    conn.commit()
    return conn


def create_run(task: str) -> int:
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO agent_runs (task, status, created_at)
            VALUES (?, 'running', ?)
        """, (task, datetime.now(timezone.utc).isoformat()))
        return cur.lastrowid


def finish_run(run_id: int, result: str, status: str = "completed"):
    with get_conn() as conn:
        conn.execute("""
            UPDATE agent_runs SET status = ?, result = ? WHERE id = ?
        """, (status, result, run_id))


def get_runs(limit: int = 20) -> list:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT id, task, status, result, created_at
            FROM agent_runs ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]


def get_run(run_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM agent_runs WHERE id = ?", (run_id,)).fetchone()
    return dict(row) if row else None


def create_approval(run_id: int, task: str, reason: str) -> int:
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO approvals (run_id, task, reason, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
        """, (run_id, task, reason, datetime.now(timezone.utc).isoformat()))
        return cur.lastrowid


def get_approvals(only_pending: bool = True) -> list:
    with get_conn() as conn:
        query = "SELECT * FROM approvals"
        if only_pending:
            query += " WHERE status = 'pending'"
        query += " ORDER BY id DESC"
        rows = conn.execute(query).fetchall()
    return [dict(r) for r in rows]


def decide_approval(approval_id: int, approved: bool):
    status = "approved" if approved else "rejected"
    with get_conn() as conn:
        conn.execute("""
            UPDATE approvals SET status = ?, decided_at = ? WHERE id = ?
        """, (status, datetime.now(timezone.utc).isoformat(), approval_id))
