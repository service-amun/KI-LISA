@echo off
chcp 65001 >nul 2>&1
title KI-LISA — KI-Assistent

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║  KI-LISA — EU-konformer KI-Assistent    ║
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
    echo    4. Dann KI-LISA erneut starten.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo  Python %%v gefunden. OK.

:: ── .env prüfen ───────────────────────────────────────────────────────────
if not exist "apps\backend\.env" (
    echo.
    echo  HINWEIS: Noch keine Einrichtung gefunden.
    echo.
    echo  Bitte die Datei  apps\backend\.env  anlegen.
    echo  Vorlage:  .env.example  im gleichen Ordner.
    echo.
    echo  Benötigter Eintrag:
    echo    GROQ_API_KEY=gsk_...
    echo    (kostenlos registrieren auf console.groq.com)
    echo.
    set /p WEITER="Trotzdem starten? (j/n): "
    if /i not "%WEITER%"=="j" (
        echo Abgebrochen.
        pause
        exit /b 0
    )
)

:: ── Pakete installieren ───────────────────────────────────────────────────
echo.
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
echo  ║  KI-LISA läuft auf:                     ║
echo  ║  http://127.0.0.1:8001/dashboard        ║
echo  ║                                         ║
echo  ║  Browser öffnet sich gleich...          ║
echo  ║  Zum Beenden: Strg+C oder Fenster zu   ║
echo  ╚══════════════════════════════════════════╝
echo.

start "" cmd /c "timeout /t 3 /nobreak >nul && start \"\" \"http://127.0.0.1:8001/dashboard\""

python -m uvicorn apps.backend.main:app --port 8001 --host 127.0.0.1

echo.
echo  KI-LISA wurde beendet.
pause
