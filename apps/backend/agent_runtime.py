"""
KI-LISA — Agent Runtime
Führt Aufgaben aus: Web-Suche via Tavily, URL-Abruf.
"""

import json
import os
import urllib.parse
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ToolResult:
    tool: str
    success: bool
    summary: dict = field(default_factory=dict)
    error: Optional[str] = None


def run_search(query: str) -> ToolResult:
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return ToolResult(
            tool="search",
            success=False,
            error="Web-Suche nicht konfiguriert. Bitte TAVILY_API_KEY setzen.",
        )

    payload = json.dumps({
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 5,
    }).encode()

    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        results = data.get("results", [])
        return ToolResult(
            tool="search",
            success=True,
            summary={
                "query": query,
                "top_results": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", "")[:500],
                    }
                    for r in results[:5]
                ],
            },
        )
    except Exception as e:
        return ToolResult(tool="search", success=False, error=str(e))


def run_fetch(url: str) -> ToolResult:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "KI-LISA/1.0 (EU AI Act konform)"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read(50_000).decode("utf-8", errors="replace")

        import re
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"\s+", " ", text).strip()

        return ToolResult(
            tool="fetch",
            success=True,
            summary={"url": url, "text_preview": text[:1000], "title": url},
        )
    except Exception as e:
        return ToolResult(tool="fetch", success=False, error=str(e))


def run_task(task: str) -> list[ToolResult]:
    task_lower = task.lower()

    if task_lower.startswith("http://") or task_lower.startswith("https://"):
        return [run_fetch(task.strip())]

    return [run_search(task)]
