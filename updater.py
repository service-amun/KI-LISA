# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA Auto-Updater
Lädt beim Start automatisch die neuesten Dateien von GitHub.
Keine Git-Installation nötig.
"""

import urllib.request
import urllib.error
import os
import sys

REPO    = "service-amun/ki-lisa"
BRANCH  = "claude/claude-md-docs-ssfhys"
BASE    = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

DATEIEN = [
    "apps/frontend/index.html",
    "apps/backend/main.py",
    "apps/backend/groq_client.py",
    "apps/backend/session_manager.py",
    "apps/backend/compliance_context.py",
    "apps/backend/routers/datei_upload.py",
    "apps/backend/skills/router_skill.py",
    "apps/backend/skills/guardrail_skill.py",
    "requirements.txt",
]

def aktualisieren():
    print("  Prüfe auf Updates...", flush=True)
    aktualisiert = 0
    fehler = 0

    for pfad in DATEIEN:
        url = f"{BASE}/{pfad}"
        ziel = pfad.replace("/", os.sep)

        os.makedirs(os.path.dirname(ziel) or ".", exist_ok=True)

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AILIZA-Updater/1.0"},
            )
            with urllib.request.urlopen(req, timeout=8) as r:
                neu = r.read()

            # Nur schreiben wenn Inhalt sich geändert hat
            if os.path.exists(ziel):
                with open(ziel, "rb") as f:
                    if f.read() == neu:
                        continue  # keine Änderung

            with open(ziel, "wb") as f:
                f.write(neu)
            print(f"  ✓ Aktualisiert: {pfad}", flush=True)
            aktualisiert += 1

        except urllib.error.URLError:
            fehler += 1
        except Exception:
            fehler += 1

    if aktualisiert > 0:
        print(f"  {aktualisiert} Datei(en) aktualisiert.", flush=True)
    elif fehler == 0:
        print("  Bereits aktuell.", flush=True)
    else:
        print("  Offline oder keine Verbindung — starte mit lokaler Version.", flush=True)

if __name__ == "__main__":
    aktualisieren()
