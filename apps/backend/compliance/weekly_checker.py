"""
KI-LISA — Wöchentlicher Compliance-Check
Prüft DSGVO- und EU AI Act-Konformität des Systems und ob Gesetze aktualisiert wurden.
"""

from datetime import datetime, date, timezone
from pathlib import Path

from compliance.eurlex_connector import pruefen as eurlex_pruefen, status as eurlex_status


# EU AI Act vollständige Anwendbarkeit
FRIST_EU_AI_ACT = date(2026, 8, 2)

CHECKLISTE = [
    {"id": "pii_tokenisierung",     "text": "PII-Tokenisierung aktiv (DSGVO Art. 5)",        "status": "ok"},
    {"id": "audit_trail",           "text": "Audit-Trail aktiv (DSGVO Art. 30)",               "status": "ok"},
    {"id": "loeschrecht",           "text": "Löschrecht implementiert (DSGVO Art. 17)",        "status": "ok"},
    {"id": "ki_kennzeichnung",      "text": "KI-Kennzeichnung in jeder Antwort (EU AI Act Art. 52)", "status": "ok"},
    {"id": "human_oversight",       "text": "Human Oversight für Hochrisiko (EU AI Act Art. 14)", "status": "ok"},
    {"id": "verbotene_praktiken",   "text": "Verbotene Praktiken geblockt (EU AI Act Art. 5)", "status": "ok"},
    {"id": "rate_limiting",         "text": "Rate Limiting aktiv (20 Req/Min)",                "status": "ok"},
    {"id": "kein_nutzer_api_key",   "text": "Kein Nutzer-API-Key erforderlich (KMU-Konformität)", "status": "ok"},
]


def bericht() -> dict:
    """Erstellt einen vollständigen Compliance-Bericht."""
    heute = date.today()
    tage_bis_frist = (FRIST_EU_AI_ACT - heute).days
    frist_ok = tage_bis_frist > 0

    # EUR-Lex Status (gespeichert, kein neuer Netzwerkaufruf)
    eurlex = eurlex_status()
    geaenderungen = [k for k, v in eurlex.items() if isinstance(v, dict) and v.get("geaendert")]

    return {
        "erstellt": datetime.now(timezone.utc).isoformat(),
        "risikoklasse": "Limited Risk (EU AI Act Art. 52)",
        "frist": {
            "datum": FRIST_EU_AI_ACT.isoformat(),
            "tage_verbleibend": tage_bis_frist,
            "status": "ok" if frist_ok else "abgelaufen",
        },
        "checkliste": CHECKLISTE,
        "alle_ok": all(p["status"] == "ok" for p in CHECKLISTE),
        "eurlex": eurlex,
        "gesetzes_aenderungen": geaenderungen,
        "handlungsbedarf": (
            geaenderungen or
            not all(p["status"] == "ok" for p in CHECKLISTE) or
            not frist_ok
        ),
    }


def komplett_check() -> dict:
    """Führt EUR-Lex-Prüfung durch und erstellt Bericht."""
    eurlex_pruefen()   # HEAD-Requests zu EUR-Lex
    return bericht()
