"""
KI-LISA — Compliance Guardrail
Prüft Eingaben auf PII und verbotene Inhalte.
Warnt — blockiert nur bei wirklich verbotenen KI-Praktiken (EU AI Act Art. 5).
"""

import re
from dataclasses import dataclass, field
from typing import Optional


PII_PATTERNS = {
    "E-Mail": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "Telefon": r"\b(\+49|0049|0)[1-9]\d{1,14}\b",
    "IBAN": r"\bDE\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b",
    "Geburtsdatum": r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b",
}

PROHIBITED_PATTERNS = [
    r"sublimin\w+",
    r"soziale[sr]?\s+scoring",
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
    requires_human_oversight: bool = False


def check_input(text: str) -> GuardrailResult:
    result = GuardrailResult()
    t_lower = text.lower()

    # 1. Verbotene Praktiken (BLOCK)
    for pattern in PROHIBITED_PATTERNS:
        if re.search(pattern, t_lower, re.IGNORECASE):
            result.blocked = True
            result.passed = False
            result.block_reason = (
                "Diese Anfrage enthält verbotene KI-Praktiken (EU AI Act Art. 5) "
                "und kann nicht bearbeitet werden."
            )
            return result

    # 2. PII erkennen (WARN, nicht blockieren)
    sanitized = text
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            result.pii_found.append(pii_type)
            result.warnings.append(
                f"Ihre Nachricht enthält {pii_type}-Daten. "
                f"Diese werden nicht gespeichert (DSGVO Art. 5)."
            )
            sanitized = re.sub(pattern, f"[{pii_type.upper()}_ENTFERNT]", sanitized, flags=re.IGNORECASE)

    if result.pii_found:
        result.sanitized_text = sanitized

    # 3. Hochrisiko erkennen (WARN + Human Oversight)
    for kw in HIGH_RISK_KEYWORDS:
        if kw in t_lower:
            result.requires_human_oversight = True
            result.warnings.append(
                "Diese Anfrage betrifft eine Hochrisiko-Entscheidung (EU AI Act Art. 6). "
                "Bitte lassen Sie das Ergebnis von einer Fachkraft prüfen."
            )
            break

    return result


def check_output(text: str) -> list:
    """Prüft ob KI-Kennzeichnung vorhanden ist (EU AI Act Art. 52)."""
    markers = ["ki-lisa", "ki-system", "ki-generiert", "künstliche intelligenz"]
    if not any(m in text.lower() for m in markers):
        return ["KI-Kennzeichnung fehlt — wird automatisch hinzugefügt (EU AI Act Art. 52)."]
    return []
