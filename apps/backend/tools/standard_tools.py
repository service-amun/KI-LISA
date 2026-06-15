# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Standard Tools Registry
Definiert alle verfügbaren Tools mit Metadaten.
"""

from dataclasses import dataclass
from typing import Callable

import gateway


@dataclass
class Tool:
    id: str
    name: str
    beschreibung: str
    beispiel: str
    erfordert_netzwerk: bool = True

    def ausfuehren(self, eingabe: str, session_id: str = "system"):
        return gateway.ausfuehren(self.id.replace("_", ""), eingabe, session_id)


TOOLS: list[Tool] = [
    Tool(
        id="suche",
        name="Web-Suche",
        beschreibung="Sucht aktuelle Informationen, Nachrichten und Fakten im Internet.",
        beispiel="Aktuelle DSGVO-Bußgelder in Deutschland 2025",
    ),
    Tool(
        id="abruf",
        name="URL-Abruf",
        beschreibung="Ruft den Textinhalt einer Webseite ab.",
        beispiel="https://www.bfdi.bund.de/",
    ),
]


def tool_info() -> list[dict]:
    return [
        {"id": t.id, "name": t.name, "beschreibung": t.beschreibung, "beispiel": t.beispiel}
        for t in TOOLS
    ]


def tool_finden(tool_id: str) -> Tool | None:
    return next((t for t in TOOLS if t.id == tool_id), None)
