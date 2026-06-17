@echo off
chcp 65001 >nul 2>&1
title AILIZA — KI-Assistent

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║  AILIZA — EU-konformer KI-Assistent    ║
echo  ║  Bitte dieses Fenster NICHT schließen!  ║
echo  ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: ── Python prüfen ─────────────────────────────────────────────────────────
where python >nul 2>&1
if errorlevel 1 (
    echo  FEHLER: Python nicht gefunden.
    echo.
    echo  Bitte Python 3.11 installieren:
    echo    1. Gehen Sie zu https://www.python.org/downloads/
    echo    2. Python 3.11 herunterladen und installieren
    echo    3. WICHTIG: "Add Python to PATH" ankreuzen!
    echo    4. Dann AILIZA erneut starten.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo  Python %%v gefunden. OK.

:: ── .env prüfen ───────────────────────────────────────────────────────────
if not exist "apps\backend\.env" (
    echo.
    echo  HINWEIS: Noch keine Einrichtung gefunden.
    echo  Kopiere .env.example nach apps\backend\.env und trage deinen GROQ_API_KEY ein.
    echo.
    copy ".env.example" "apps\backend\.env" >nul 2>&1
    echo  Vorlage wurde nach apps\backend\.env kopiert.
    echo  Bitte dort den GROQ_API_KEY eintragen und neu starten.
    echo.
    pause
    exit /b 0
)

:: ── Port aus .env lesen (Standard: 8001) ─────────────────────────────────
set AILIZA_PORT=8001
for /f "tokens=1,2 delims==" %%a in (apps\backend\.env) do (
    if "%%a"=="AILIZA_PORT" set AILIZA_PORT=%%b
)

:: ── Auto-Update ────────────────────────────────────────────────────────────
echo.
python updater.py
echo.

:: ── Pakete installieren ───────────────────────────────────────────────────
echo  Prüfe Pakete (erste Ausführung dauert ~30 Sekunden)...
python -m pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo  FEHLER: Pakete konnten nicht installiert werden.
    echo  Bitte Internetverbindung prüfen und erneut versuchen.
    pause
    exit /b 1
)
echo  Pakete OK.

:: ── Server starten, Browser nach 3 Sekunden öffnen ───────────────────────
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║  AILIZA läuft auf:                     ║
echo  ║  http://127.0.0.1:%AILIZA_PORT%/dashboard        ║
echo  ║                                         ║
echo  ║  Browser öffnet sich gleich...          ║
echo  ║  Zum Beenden: Strg+C oder Fenster zu   ║
echo  ╚══════════════════════════════════════════╝
echo.

start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:%AILIZA_PORT%/dashboard"

python -m uvicorn apps.backend.main:app --port %AILIZA_PORT% --host 127.0.0.1

echo.
echo  AILIZA wurde beendet.
pause
