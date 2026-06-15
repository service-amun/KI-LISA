# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Groq LLM Client
Zentraler API-Key im Backend — kein Nutzer-Key nötig.
"""

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    text: str
    model: str
    tokens_used: int = 0
    error: Optional[str] = None


MODELS = {
    "standard":  "llama3-70b-8192",
    "schnell":   "llama3-8b-8192",
    "alternativ":"mixtral-8x7b-32768",
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

    messages = [{"role": "system", "content": system_prompt}]
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
        return LLMResponse(
            text="Es gab ein Problem beim Abrufen der KI-Antwort. Bitte versuchen Sie es erneut." + AI_DISCLAIMER,
            model=chosen_model,
            error=f"HTTP {e.code}: {body[:200]}",
        )
    except Exception as e:
        return LLMResponse(
            text="Die KI-Antwort konnte nicht geladen werden. Bitte versuchen Sie es erneut." + AI_DISCLAIMER,
            model=chosen_model,
            error=str(e),
        )
