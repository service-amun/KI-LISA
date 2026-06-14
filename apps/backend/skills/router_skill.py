"""
KI-LISA — Router Skill
Wählt Modell, Token-Budget und Kontextgröße — ohne LLM-Aufruf.
"""

import re
from dataclasses import dataclass


@dataclass
class RouteConfig:
    modell: str
    max_tokens: int
    temperature: float
    kontext_nachrichten: int   # wie viele Chat-Nachrichten ans LLM schicken


# Compliance/Rechtliches → großes Modell, exakt, viel Raum
_COMPLIANCE = [
    "dsgvo", "datenschutz", "eu ai act", "compliance", "datenschutzgrundverordnung",
    "rechtsgrundlage", "einwilligung", "personenbezogen", "auftragsdatenverarbeitung",
    "datenschutzbeauftragter", "haftung", "bußgeld", "rechtlich", "gesetzlich",
    "kreditentscheidung", "einstellungsentscheidung", "kündigung", "hochrisiko",
    "strafverfolgung", "medizinische diagnose", "art.", "artikel §", "paragraph",
    "vertragsrecht", "arbeitsrecht", "steuerrecht", "impressumspflicht",
]

# Kreatives Schreiben → großes Modell, kreativer
_KREATIV = [
    "schreib", "verfasse", "erstelle einen", "formulier", "übersetze", "briefe",
    "e-mail", "anschreiben", "einladung", "pressemitteilung", "stellenausschreibung",
]

# Kurze Grüße / Bestätigungen → 8B, minimal
_SIMPLE_RE = re.compile(
    r"^(hallo|hi|hey|guten\s+\w+|danke|danke\s+schön|vielen\s+dank|ok|okay|alles\s+klar|ja|nein|bitte)"
    r"[\s!?.,]*$",
    re.IGNORECASE,
)


def classify(text: str) -> RouteConfig:
    t = text.lower().strip()
    woerter = len(t.split())

    # 1. Kurze Grüße → 8B, schnell, wenig Tokens
    if woerter <= 5 or _SIMPLE_RE.match(t):
        return RouteConfig(
            modell="llama3-8b-8192",
            max_tokens=256,
            temperature=0.6,
            kontext_nachrichten=4,
        )

    # 2. Compliance / Rechtliches → 70B, präzise, viel Raum
    if any(kw in t for kw in _COMPLIANCE):
        return RouteConfig(
            modell="llama3-70b-8192",
            max_tokens=2048,
            temperature=0.3,
            kontext_nachrichten=8,
        )

    # 3. Kreatives Schreiben → 70B, kreativer
    if any(kw in t for kw in _KREATIV):
        return RouteConfig(
            modell="llama3-70b-8192",
            max_tokens=1024,
            temperature=0.72,
            kontext_nachrichten=6,
        )

    # 4. Alles andere → 70B, ausgewogen
    return RouteConfig(
        modell="llama3-70b-8192",
        max_tokens=768,
        temperature=0.55,
        kontext_nachrichten=6,
    )
