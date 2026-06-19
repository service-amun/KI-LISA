# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Gateway
Sichere Tool-Ausführung mit Policy-Gate und Audit-Logging.
Einheitlicher Einstiegspunkt für alle Tool-Aufrufe.
"""

from audit.audit_logger import write_audit_entry
from agent_runtime import run_search, run_fetch, ToolResult
from ailiza_guard import enforce_policy


def ausfuehren(tool: str, eingabe: str, session_id: str = "system") -> ToolResult:
    """
    Führt ein Tool aus — mit Policy-Gate davor und Audit danach.

    tool:    "suche" | "abruf"
    eingabe: Suchbegriff oder URL
    """
    action = "run_search" if tool == "suche" else "run_fetch"
    policy = enforce_policy(eingabe, action=action, session_id=session_id)

    if not policy.allowed:
        # Credentials bekommen sparses Audit-Event — kein Inhalt
        if policy.is_credential_block:
            write_audit_entry("gateway.credential_blocked", {
                "tool": tool,
                "session_id": session_id[:8] + "...",
                "action": action,
                "content_stored": False,
            })
        else:
            write_audit_entry("gateway.blocked", {
                "tool": tool,
                "session_id": session_id[:8] + "...",
                "decision": policy.decision,
                "data_classes": policy.policy.get("data_classes", []),
                "rule": policy.policy.get("triggered_rules", []),
            })
        return ToolResult(tool=tool, success=False, error=policy.message)

    # PII-bereinigten Text verwenden (falls Anonymisierung nötig)
    bereinigt = policy.sanitized_text or eingabe

    if tool == "suche":
        result = run_search(bereinigt)
    elif tool == "abruf":
        # Originale URL übergeben — URL-Sicherheit wurde bereits in enforce_policy geprüft
        result = run_fetch(eingabe)
    else:
        return ToolResult(tool=tool, success=False, error=f"Unbekanntes Tool: {tool}")

    write_audit_entry(f"gateway.{tool}", {
        "session_id": session_id[:8] + "...",
        "success": result.success,
        "decision": policy.decision,
        "pii_bereinigt": bool(policy.token_map),
        "data_classes": policy.policy.get("data_classes", []),
        "error": (result.error or "")[:80] if not result.success else None,
    })

    return result
