"""
KI-LISA — Reflection Skill (RAG Memory)
Merkt sich wichtige Fakten aus Gesprächen und ruft sie bei neuen Anfragen ab.
Kein Embedding nötig — keyword-basiertes SQLite-Retrieval.
"""

import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DB_PATH = Path("data/reflection.db")

# Stoppwörter die beim Indexieren ignoriert werden
_STOP = {
    "dass", "wird", "sind", "haben", "kann", "bitte", "auch", "eine", "dieser",
    "beim", "nach", "über", "mehr", "noch", "dann", "sehr", "aber", "oder",
    "wenn", "alle", "kein", "keine", "nicht", "dies", "sich", "para", "bitte",
}

# Max. Einträge im Speicher (älteste werden gelöscht wenn überschritten)
MAX_EINTRAEGE = 1000


@dataclass
class Erinnerung:
    id: int
    session_id: str
    inhalt: str
    stichwörter: str
    wichtigkeit: int   # 1–5 (5 = sehr wichtig)
    erstellt: str


def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute("""
        CREATE TABLE IF NOT EXISTS erinnerungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            inhalt TEXT NOT NULL,
            stichwörter TEXT DEFAULT '',
            wichtigkeit INTEGER DEFAULT 3,
            erstellt TEXT NOT NULL
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_wichtigkeit ON erinnerungen (wichtigkeit DESC, erstellt DESC)")
    c.commit()
    return c


def merken(session_id: str, inhalt: str, stichwörter: list = None, wichtigkeit: int = 3):
    """Speichert eine wichtige Information aus der aktuellen Session."""
    with _conn() as c:
        c.execute(
            "INSERT INTO erinnerungen (session_id, inhalt, stichwörter, wichtigkeit, erstellt) VALUES (?,?,?,?,?)",
            (
                session_id,
                inhalt[:500],
                ",".join(stichwörter or []),
                min(5, max(1, wichtigkeit)),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        # Speicher begrenzen: Überschuss (älteste) löschen
        c.execute(
            "DELETE FROM erinnerungen WHERE id IN "
            "(SELECT id FROM erinnerungen ORDER BY wichtigkeit ASC, erstellt ASC LIMIT MAX(0, (SELECT COUNT(*) FROM erinnerungen) - ?))",
            (MAX_EINTRAEGE,),
        )


def erinnern(anfrage: str, limit: int = 3) -> list[Erinnerung]:
    """Holt relevante Erinnerungen via Keyword-Matching."""
    woerter = [w.lower() for w in re.findall(r'\b\w{4,}\b', anfrage) if w.lower() not in _STOP]
    if not woerter:
        return []

    with _conn() as c:
        # Neueste 200 nach Wichtigkeit
        rows = c.execute(
            "SELECT id, session_id, inhalt, stichwörter, wichtigkeit, erstellt "
            "FROM erinnerungen ORDER BY wichtigkeit DESC, erstellt DESC LIMIT 200"
        ).fetchall()

    treffer = []
    for row in rows:
        haystack = (row[2] + " " + row[3]).lower()
        punkte = sum(1 for w in woerter if w in haystack)
        if punkte > 0:
            treffer.append((punkte * row[4], row))   # punkte × wichtigkeit

    treffer.sort(reverse=True)
    return [
        Erinnerung(id=r[0], session_id=r[1], inhalt=r[2], stichwörter=r[3],
                   wichtigkeit=r[4], erstellt=r[5])
        for _, r in treffer[:limit]
    ]


def kontext_aufbauen(anfrage: str) -> str:
    """
    Gibt relevante Erinnerungen als kompakten System-Kontext zurück.
    Leerer String wenn nichts Passendes gefunden.
    """
    erinnerungen = erinnern(anfrage, limit=3)
    if not erinnerungen:
        return ""
    teile = [f"- {e.inhalt}" for e in erinnerungen]
    return "Aus früheren Gesprächen:\n" + "\n".join(teile)


def auto_extrahieren(text: str, session_id: str):
    """
    Extrahiert automatisch merkenswerte Sätze aus einer KI-Antwort.
    Nur Sätze mit konkreten Fakten (Zahlen, Daten, Euro-Beträge, Fristen).
    """
    saetze = re.split(r'(?<=[.!?])\s+', text.replace('\n', ' '))
    for satz in saetze:
        s = satz.strip()
        if len(s) < 25 or len(s) > 350:
            continue
        # Konkrete Fakten erkennen
        hat_datum   = bool(re.search(r'\d{1,2}[.]\d{1,2}[.]\d{2,4}|\b20\d\d\b', s))
        hat_euro    = bool(re.search(r'€|\bEuro\b|\bProzent\b|\b%\b', s, re.IGNORECASE))
        hat_frist   = bool(re.search(r'\bFrist\b|\bDeadline\b|\bPflicht\b|\bmuss\b', s, re.IGNORECASE))
        hat_artikel = bool(re.search(r'\bArt\.\s*\d+|\bArtikel\s*\d+|\bAbs\.\s*\d+', s))

        if not (hat_datum or hat_euro or hat_frist or hat_artikel):
            continue

        wichtigkeit = 3
        if hat_datum:   wichtigkeit = max(wichtigkeit, 4)
        if hat_euro:    wichtigkeit = max(wichtigkeit, 4)
        if hat_artikel: wichtigkeit = max(wichtigkeit, 4)
        if hat_frist:   wichtigkeit = max(wichtigkeit, 5)

        sw = [w for w in re.findall(r'\b\w{4,}\b', s.lower()) if w not in _STOP][:10]
        merken(session_id, s, sw, wichtigkeit)
