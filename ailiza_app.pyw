# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA Desktop-App
Startet den Server im Hintergrund und zeigt ein Tray-Icon.
Doppelklick auf das Icon öffnet AILIZA im Browser.
"""
import os
import sys
import threading
import webbrowser
from pathlib import Path

# Projektverzeichnis als Arbeitsverzeichnis und Python-Pfad
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYTHONPATH", str(ROOT))

# .env laden
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / "apps" / "backend" / ".env")
except Exception:
    pass

PORT = int(os.getenv("AILIZA_PORT", "8001"))
NETZWERK = os.getenv("AILIZA_NETZWERK", "0").strip() in ("1", "true", "True")
HOST = "0.0.0.0" if NETZWERK else "127.0.0.1"
URL = f"http://127.0.0.1:{PORT}/dashboard"


# ── Icon generieren ──────────────────────────────────────────────────────────

def _erstelle_icon(groesse: int = 64):
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (groesse, groesse), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = groesse // 2 - 1
    cx = cy = groesse // 2
    # Grüner Kreis
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#2e7d32")
    # Weißes "A" aus Polygonen
    w = groesse
    lw = max(3, groesse // 14)
    # Linker Schenkel
    d.polygon([
        (int(w * 0.27), int(w * 0.78)),
        (int(w * 0.50), int(w * 0.18)),
        (int(w * 0.50 + lw), int(w * 0.18)),
        (int(w * 0.27 + lw * 1.6), int(w * 0.78)),
    ], fill="white")
    # Rechter Schenkel
    d.polygon([
        (int(w * 0.73), int(w * 0.78)),
        (int(w * 0.50), int(w * 0.18)),
        (int(w * 0.50 - lw), int(w * 0.18)),
        (int(w * 0.73 - lw * 1.6), int(w * 0.78)),
    ], fill="white")
    # Querstrich
    d.rectangle([
        int(w * 0.35), int(w * 0.52),
        int(w * 0.65), int(w * 0.52 + lw * 1.3),
    ], fill="white")
    return img


def _icon_als_ico_speichern(pfad: Path):
    """Speichert das Icon in allen Windows-Standardgrößen als .ico."""
    groessen = [16, 24, 32, 48, 64, 128, 256]
    bilder = [_erstelle_icon(g) for g in groessen]
    bilder[0].save(
        pfad,
        format="ICO",
        sizes=[(g, g) for g in groessen],
        append_images=bilder[1:],
    )


# ── Server im Hintergrund starten ────────────────────────────────────────────

_server_bereit = threading.Event()


def _server_thread():
    import uvicorn
    config = uvicorn.Config(
        "apps.backend.main:app",
        host=HOST,
        port=PORT,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    _server_bereit.set()
    server.run()


def _browser_oeffnen_nach_start():
    _server_bereit.wait()
    import time; time.sleep(2)
    webbrowser.open(URL)


# ── Tray-App ──────────────────────────────────────────────────────────────────

def _app_starten():
    import pystray
    from PIL import Image

    icon_bild = _erstelle_icon(64)

    def oeffnen(icon, item):
        webbrowser.open(URL)

    def beenden(icon, item):
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("AILIZA öffnen", oeffnen, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Beenden", beenden),
    )

    tray = pystray.Icon("AILIZA", icon_bild, "AILIZA KI-Assistent", menu)
    tray.run()


if __name__ == "__main__":
    # Server starten
    t_server = threading.Thread(target=_server_thread, daemon=True)
    t_server.start()

    # Browser nach dem Start öffnen
    t_browser = threading.Thread(target=_browser_oeffnen_nach_start, daemon=True)
    t_browser.start()

    # Tray-App (blockiert bis "Beenden" geklickt wird)
    _app_starten()
