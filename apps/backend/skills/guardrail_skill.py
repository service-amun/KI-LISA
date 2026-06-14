"""
KI-LISA — Compliance Guardrail
Prüft Eingaben auf PII und verbotene Inhalte.

PII-Strategie (DSGVO Art. 5 — Privacy by Design):
  1. PII wird durch nummerierte Tokens ersetzt: [DATEN_1], [DATEN_2], ...
  2. Das Token-Mapping wird im Sitzungs-Zwischenspeicher gehalten (nur Arbeitsspeicher)
  3. Die KI erhält nur tokenisierten Text — keine Klardaten
  4. Nach der Antwort werden Tokens durch die Originaldaten ersetzt
  5. PII verlässt den lokalen Server nie im Klartext

Warnt — blockiert nur bei wirklich verbotenen KI-Praktiken (EU AI Act Art. 5).
"""

import re
from dataclasses import dataclass, field
from typing import Optional


PII_PATTERNS = {
    "E-Mail":       r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "Telefon":      r"\b(?:\+49|0049|0)[1-9][\d\s/\-]{4,14}\b",
    "IBAN":         r"\bDE\d{2}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{4}[\s]?\d{2}\b",
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
    # Tokenisierter Text für den LLM-Aufruf
    sanitized_text: Optional[str] = None
    # Mapping Token → Originalwert (nur im Arbeitsspeicher)
    token_map: dict = field(default_factory=dict)
    requires_human_oversight: bool = False


def check_input(text: str, existing_token_map: dict = None) -> GuardrailResult:
    """
    Prüft Eingabe und tokenisiert PII.

    existing_token_map: Token-Mapping der laufenden Session —
    bereits bekannte PII bekommt denselben Token (Konsistenz über Nachrichten).
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

    # 2. PII durch Tokens ersetzen (kein Klartext an LLM)
    # Bestehendes Mapping der Session übernehmen
    token_map = dict(existing_token_map) if existing_token_map else {}
    # Umgekehrtes Mapping: Originalwert → Token (für schnelle Suche)
    reverse_map = {v: k for k, v in token_map.items()}

    sanitized = text
    zaehler = len(token_map) + 1

    for pii_typ, pattern in PII_PATTERNS.items():
        treffer = re.findall(pattern, text, re.IGNORECASE)
        if not treffer:
            continue

        result.pii_found.append(pii_typ)
        result.warnings.append(
            f"Ihre Nachricht enthält {pii_typ}-Daten. "
            f"Diese werden nur lokal gespeichert und nicht weitergeleitet (DSGVO Art. 5)."
        )

        for wert_roh in treffer:
            wert = wert_roh.strip()      # Leerzeichen am Rand entfernen
            if not wert:
                continue
            if wert in reverse_map:
                # Bereits bekannt — gleichen Token wiederverwenden
                token = reverse_map[wert]
            else:
                # Neuer Wert → neuen Token anlegen
                token = f"[DATEN_{zaehler}]"
                token_map[token] = wert
                reverse_map[wert] = token
                zaehler += 1

            # Rohen Treffer (inkl. Leerzeichen) ersetzen damit kein Rest bleibt
            sanitized = sanitized.replace(wert_roh, token)
            # Auch gestrippte Variante ersetzen (falls Pattern kein trailing space hat)
            if wert != wert_roh:
                sanitized = sanitized.replace(wert, token)

    if result.pii_found:
        result.sanitized_text = sanitized
        result.token_map = token_map

    # 3. Hochrisiko prüfen (WARN + Human Oversight)
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
    """
    Setzt nach der LLM-Antwort die Originaldaten wieder ein.
    Die KI hat nur Tokens gesehen — der Nutzer sieht die echten Werte.
    """
    if not token_map:
        return text
    restored = text
    for token, original in token_map.items():
        restored = restored.replace(token, original)
    return restored


def check_output(text: str) -> list:
    """Prüft ob KI-Kennzeichnung vorhanden ist (EU AI Act Art. 52)."""
    markers = ["ki-lisa", "ki-system", "ki-generiert", "künstliche intelligenz"]
    if not any(m in text.lower() for m in markers):
        return ["KI-Kennzeichnung fehlt — wird automatisch hinzugefügt (EU AI Act Art. 52)."]
    return []
