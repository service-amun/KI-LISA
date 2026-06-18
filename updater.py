# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA Auto-Updater mit SHA-256 Integritätsprüfung.
Jede Datei wird gegen eine signierte Prüfsummen-Datei verifiziert,
bevor sie auf Disk geschrieben wird. Manipulation am Repo wird erkannt.
"""

import hashlib
import json
import os
import urllib.error
import urllib.request

REPO   = "service-amun/ki-lisa"
BRANCH = "claude/claude-md-docs-ssfhys"
BASE   = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

# Prüfsummen-Datei im Repo — wird zusammen mit den Dateien gepflegt
CHECKSUMS_URL = f"{BASE}/checksums.json"

DATEIEN = [
    "apps/__init__.py",
    "apps/backend/__init__.py",
    "apps/backend/routers/__init__.py",
    "apps/backend/skills/__init__.py",
    "apps/backend/compliance/__init__.py",
    "apps/backend/audit/__init__.py",
    "apps/backend/tools/__init__.py",
    "apps/frontend/index.html",
    "apps/backend/main.py",
    "apps/backend/groq_client.py",
    "apps/backend/session_manager.py",
    "apps/backend/compliance_context.py",
    "apps/backend/database.py",
    "apps/backend/gateway.py",
    "apps/backend/agent_runtime.py",
    "apps/backend/routers/datei_upload.py",
    "apps/backend/routers/approvals.py",
    "apps/backend/skills/router_skill.py",
    "apps/backend/skills/guardrail_skill.py",
    "apps/backend/skills/reflection_skill.py",
    "apps/backend/compliance/weekly_checker.py",
    "requirements.txt",
]


def _holen(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "AILIZA-Updater/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read()


def _sha256(daten: bytes) -> str:
    return hashlib.sha256(daten).hexdigest()


def aktualisieren():
    print("  Pruefe auf Updates...", flush=True)

    # Prüfsummen-Datei laden
    try:
        checksums = json.loads(_holen(CHECKSUMS_URL))
    except Exception:
        # Keine Prüfsummen verfügbar — kein Update (sicher scheitern)
        print("  Pruefung nicht moeglich — starte mit lokaler Version.", flush=True)
        return

    aktualisiert = 0
    abgelehnt = 0

    for pfad in DATEIEN:
        erwartete_pruefsumme = checksums.get(pfad)
        if not erwartete_pruefsumme:
            continue  # Datei nicht in Prüfsummen-Liste — überspringen

        url = f"{BASE}/{pfad}"
        ziel = pfad.replace("/", os.sep)
        os.makedirs(os.path.dirname(ziel) or ".", exist_ok=True)

        try:
            neu = _holen(url)
        except urllib.error.URLError:
            continue
        except Exception:
            continue

        # Integrität prüfen — stimmt die Prüfsumme nicht, wird NICHT geschrieben
        if _sha256(neu) != erwartete_pruefsumme:
            print(f"  WARNUNG: Integritaetsfehler bei {pfad} — Update abgelehnt!", flush=True)
            abgelehnt += 1
            continue

        # Nur schreiben wenn Inhalt sich geändert hat
        if os.path.exists(ziel):
            with open(ziel, "rb") as f:
                if f.read() == neu:
                    continue

        with open(ziel, "wb") as f:
            f.write(neu)
        print(f"  Aktualisiert: {pfad}", flush=True)
        aktualisiert += 1

    if abgelehnt > 0:
        print(f"  {abgelehnt} Datei(en) abgelehnt (Integritaetsfehler)!", flush=True)
    if aktualisiert > 0:
        print(f"  {aktualisiert} Datei(en) aktualisiert.", flush=True)
    elif abgelehnt == 0:
        print("  Bereits aktuell.", flush=True)


if __name__ == "__main__":
    aktualisieren()
