# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — EUR-Lex Delta-Checker
Prüft via HEAD-Request ob relevante EU-Verordnungen aktualisiert wurden.
Kein Volltext-Download — nur Last-Modified Header.
"""

import json
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path("data/eurlex_checks.db")

# Zu überwachende EU-Verordnungen (stabile EUR-Lex HTML-URLs)
QUELLEN = {
    "DSGVO": "https://eur-lex.europa.eu/legal-content/DE/TXT/HTML/?uri=CELEX:32016R0679",
    "EU_AI_Act": "https://eur-lex.europa.eu/legal-content/DE/TXT/HTML/?uri=CELEX:32024R1689",
}


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            quelle TEXT PRIMARY KEY,
            letzter_check TEXT,
            last_modified TEXT,
            geaendert INTEGER DEFAULT 0
        )
    """)
    c.commit()
    return c


def _head(url: str) -> str:
    """Holt nur den Last-Modified-Header ohne Volltext zu laden."""
    try:
        req = urllib.request.Request(url, method="HEAD",
            headers={"User-Agent": "AILIZA/1.0 (EU AI Act compliance check)"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.headers.get("Last-Modified", "")
    except Exception:
        return ""


def pruefen() -> dict:
    """
    Prüft alle Quellen und speichert das Ergebnis.
    Gibt zurück: {quelle: {geaendert, letzter_check, last_modified}}
    """
    jetzt = datetime.now(timezone.utc).isoformat()
    ergebnis = {}

    with _conn() as c:
        for name, url in QUELLEN.items():
            neu = _head(url)
            row = c.execute("SELECT last_modified FROM checks WHERE quelle = ?", (name,)).fetchone()
            alt = row[0] if row else None
            geaendert = bool(neu and alt and neu != alt)

            c.execute("""
                INSERT OR REPLACE INTO checks (quelle, letzter_check, last_modified, geaendert)
                VALUES (?, ?, ?, ?)
            """, (name, jetzt, neu or alt or "", int(geaendert)))

            ergebnis[name] = {
                "geaendert": geaendert,
                "letzter_check": jetzt,
                "last_modified": neu or alt or "unbekannt",
            }

    return ergebnis


def status() -> dict:
    """Letzter gespeicherter Prüfstatus — ohne neuen Netzwerkaufruf."""
    with _conn() as c:
        rows = c.execute("SELECT quelle, letzter_check, last_modified, geaendert FROM checks").fetchall()
    if not rows:
        return {"hinweis": "Noch kein Check durchgeführt. POST /compliance/check aufrufen."}
    return {
        r[0]: {"letzter_check": r[1], "last_modified": r[2], "geaendert": bool(r[3])}
        for r in rows
    }
