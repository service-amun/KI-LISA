@echo off
chcp 65001 >nul 2>&1
title AILIZA — Windows App bauen

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║  AILIZA — Windows Installer bauen       ║
echo  ║  © 2026 Karola Fromm-Nasreldin          ║
echo  ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0.."

:: ── Python prüfen ─────────────────────────────────────────────────────────
where python >nul 2>&1
if errorlevel 1 (
    echo  FEHLER: Python nicht gefunden.
    echo  Bitte Python 3.11 installieren: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo  Python %%v gefunden. OK.

:: ── Abhängigkeiten + PyInstaller installieren ────────────────────────────
echo.
echo  Installiere Pakete...
python -m pip install -r requirements.txt -q --disable-pip-version-check
python -m pip install pyinstaller -q --disable-pip-version-check
echo  Pakete OK.

:: ── Altes Build-Verzeichnis löschen ──────────────────────────────────────
if exist "dist\AILIZA" rmdir /s /q "dist\AILIZA"
if exist "build\AILIZA" rmdir /s /q "build\AILIZA"

:: ── Build starten ─────────────────────────────────────────────────────────
echo.
echo  Baue AILIZA App (das dauert 2-5 Minuten)...
echo.
pyinstaller installer\ailiza.spec --noconfirm

if errorlevel 1 (
    echo.
    echo  FEHLER beim Bauen. Bitte Fehlermeldung oben prüfen.
    pause
    exit /b 1
)

:: ── Ergebnis prüfen ───────────────────────────────────────────────────────
if not exist "dist\AILIZA\AILIZA.exe" (
    echo.
    echo  FEHLER: AILIZA.exe wurde nicht gefunden.
    pause
    exit /b 1
)

:: ── .env.example kopieren ─────────────────────────────────────────────────
copy ".env.example" "dist\AILIZA\.env.example" >nul

:: ── Start-Skript erstellen ────────────────────────────────────────────────
(
echo @echo off
echo title AILIZA
echo cd /d "%%~dp0"
echo if not exist ".env" copy ".env.example" ".env" ^>nul
echo start "" "AILIZA.exe"
) > "dist\AILIZA\AILIZA starten.bat"

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║  FERTIG! App liegt in: dist\AILIZA\     ║
echo  ║                                         ║
echo  ║  Weitergeben: dist\AILIZA\ Ordner       ║
echo  ║  Starten: "AILIZA starten.bat"          ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  Nächste Schritte:
echo  1. dist\AILIZA\ Ordner als ZIP verpacken
echo  2. ZIP an Nutzer weitergeben
echo  3. Nutzer entpackt ZIP, trägt API-Key in .env ein
echo  4. Doppelklick auf "AILIZA starten.bat"
echo.
pause
