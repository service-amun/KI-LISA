# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Groq LLM Client
Zentraler API-Key im Backend — kein Nutzer-Key nötig.
"""

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

TAVILY_URL = "https://api.tavily.com/search"

# Stichworte die eine aktuelle Web-Suche nötig machen
_SUCHE_MUSTER = re.compile(
    r"\b(aktuell|heute|news|neuigkeit|2025|2026|stand\s+\d{4}|"
    r"aktuelle\s+(gesetz|recht|regel|vorschrift|nachrichten?)|"
    r"was\s+(ist|sind|gilt|steht)\s+(gerade|aktuell|jetzt)|"
    r"social.?media|instagram|tiktok|linkedin|twitter|facebook)\b",
    re.IGNORECASE,
)


def _web_suche(query: str) -> str:
    """Sucht mit Tavily und gibt kompakten Text zurück. Leer wenn kein Key."""
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return ""
    try:
        payload = json.dumps({
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": 3,
            "include_answer": True,
        }).encode()
        req = urllib.request.Request(
            TAVILY_URL, data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (AILIZA-Backend)",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
        teile = []
        if data.get("answer"):
            teile.append(f"Aktuelle Info: {data['answer']}")
        for res in data.get("results", [])[:3]:
            if res.get("content"):
                teile.append(f"- {res['content'][:300]}")
        return "\n".join(teile)[:1500]
    except Exception as e:
        print(f"[AILIZA] Tavily-Suche fehlgeschlagen: {e}", flush=True)
        return ""


@dataclass
class LLMResponse:
    text: str
    model: str
    tokens_used: int = 0
    error: Optional[str] = None


MODELS = {
    "standard":  "llama-3.3-70b-versatile",
    "schnell":   "llama-3.1-8b-instant",
    "alternativ":"gemma2-9b-it",
}

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

AI_DISCLAIMER = "\n\n---\n*KI-generiert — AILIZA (EU AI Act Art. 52). Bitte prüfen Sie wichtige Entscheidungen.*"

# Kontext-Nachrichten auf max. 700 Zeichen kürzen — spart Token, behält Kern
_MAX_CTX_CHARS = 700


def is_configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def _trim_context(messages: list) -> list:
    """Kürzt lange Kontext-Nachrichten, damit keine unnötigen Token verschwendet werden."""
    result = []
    for m in messages:
        content = m["content"]
        if len(content) > _MAX_CTX_CHARS:
            content = content[:_MAX_CTX_CHARS] + "…"
        result.append({"role": m["role"], "content": content})
    return result


def chat(
    message: str,
    system_prompt: str,
    context: list = None,
    model: str = None,
    max_tokens: int = 768,
    temperature: float = 0.55,
) -> LLMResponse:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return LLMResponse(
            text=(
                "AILIZA ist noch nicht vollständig eingerichtet. "
                "Bitte wenden Sie sich an Ihren Administrator."
                + AI_DISCLAIMER
            ),
            model="none",
            error="kein_api_key",
        )

    chosen_model = model or MODELS["standard"]

    # Echtzeit-Websuche wenn Frage aktuelle Informationen braucht
    erweiterter_prompt = system_prompt
    if _SUCHE_MUSTER.search(message):
        suchergebnis = _web_suche(message)
        if suchergebnis:
            erweiterter_prompt += (
                f"\n\nAKTUELLE WEB-SUCHERGEBNISSE (Stand heute):\n{suchergebnis}\n"
                "Nutze diese Informationen für deine Antwort."
            )

    messages = [{"role": "system", "content": erweiterter_prompt}]
    for m in _trim_context(context or []):
        messages.append(m)
    messages.append({"role": "user", "content": message})

    payload = json.dumps({
        "model": chosen_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()

    req = urllib.request.Request(
        GROQ_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            # Ohne User-Agent blockiert Cloudflare den Standard-Python-Header (Fehler 1010)
            "User-Agent": "Mozilla/5.0 (AILIZA-Backend)",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)

        if "ailiza" not in text.lower() and "ki-system" not in text.lower():
            text += AI_DISCLAIMER

        return LLMResponse(text=text, model=chosen_model, tokens_used=tokens)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        error_detail = f"HTTP {e.code}: {body[:300]}"
        print(f"[AILIZA] Groq API Fehler — {error_detail}", flush=True)
        return LLMResponse(
            text="Es gab ein Problem beim Abrufen der KI-Antwort. Bitte versuchen Sie es erneut." + AI_DISCLAIMER,
            model=chosen_model,
            error=error_detail,
        )
    except Exception as e:
        print(f"[AILIZA] Groq Verbindungsfehler — {e}", flush=True)
        return LLMResponse(
            text="Die KI-Antwort konnte nicht geladen werden. Bitte versuchen Sie es erneut." + AI_DISCLAIMER,
            model=chosen_model,
            error=str(e),
        )
