@echo off
chcp 65001 >nul 2>&1
title AILIZA - KI-Assistent

cd /d "%~dp0"

echo.
echo  *** AILIZA - EU-konformer KI-Assistent ***
echo  Bitte dieses Fenster NICHT schliessen!
echo.

:: Python pruefen
where python >nul 2>&1
if errorlevel 1 (
    echo  FEHLER: Python nicht gefunden.
    echo  Bitte Python 3.11 installieren: https://www.python.org/downloads/
    echo  WICHTIG: "Add Python to PATH" ankreuzen!
    pause
    exit /b 1
)

:: .env pruefen
if not exist "apps\backend\.env" (
    echo  HINWEIS: Keine Einrichtung gefunden.
    copy ".env.example" "apps\backend\.env" >nul 2>&1
    echo  Vorlage wurde nach apps\backend\.env kopiert.
    echo  Bitte dort den GROQ_API_KEY eintragen und neu starten.
    pause
    exit /b 0
)

:: Pakete installieren (muss VOR dem Updater laufen, damit Abhaengigkeiten vorhanden sind)
echo  Pruefe Pakete...
python -m pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    echo  FEHLER: Pakete konnten nicht installiert werden.
    pause
    exit /b 1
)
echo  Pakete OK.
echo.

:: Auto-Update (laeuft nach pip install, damit Updater-Abhaengigkeiten verfuegbar sind)
echo  Pruefe auf Updates...
python updater.py
echo.

:: PYTHONPATH explizit auf das Projektverzeichnis setzen,
:: damit Python das 'apps'-Paket immer findet
set PYTHONPATH=%~dp0

:: Server starten
:: HINWEIS: Fuer Railway/Container-Deployments --host 0.0.0.0 und --port $PORT verwenden (siehe Procfile).
echo  AILIZA laeuft auf: http://127.0.0.1:8001/dashboard
echo  Browser oeffnet sich gleich...
echo  Zum Beenden: Strg+C oder Fenster schliessen
echo.

start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8001/dashboard"

python -m uvicorn apps.backend.main:app --port 8001 --host 127.0.0.1

echo.
echo  AILIZA wurde beendet.
pause
