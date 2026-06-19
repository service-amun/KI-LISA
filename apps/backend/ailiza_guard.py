# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Policy Guard
Zentraler Einstiegspunkt für alle Policy-Entscheidungen.

Entscheidungen:
  allow            — erlauben
  allow_with_notice — erlauben mit Hinweis (z.B. PII anonymisiert)
  require_approval  — Freigabe durch Admin nötig
  block            — blockiert

Aufrufreihenfolge (fail-closed):
  1. Credential-Erkennung (Stufe 5 — sofort blockieren, kein Audit-Inhalt)
  2. Kill-Switch (AILIZA_EXTERNAL_LLM_ENABLED) — default: false
  3. Opt-in-Check (AILIZA_MEMORY_ENABLED) — default: false
  4. URL-Sicherheit (nur für run_fetch) — inkl. DNS-Auflösung
  5. Guardrail-Prüfung (PII, verbotene Praktiken, Hochrisiko)
  6. Datenklassen-Regelwerk aus policy_rules.json
"""

import ipaddress
import json
import os
import re
import socket
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from skills.guardrail_skill import check_input, GuardrailResult

_RULES_PATH = Path(__file__).parent / "policy_rules.json"


def _load_rules() -> dict:
    try:
        with open(_RULES_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"actions": {}, "credential_patterns": [], "messages": {}}


_RULES: dict = _load_rules()


@dataclass
class PolicyResult:
    decision: str = "allow"          # allow | allow_with_notice | require_approval | block
    allowed: bool = True
    message: str = ""
    policy: dict = field(default_factory=dict)
    sanitized_text: Optional[str] = None
    token_map: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    is_credential_block: bool = False  # Sparse-Audit: kein Inhalt loggen
    pii_found: list = field(default_factory=list)
    requires_human_oversight: bool = False


# ── Interne Hilfsfunktionen ───────────────────────────────────────────────────

def _detect_credentials(text: str) -> bool:
    """Erkennt API-Keys, Tokens, Passwörter — Stufe 5 (Credentials)."""
    for pattern in _RULES.get("credential_patterns", []):
        if re.search(pattern, text):
            return True
    return False


def _classify_pii_to_data_class(guardrail: GuardrailResult) -> list[int]:
    """
    Mappt erkannte PII-Typen auf Datenklassen (0-10).
    Strengste Regel gewinnt im Aufrufer.
    """
    classes = set()
    pii_class_map = {
        "E-Mail-Adresse": 3,
        "Telefonnummer": 3,
        "Kontoverbindung": 6,
        "Geburtsdatum": 3,
        "IP-Adresse": 3,
        "Sozialversicherung": 3,
    }
    for pii_typ in guardrail.pii_found:
        cls = pii_class_map.get(pii_typ, 3)
        classes.add(cls)
    if guardrail.requires_human_oversight:
        classes.add(3)
    return sorted(classes)


def _strictest_decision(decisions: list[str]) -> str:
    """Gibt die strengste Entscheidung aus einer Liste zurück."""
    order = ["allow", "allow_with_notice", "require_approval", "block"]
    result = "allow"
    for d in decisions:
        if order.index(d) > order.index(result):
            result = d
    return result


def _build_private_ranges() -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    """Baut die Liste privater IP-Ranges aus der Konfiguration."""
    ranges = []
    for r in _RULES.get("private_ip_ranges", [
        "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
        "127.0.0.0/8", "169.254.0.0/16", "0.0.0.0/8", "100.64.0.0/10",
        "::1/128", "fc00::/7", "fe80::/10",
    ]):
        try:
            ranges.append(ipaddress.ip_network(r, strict=False))
        except ValueError:
            pass
    return ranges


_PRIVATE_RANGES: list = _build_private_ranges()


def _ip_is_private(ip_str: str) -> bool:
    """Prüft ob eine IP-Adresse privat/intern ist."""
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
            return True
        for rng in _PRIVATE_RANGES:
            if ip in rng:
                return True
    except ValueError:
        pass
    return False


def _resolve_hostname(hostname: str, timeout: float = 2.0) -> list[str]:
    """
    DNS-Auflösung mit Timeout.
    Gibt [] zurück bei Fehler — fail-open: kein Block bei DNS-Ausfall.
    """
    old_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout)
        infos = socket.getaddrinfo(hostname, None)
        return list({info[4][0] for info in infos})
    except (socket.gaierror, OSError):
        return []
    finally:
        socket.setdefaulttimeout(old_timeout)


def _check_url_safety(url: str) -> tuple[bool, str]:
    """
    SSRF-Schutz: blockiert private IPs, interne Adressen, unsichere Schemes.
    Prüft zusätzlich per DNS-Auflösung gegen DNS-Rebinding-Angriffe.
    Gibt (safe, reason) zurück.
    """
    msgs = _RULES.get("messages", {})
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False, "Ungültige URL."

    # Nur http/https erlaubt
    if parsed.scheme not in {"http", "https"}:
        return False, msgs.get("blocked_url_scheme", "URL-Schema nicht erlaubt.")

    hostname = parsed.hostname
    if not hostname:
        return False, "Kein Hostname in der URL."

    # Explizit blockierte Hostnamen (Konfiguration + Hardcode)
    blocked_hosts = set(
        h.lower() for h in _RULES.get("blocked_hostnames", [])
    ) | {"localhost", "0.0.0.0"}
    if hostname.lower() in blocked_hosts:
        return False, msgs.get("blocked_private_url", "Interne Adressen nicht erlaubt.")

    # IP-Literal direkt prüfen
    try:
        if _ip_is_private(hostname):
            return False, msgs.get("blocked_private_url", "Interne Adressen nicht erlaubt.")
    except ValueError:
        pass  # kein IP-Literal

    # DNS-Auflösung: Hostnamen auf private IPs prüfen (DNS-Rebinding-Schutz)
    resolved = _resolve_hostname(hostname)
    for ip_str in resolved:
        if _ip_is_private(ip_str):
            return False, msgs.get("blocked_dns_rebind", "Diese Adresse löst auf eine interne IP auf.")

    return True, ""


# ── Haupt-API ─────────────────────────────────────────────────────────────────

def enforce_policy(
    text: str,
    action: str,
    session_id: str = "system",
    existing_token_map: Optional[dict] = None,
) -> PolicyResult:
    """
    Zentrale Policy-Entscheidung für eine Aktion.

    text:               Eingabetext (Prompt, URL, Memory-Fakt, etc.)
    action:             "call_external_model" | "run_search" | "run_fetch" |
                        "save_memory" | "write_system"
    session_id:         Für konsistentes PII-Mapping innerhalb einer Session
    existing_token_map: Bereits bekannte PII-Tokens dieser Session

    Rückgabe: PolicyResult mit decision, allowed, message, sanitized_text, token_map
    """
    msgs = _RULES.get("messages", {})
    action_rules = _RULES.get("actions", {}).get(action, {})

    # ── 1. Credential-Erkennung — vor allem anderen ───────────────────────────
    if _detect_credentials(text):
        return PolicyResult(
            decision="block",
            allowed=False,
            message=msgs.get("blocked_credential", "Zugangsdaten erkannt — blockiert."),
            policy={"rule": "credential_detection", "action": action},
            is_credential_block=True,
        )

    # ── 2. Kill-Switch (fail-closed: fehlt oder ungültig → blockieren) ────────
    kill_switch_env = action_rules.get("kill_switch_env")
    if kill_switch_env:
        raw = os.getenv(kill_switch_env)
        enabled = raw is not None and raw.lower().strip() in {"true", "1", "yes", "on"}
        if not enabled:
            return PolicyResult(
                decision="block",
                allowed=False,
                message=msgs.get("kill_switch_off", "Externe Verarbeitung deaktiviert."),
                policy={"rule": "kill_switch", "env": kill_switch_env, "action": action},
            )

    # ── 3. Opt-in-Check (fail-closed: fehlt oder ungültig → blockieren) ──────
    opt_in_env = action_rules.get("require_opt_in_env")
    if opt_in_env:
        raw = os.getenv(opt_in_env)
        opt_in = raw is not None and raw.lower().strip() in {"true", "1", "yes", "on"}
        if not opt_in:
            return PolicyResult(
                decision="block",
                allowed=False,
                message=msgs.get("memory_disabled", "Langzeitspeicher nicht aktiviert."),
                policy={"rule": "opt_in_required", "env": opt_in_env, "action": action},
            )

    # ── 4. URL-Sicherheit (nur run_fetch) ─────────────────────────────────────
    if action == "run_fetch":
        safe, reason = _check_url_safety(text)
        if not safe:
            return PolicyResult(
                decision="block",
                allowed=False,
                message=reason,
                policy={"rule": "url_safety", "action": action},
            )

    # ── 5. Guardrail-Prüfung (PII, verbotene Praktiken, Hochrisiko) ──────────
    guardrail: GuardrailResult = check_input(text, existing_token_map)

    if guardrail.blocked:
        return PolicyResult(
            decision="block",
            allowed=False,
            message=guardrail.block_reason,
            policy={"rule": "prohibited_practice", "action": action},
            warnings=guardrail.warnings,
        )

    # ── 6. Datenklassen → Regelwerk ───────────────────────────────────────────
    data_classes = _classify_pii_to_data_class(guardrail)
    class_rules = action_rules.get("data_class_rules", {})
    default_decision = action_rules.get("default", "allow")

    decisions = []
    triggered_rules = []
    for cls in data_classes:
        rule = class_rules.get(str(cls), default_decision)
        decisions.append(rule)
        triggered_rules.append({"data_class": cls, "decision": rule})

    final_decision = _strictest_decision(decisions) if decisions else default_decision

    # ── 7. Ergebnis zusammenstellen ───────────────────────────────────────────
    allowed = final_decision in {"allow", "allow_with_notice"}
    message = ""

    if final_decision == "block":
        if 4 in data_classes:
            message = msgs.get("blocked_special_category", "Besonders schützenswerte Daten — blockiert.")
        else:
            message = f"Diese Aktion ist für die erkannten Datenklassen nicht erlaubt ({action})."
    elif final_decision == "allow_with_notice":
        message = msgs.get("allow_with_notice_pii", "Daten werden vor externer Verarbeitung anonymisiert.")
    elif final_decision == "require_approval":
        allowed = False
        if action == "save_memory":
            message = msgs.get("require_approval_memory", "Admin-Freigabe für Speicherung nötig.")
        else:
            message = msgs.get("require_approval_write", "Freigabe für diesen Vorgang nötig.")

    warnings = list(guardrail.warnings)
    if guardrail.requires_human_oversight:
        warnings.append(
            "Diese Anfrage betrifft eine Hochrisiko-Entscheidung. "
            "Bitte lassen Sie das Ergebnis von einer Fachkraft prüfen. (EU AI Act Art. 6)"
        )

    return PolicyResult(
        decision=final_decision,
        allowed=allowed,
        message=message,
        policy={
            "action": action,
            "data_classes": data_classes,
            "triggered_rules": triggered_rules,
            "final_decision": final_decision,
        },
        sanitized_text=guardrail.sanitized_text,
        token_map=guardrail.token_map,
        warnings=warnings,
        pii_found=guardrail.pii_found,
        requires_human_oversight=guardrail.requires_human_oversight,
    )
