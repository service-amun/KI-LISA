"""
KI-LISA — Law Updater
Wenn EUR-Lex eine Änderung meldet:
  1. Neuen Text von EUR-Lex holen (Volltext, max. 8 000 Zeichen)
  2. LLM extrahiert KMU-relevante Änderungen (400 Token, Temp 0.2)
  3. Zusammenfassung landet im RAG-Gedächtnis (Wichtigkeit 5)
  4. Ab nächster Anfrage beachtet der Agent die neuen Regeln automatisch

Kein manuelles Eingreifen nötig — läuft vollständig im Hintergrund.
"""

import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

from compliance.eurlex_connector import QUELLEN, pruefen
from skills.reflection_skill import merken


_ABRUF_LIMIT_HTML = 60_000   # Bytes vom HTML holen
_TEXT_LIMIT = 5_000          # Zeichen nach HTML-Stripping


def _html_zu_text(html: str) -> str:
    text = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:_TEXT_LIMIT]


def _text_holen(url: str) -> str:
    """Holt den bereinigten Plaintext einer EUR-Lex Seite."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "KI-LISA/1.0 (EU-Compliance-Monitor, non-commercial)"},
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            html = r.read(_ABRUF_LIMIT_HTML).decode("utf-8", errors="replace")
        return _html_zu_text(html)
    except Exception:
        return ""


def _aenderungen_extrahieren(verordnung_name: str, text: str) -> str:
    """
    Lässt das LLM die KMU-relevanten Punkte aus dem Verordnungstext destillieren.
    Nutzt kleines Token-Budget und niedrige Temperatur für präzise Fakten.
    """
    if not text:
        return ""
    try:
        from groq_client import chat
        antwort = chat(
            message=(
                f"Verordnungstext ({verordnung_name}):\n\n{text[:4_000]}\n\n"
                "Fasse in 3–5 präzisen deutschen Sätzen zusammen, welche konkreten "
                "Pflichten und Rechte sich für kleine und mittlere Unternehmen (KMU) "
                "aus diesem Abschnitt ergeben. Keine Einleitung, direkt mit den Pflichten beginnen."
            ),
            system_prompt=(
                "Du bist EU-Rechtsexperte für KMU. Antworte ausschließlich auf Deutsch, "
                "sachlich und ohne Floskeln. Nenne nur konkrete Handlungspflichten."
            ),
            max_tokens=450,
            temperature=0.2,
        )
        if antwort.error:
            return ""
        # EU AI Act Art. 52 Disclaimer aus der Zusammenfassung entfernen
        return re.sub(r"\n*---\n\*KI-generiert.*", "", antwort.text).strip()
    except Exception:
        return ""


def update_pruefen() -> dict:
    """
    Hauptfunktion: Prüft EUR-Lex auf Änderungen, führt bei Treffer ein Update durch.

    Rückgabe:
        {
          "DSGVO":     {"geaendert": bool, "zusammenfassung": str, "gespeichert": bool},
          "EU_AI_Act": {...},
        }
    """
    aenderungen = pruefen()     # HEAD-Requests — sehr schnell
    bericht = {}

    for name, info in aenderungen.items():
        bericht[name] = {"geaendert": info.get("geaendert", False), "zusammenfassung": "", "gespeichert": False}

        if not info.get("geaendert"):
            continue

        # Volltext (begrenzt) laden und KMU-relevant destillieren
        url = QUELLEN.get(name, "")
        text = _text_holen(url) if url else ""
        zusammenfassung = _aenderungen_extrahieren(name, text)

        if not zusammenfassung:
            continue

        # Im RAG-Gedächtnis speichern — Wichtigkeit 5 = höchste Priorität
        datum = datetime.now(timezone.utc).strftime("%d.%m.%Y")
        merken(
            session_id="system",
            inhalt=f"[{name} Aktualisierung {datum}]: {zusammenfassung}",
            stichwörter=[
                name.lower().replace("_", " "),
                "gesetzesänderung", "aktualisierung", "pflicht", "kmu",
                "dsgvo" if "DSGVO" in name else "eu ai act",
            ],
            wichtigkeit=5,
        )

        bericht[name]["zusammenfassung"] = zusammenfassung
        bericht[name]["gespeichert"] = True

    return bericht
