# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Windows App Launcher
Startet den Server und öffnet den Browser automatisch.
Wird von PyInstaller als Einstiegspunkt genutzt.
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path


# ── Pfade je nach Ausführungsart setzen ──────────────────────────────────────
# PyInstaller entpackt alles nach sys._MEIPASS
# Im normalen Betrieb ist BASE_DIR das Projektverzeichnis

if getattr(sys, "frozen", False):
    # Als .exe kompiliert
    BASE_DIR = Path(sys._MEIPASS)
    USER_DIR = Path(sys.executable).parent  # Neben der .exe
else:
    # Direkt als Python-Script
    BASE_DIR = Path(__file__).parent
    USER_DIR = BASE_DIR

# Eigene Module findbar machen
sys.path.insert(0, str(BASE_DIR / "apps" / "backend"))

# ── Datenpfade konfigurieren ──────────────────────────────────────────────────
data_dir = USER_DIR / "data"
data_dir.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("AILIZA_DB_PATH",      str(data_dir / "ailiza.db"))
os.environ.setdefault("AILIZA_AUDIT_DB_PATH", str(data_dir / "audit.db"))
os.environ.setdefault("AILIZA_MEMORY_DB_PATH", str(data_dir / "reflection.db"))

# ── .env laden ────────────────────────────────────────────────────────────────
env_file = USER_DIR / ".env"
if not env_file.exists():
    env_example = BASE_DIR / ".env.example"
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)

try:
    from dotenv import load_dotenv
    load_dotenv(env_file)
except Exception:
    pass

# ── Port bestimmen ────────────────────────────────────────────────────────────
PORT = int(os.environ.get("AILIZA_PORT", "8001"))
URL  = f"http://127.0.0.1:{PORT}/dashboard"


# ── Browser nach Serverstart öffnen ──────────────────────────────────────────
def _browser_oeffnen():
    time.sleep(3)
    webbrowser.open(URL)

threading.Thread(target=_browser_oeffnen, daemon=True).start()


# ── Konsolenausgabe ───────────────────────────────────────────────────────────
print("\n" + "═" * 50)
print("  AILIZA — EU-konformer KI-Assistent")
print("  © 2026 Karola Fromm-Nasreldin")
print("═" * 50)
print(f"\n  Läuft auf: {URL}")
print("  Browser öffnet sich in 3 Sekunden...")
print("  Zum Beenden: dieses Fenster schließen\n")


# ── Server starten ────────────────────────────────────────────────────────────
try:
    import uvicorn
    uvicorn.run(
        "main:app",
        app_dir=str(BASE_DIR / "apps" / "backend"),
        host="127.0.0.1",
        port=PORT,
        log_level="warning",
    )
except KeyboardInterrupt:
    print("\n  AILIZA wurde beendet.")
