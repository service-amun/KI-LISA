# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Compliance Guardrail
Prüft Eingaben auf PII und verbotene Inhalte.

PII-Strategie (DSGVO Art. 5 — Privacy by Design):
  1. PII wird durch lesbare Platzhalter ersetzt: [E-Mail-Adresse], [Telefonnummer] ...
  2. Das Platzhalter-Mapping wird im Sitzungs-Zwischenspeicher gehalten (nur RAM)
  3. Die KI erhält nur den tokenisierten Text — keine Klardaten
  4. Nach der Antwort kann der Nutzer jeden Platzhalter per Klick wieder einsetzen
  5. PII verlässt den lokalen Server nie im Klartext

Warnt — blockiert nur bei wirklich verbotenen KI-Praktiken (EU AI Act Art. 5).
"""

import re
from dataclasses import dataclass, field
from typing import Optional


# ── Lesbare Platzhalter-Namen (statt DATEN_1) ────────────────────────────────

PII_PATTERNS = {
    "E-Mail-Adresse":    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "Telefonnummer":     r"\b(?:\+49|0049|0)[1-9][\d/\-]{4,14}\b",
    "Kontoverbindung":   r"\bDE\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b",
    "Geburtsdatum":      r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b",
    "IP-Adresse":        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b",
    "Sozialversicherung":r"\b\d{2}\s?\d{6}\s?[A-Z]\s?\d{3}\b",
}

PROHIBITED_PATTERNS = [
    r"sublimin\w+",
    r"social[\s\-]?scoring|sozialkreditsystem|sozialpunkte|bürgerbewertung|verhaltensscoring",
    r"biometrische\s+(echtzeit|massen)überwachung",
    r"manipulation\s+(durch\s+)?täuschung",
]

HIGH_RISK_KEYWORDS = [
    "kreditentscheidung", "einstellungsentscheidung", "kündigungsentscheidung",
    "schulbewertung", "strafverfolgung", "asylentscheidung",
    "medizinische diagnose", "sicherheitskritisch",
]


@dataclass
class GuardrailResult:
    passed: bool = True
    blocked: bool = False
    block_reason: str = ""
    warnings: list = field(default_factory=list)
    pii_found: list = field(default_factory=list)
    sanitized_text: Optional[str] = None
    # Platzhalter → Originalwert (z.B. "[E-Mail-Adresse]" → "max@firma.de")
    token_map: dict = field(default_factory=dict)
    requires_human_oversight: bool = False


def _make_token(pii_typ: str, zaehler: int) -> str:
    """Erstellt lesbaren Platzhalter — mit Nummer nur wenn mehrere desselben Typs."""
    if zaehler == 1:
        return f"[{pii_typ}]"
    return f"[{pii_typ} {zaehler}]"


def check_input(text: str, existing_token_map: dict = None) -> GuardrailResult:
    """
    Prüft Eingabe und tokenisiert PII mit lesbaren Platzhaltern.

    existing_token_map: Platzhalter-Mapping der laufenden Session —
    bereits bekannte Werte bekommen denselben Platzhalter (Konsistenz).
    """
    result = GuardrailResult()
    t_lower = text.lower()

    # 1. Verbotene Praktiken — sofort blockieren (EU AI Act Art. 5)
    for pattern in PROHIBITED_PATTERNS:
        if re.search(pattern, t_lower, re.IGNORECASE):
            result.blocked = True
            result.passed = False
            result.block_reason = (
                "Diese Anfrage enthält verbotene KI-Praktiken (EU AI Act Art. 5) "
                "und kann nicht bearbeitet werden."
            )
            return result

    # 2. PII durch lesbare Platzhalter ersetzen
    token_map = dict(existing_token_map) if existing_token_map else {}
    reverse_map = {v: k for k, v in token_map.items()}

    # Zähler pro Typ (für [E-Mail-Adresse 2] etc.)
    typ_zaehler: dict[str, int] = {}
    for token in token_map:
        for pii_typ in PII_PATTERNS:
            if token.startswith(f"[{pii_typ}"):
                typ_zaehler[pii_typ] = typ_zaehler.get(pii_typ, 0) + 1

    sanitized = text

    for pii_typ, pattern in PII_PATTERNS.items():
        treffer = re.findall(pattern, text, re.IGNORECASE)
        if not treffer:
            continue

        result.pii_found.append(pii_typ)
        result.warnings.append(
            f"Ihre Nachricht enthält {pii_typ}-Daten. "
            f"Diese werden lokal durch [{pii_typ}] ersetzt und nicht weitergeleitet (DSGVO Art. 5)."
        )

        for wert_roh in treffer:
            wert = wert_roh.strip()
            if not wert:
                continue

            if wert in reverse_map:
                token = reverse_map[wert]
            else:
                typ_zaehler[pii_typ] = typ_zaehler.get(pii_typ, 0) + 1
                token = _make_token(pii_typ, typ_zaehler[pii_typ])
                token_map[token] = wert
                reverse_map[wert] = token

            sanitized = sanitized.replace(wert_roh, token)
            if wert != wert_roh:
                sanitized = sanitized.replace(wert, token)

    if result.pii_found:
        result.sanitized_text = sanitized
        result.token_map = token_map

    # 3. Hochrisiko prüfen
    for kw in HIGH_RISK_KEYWORDS:
        if kw in t_lower:
            result.requires_human_oversight = True
            result.warnings.append(
                "Diese Anfrage betrifft eine Hochrisiko-Entscheidung (EU AI Act Art. 6). "
                "Bitte lassen Sie das Ergebnis von einer Fachkraft prüfen."
            )
            break

    return result


def restore_tokens(text: str, token_map: dict) -> str:
    """Setzt nach dem LLM-Aufruf die Originaldaten wieder ein."""
    if not token_map:
        return text
    restored = text
    for token, original in token_map.items():
        restored = restored.replace(token, original)
    return restored


def check_output(text: str) -> list:
    """Prüft ob KI-Kennzeichnung vorhanden ist (EU AI Act Art. 52)."""
    markers = ["ailiza", "ki-system", "ki-generiert", "künstliche intelligenz"]
    if not any(m in text.lower() for m in markers):
        return ["KI-Kennzeichnung fehlt — wird automatisch hinzugefügt (EU AI Act Art. 52)."]
    return []
