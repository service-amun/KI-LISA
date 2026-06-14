"""
KI-LISA — Gateway
Sichere Tool-Ausführung mit Guardrail-Prüfung und Audit-Logging.
Einheitlicher Einstiegspunkt für alle Tool-Aufrufe.
"""

from audit.audit_logger import write_audit_entry
from agent_runtime import run_search, run_fetch, ToolResult
from skills.guardrail_skill import check_input


def ausfuehren(tool: str, eingabe: str, session_id: str = "system") -> ToolResult:
    """
    Führt ein Tool aus — mit Guardrail davor und Audit danach.

    tool:     "suche" | "abruf"
    eingabe:  Suchbegriff oder URL
    """
    guard = check_input(eingabe)

    if guard.blocked:
        write_audit_entry("gateway.blocked", {
            "tool": tool,
            "session_id": session_id[:8] + "...",
            "grund": guard.block_reason[:100],
        })
        return ToolResult(tool=tool, success=False, error=guard.block_reason)

    bereinigt = guard.sanitized_text or eingabe

    if tool == "suche":
        result = run_search(bereinigt)
    elif tool == "abruf":
        result = run_fetch(eingabe)   # URL nicht tokenisieren
    else:
        return ToolResult(tool=tool, success=False, error=f"Unbekanntes Tool: {tool}")

    write_audit_entry(f"gateway.{tool}", {
        "session_id": session_id[:8] + "...",
        "success": result.success,
        "pii_bereinigt": bool(guard.pii_found),
        "error": (result.error or "")[:80] if not result.success else None,
    })

    return result
