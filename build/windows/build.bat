@echo off
chcp 65001 >nul 2>&1
title AILIZA — Build Windows Installer
cd /d "%~dp0..\.."

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   AILIZA Build — Windows AILIZA-Setup.exe              ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: Voraussetzungen prüfen
where python >nul 2>&1
if errorlevel 1 (
    echo  FEHLER: Python nicht gefunden.
    pause & exit /b 1
)
where iscc >nul 2>&1
if errorlevel 1 (
    echo  HINWEIS: Inno Setup nicht gefunden.
    echo  Bitte Inno Setup installieren: https://jrsoftware.org/isdl.php
    echo  Dann dieses Skript erneut starten.
    pause & exit /b 1
)

:: Build-Umgebung vorbereiten
echo  [1/5] Installiere Build-Pakete ...
python -m pip install pyinstaller pillow -q --disable-pip-version-check
python -m pip install -r requirements.txt -q --disable-pip-version-check

:: Icon erzeugen
echo  [2/5] Erzeuge Icon ...
python -c "import sys,os; sys.path.insert(0,'.'); os.chdir('.'); exec(open('ailiza_app.pyw').read().split('if __name__')[0]); _icon_als_ico_speichern(__import__('pathlib').Path('ailiza.ico'))"

:: PyInstaller
echo  [3/5] Kompiliere AILIZA.exe ...
python -m PyInstaller ailiza.spec --clean --noconfirm
if errorlevel 1 (
    echo  FEHLER beim Kompilieren.
    pause & exit /b 1
)

:: .env.example in dist kopieren
echo  [4/5] Dateien kopieren ...
copy ".env.example" "dist\AILIZA\.env.example" >nul

:: Inno Setup — Installer bauen
echo  [5/5] Erstelle AILIZA-Setup.exe ...
iscc "build\windows\ailiza_setup.iss"
if errorlevel 1 (
    echo  FEHLER beim Erstellen des Installers.
    pause & exit /b 1
)

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║   FERTIG!                                               ║
echo  ║   Installer:  build\output\AILIZA-Setup.exe            ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
explorer "build\output"
pause
