"""
KI-LISA — Groq LLM Client
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
    "standard": "llama3-70b-8192",
    "schnell": "llama3-8b-8192",
    "alternativ": "mixtral-8x7b-32768",
}

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

AI_DISCLAIMER = "\n\n---\n*KI-generiert — KI-LISA (EU AI Act Art. 52). Bitte prüfen Sie wichtige Entscheidungen.*"


def is_configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def chat(
    message: str,
    system_prompt: str,
    context: list = None,
    model: str = None,
) -> LLMResponse:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return LLMResponse(
            text=(
                "KI-LISA ist noch nicht vollständig eingerichtet. "
                "Bitte wenden Sie sich an Ihren Administrator."
                + AI_DISCLAIMER
            ),
            model="none",
            error="kein_api_key",
        )

    chosen_model = model or MODELS["standard"]

    messages = [{"role": "system", "content": system_prompt}]
    for m in (context or [])[-10:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": message})

    payload = json.dumps({
        "model": chosen_model,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7,
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

        if "ki-lisa" not in text.lower() and "ki-system" not in text.lower():
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
