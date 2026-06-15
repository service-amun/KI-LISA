# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Compliance-Kontext Manager
Erkennt relevante DSGVO- und EU AI Act-Artikel in Nutzeranfragen
und baut daraus einen kompakten System-Prompt.
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Artikel-Datenbank ────────────────────────────────────────────────────────

DSGVO_ARTICLES = {
    "art5": {
        "title": "DSGVO Art. 5 — Datensparsamkeit & Zweckbindung",
        "kurz": "Nur notwendige Daten verarbeiten, klarer Zweck.",
        "keywords": ["daten", "personenbezogen", "speichern", "verarbeiten", "sammeln", "nutzen", "weitergeben"],
    },
    "art6": {
        "title": "DSGVO Art. 6 — Rechtsgrundlage",
        "kurz": "Verarbeitung nur mit Einwilligung oder gesetzlicher Grundlage.",
        "keywords": ["einwilligung", "rechtsgrundlage", "erlaubnis", "zustimmung", "berechtigung"],
    },
    "art13": {
        "title": "DSGVO Art. 13 — Informationspflicht",
        "kurz": "Nutzer muss wissen, was mit seinen Daten passiert.",
        "keywords": ["information", "aufklärung", "hinweis", "datenschutzerklärung"],
    },
    "art17": {
        "title": "DSGVO Art. 17 — Recht auf Löschung",
        "kurz": "Daten auf Wunsch vollständig löschen.",
        "keywords": ["löschen", "löschung", "vergessen", "entfernen", "vernichten"],
    },
    "art20": {
        "title": "DSGVO Art. 20 — Datenportabilität",
        "kurz": "Daten exportieren und übertragen können.",
        "keywords": ["export", "portabilität", "übertragen", "herausgabe", "download"],
    },
    "art25": {
        "title": "DSGVO Art. 25 — Privacy by Design",
        "kurz": "Datenschutz von Anfang an eingebaut.",
        "keywords": ["privacy by design", "datenschutz design", "technische maßnahmen"],
    },
    "art30": {
        "title": "DSGVO Art. 30 — Verzeichnis der Verarbeitungstätigkeiten",
        "kurz": "Alle Datenverarbeitungen müssen dokumentiert sein.",
        "keywords": ["protokoll", "dokumentation", "verzeichnis", "audit", "nachweis"],
    },
    "art35": {
        "title": "DSGVO Art. 35 — Datenschutz-Folgenabschätzung",
        "kurz": "Risiken bei sensibler Datenverarbeitung bewerten.",
        "keywords": ["dsfa", "folgenabschätzung", "risikoabschätzung", "datenschutzfolgen"],
    },
}

EU_AI_ACT_ARTICLES = {
    "art5": {
        "title": "EU AI Act Art. 5 — Verbotene KI-Praktiken",
        "kurz": "Manipulation, Social Scoring und biometrische Massenüberwachung sind verboten.",
        "keywords": ["manipulation", "social scoring", "täuschung", "subliminal", "biometrisch", "massenüberwachung"],
        "block": True,
    },
    "art6": {
        "title": "EU AI Act Art. 6 — Hochrisiko-KI",
        "kurz": "Kredit, Einstellung, Medizin, Strafverfolgung — immer menschliche Kontrolle.",
        "keywords": ["kredit", "kreditentscheidung", "einstellung", "kündigung", "medizin", "diagnose",
                     "strafverfolgung", "asyl", "hochrisiko", "bildungsentscheidung", "schulbewertung"],
        "block": False,
    },
    "art9": {
        "title": "EU AI Act Art. 9 — Risikomanagementsystem",
        "kurz": "Risiken regelmäßig bewerten und dokumentieren.",
        "keywords": ["risiko", "risikoanalyse", "risikobewertung", "risikoklasse"],
    },
    "art13": {
        "title": "EU AI Act Art. 13 — Transparenz",
        "kurz": "KI-System muss verständlich und nachvollziehbar sein.",
        "keywords": ["transparenz", "erklärung", "nachvollziehbar", "verständlich"],
    },
    "art14": {
        "title": "EU AI Act Art. 14 — Menschliche Aufsicht",
        "kurz": "Kritische Entscheidungen brauchen menschliche Kontrolle.",
        "keywords": ["aufsicht", "kontrolle", "human oversight", "menschlich", "genehmigung"],
    },
    "art52": {
        "title": "EU AI Act Art. 52 — Transparenzpflicht (Limited Risk)",
        "kurz": "KI muss sich immer als KI zu erkennen geben.",
        "keywords": ["ki-system", "künstliche intelligenz", "chatbot", "automatisch"],
    },
}

BASE_ARTICLES = {
    "dsgvo": ["art5", "art13"],
    "eu_ai_act": ["art13", "art14", "art52"],
}


# ── Datenstrukturen ──────────────────────────────────────────────────────────

@dataclass
class ComplianceContext:
    dsgvo_articles: list = field(default_factory=list)
    eu_ai_act_articles: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    risk_level: str = "low"
    requires_human_oversight: bool = False
    block_response: bool = False
    block_reason: str = ""


# ── Manager ──────────────────────────────────────────────────────────────────

class ComplianceContextManager:

    # Kompakter Basis-Prompt — weniger Token, gleiche Wirkung
    BASE_SYSTEM_PROMPT = (
        "Du bist AILIZA, EU-konformer KI-Assistent für KMU. "
        "Antworte auf Deutsch, präzise, ohne Fachjargon. "
        "Weise dich als KI aus (EU AI Act Art. 52). "
        "Keine automatisierten Entscheidungen zu Kredit, Einstellung oder Medizin."
    )

    def analyze(self, text: str) -> ComplianceContext:
        t = text.lower()
        ctx = ComplianceContext(
            dsgvo_articles=list(BASE_ARTICLES["dsgvo"]),
            eu_ai_act_articles=list(BASE_ARTICLES["eu_ai_act"]),
        )

        for art_id, art in DSGVO_ARTICLES.items():
            if art_id not in ctx.dsgvo_articles:
                if any(kw in t for kw in art["keywords"]):
                    ctx.dsgvo_articles.append(art_id)

        for art_id, art in EU_AI_ACT_ARTICLES.items():
            if any(kw in t for kw in art["keywords"]):
                if art_id not in ctx.eu_ai_act_articles:
                    ctx.eu_ai_act_articles.append(art_id)

                if art.get("block"):
                    ctx.block_response = True
                    ctx.block_reason = art["title"]

                if art_id == "art6":
                    ctx.requires_human_oversight = True
                    ctx.risk_level = "high"
                    ctx.warnings.append(
                        "Mögliche Hochrisiko-Anwendung — bitte einen Menschen hinzuziehen "
                        "(EU AI Act Art. 6, Art. 14)"
                    )

        return ctx

    def build_system_prompt(self, user_message: str, session_ctx: Optional["ComplianceContext"] = None) -> tuple[str, ComplianceContext]:
        ctx = self.analyze(user_message)
        parts = [self.BASE_SYSTEM_PROMPT]

        # Nur aktuelle Nachricht für Artikel-Selektion — spart Token
        # (Die Gesprächshistorie im Kontext liefert den Rest)
        extra_dsgvo = [a for a in ctx.dsgvo_articles if a not in BASE_ARTICLES["dsgvo"]]
        extra_eu    = [a for a in ctx.eu_ai_act_articles if a not in BASE_ARTICLES["eu_ai_act"]]

        if extra_dsgvo:
            kurz = [DSGVO_ARTICLES[a]["kurz"] for a in extra_dsgvo if a in DSGVO_ARTICLES]
            parts.append("DSGVO: " + " | ".join(kurz))

        if extra_eu:
            kurz = [EU_AI_ACT_ARTICLES[a]["kurz"] for a in extra_eu if a in EU_AI_ACT_ARTICLES]
            parts.append("EU AI Act: " + " | ".join(kurz))

        # Risikoeskalation aus Session beibehalten
        if ctx.requires_human_oversight or (session_ctx and session_ctx.requires_human_oversight):
            parts.append(
                "HOCHRISIKO: Weise ausdrücklich darauf hin, dass eine Fachkraft "
                "die Entscheidung prüfen muss (EU AI Act Art. 14)."
            )

        return "\n\n".join(parts), ctx

    def get_compliance_summary(self, ctx: ComplianceContext) -> dict:
        return {
            "dsgvo": [DSGVO_ARTICLES[a]["title"] for a in ctx.dsgvo_articles if a in DSGVO_ARTICLES],
            "eu_ai_act": [EU_AI_ACT_ARTICLES[a]["title"] for a in ctx.eu_ai_act_articles if a in EU_AI_ACT_ARTICLES],
            "risk_level": ctx.risk_level,
            "warnings": ctx.warnings,
            "requires_human_oversight": ctx.requires_human_oversight,
        }
