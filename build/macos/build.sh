#!/usr/bin/env bash
# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
# macOS Build — erstellt AILIZA.dmg
# Voraussetzungen: Python 3.11+, create-dmg (brew install create-dmg)

set -e
cd "$(dirname "$0")/../.."
ROOT="$(pwd)"

echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║   AILIZA Build — macOS AILIZA.dmg           ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""

# Voraussetzungen
command -v python3 >/dev/null || { echo "FEHLER: Python3 fehlt"; exit 1; }
command -v create-dmg >/dev/null || { echo "FEHLER: create-dmg fehlt. 'brew install create-dmg'"; exit 1; }

echo "  [1/4] Installiere Build-Pakete ..."
python3 -m pip install pyinstaller pillow -q
python3 -m pip install -r requirements.txt -q

echo "  [2/4] Kompiliere AILIZA.app ..."
python3 -m PyInstaller ailiza.spec --clean --noconfirm \
  --target-arch universal2

echo "  [3/4] Erstelle DMG ..."
mkdir -p build/output
create-dmg \
  --volname "AILIZA" \
  --volicon "ailiza.ico" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "AILIZA.app" 175 190 \
  --hide-extension "AILIZA.app" \
  --app-drop-link 425 190 \
  "build/output/AILIZA.dmg" \
  "dist/AILIZA/"

echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║   FERTIG!  build/output/AILIZA.dmg          ║"
echo "  ╚══════════════════════════════════════════════╝"
echo ""
open build/output
