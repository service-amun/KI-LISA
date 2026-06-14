@echo off
title KI-LISA — KI-Assistent
echo.
echo  ╔════════════════════════════════╗
echo  ║   KI-LISA startet...           ║
echo  ║   Bitte Fenster offen lassen!  ║
echo  ╚════════════════════════════════╝
echo.

cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert.
    echo Bitte python.org aufrufen und Python 3.11 installieren.
    pause
    exit /b 1
)

if not exist "apps\backend\.env" (
    echo HINWEIS: Keine .env Datei gefunden.
    echo Bitte .env.example nach apps\backend\.env kopieren und API-Keys eintragen.
    pause
    exit /b 1
)

pip install -r requirements.txt -q

echo.
echo  KI-LISA laeuft jetzt!
echo  Browser oeffnet sich automatisch...
echo.

start "" "http://127.0.0.1:8001/dashboard"
python -m uvicorn apps.backend.main:app --port 8001

pause
