@echo off
chcp 65001 >nul 2>&1
title AILIZA - KI-Assistent

cd /d "%~dp0"

:: Gebündeltes Python bevorzugen, sonst System-Python
if exist "%~dp0_python\python.exe" (
    set PYTHON=%~dp0_python\python.exe
) else (
    set PYTHON=python
)

echo.
echo  *** AILIZA - EU-konformer KI-Assistent ***
echo  Bitte dieses Fenster NICHT schliessen!
echo.

:: Python pruefen
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo  FEHLER: Python nicht gefunden.
    echo  Bitte AILIZA.bat starten — richtet Python automatisch ein.
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

:: Pakete installieren
echo  Pruefe Pakete...
"%PYTHON%" -m pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    echo  FEHLER: Pakete konnten nicht installiert werden.
    pause
    exit /b 1
)
echo  Pakete OK.
echo.

:: Auto-Update
echo  Pruefe auf Updates...
"%PYTHON%" updater.py
echo.

:: PYTHONPATH setzen — stellt sicher dass Python 'apps' findet
set PYTHONPATH=%~dp0

:: Autostart beim Windows-Login einrichten (einmalig, lautlos)
schtasks /query /tn "AILIZA" >nul 2>&1
if errorlevel 1 (
    schtasks /create /tn "AILIZA" /tr "\"%~dp0start_ailiza_hintergrund.bat\"" /sc onlogon /rl limited /f >nul 2>&1
    if not errorlevel 1 echo  Autostart eingerichtet — AILIZA startet kuenftig automatisch beim Einloggen.
)

:: Netzwerk-IP ermitteln fuer Buero-Betrieb
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set LAN_IP=%%a
    goto :ip_gefunden
)
:ip_gefunden
set LAN_IP=%LAN_IP: =%

:: Modus aus .env lesen (AILIZA_NETZWERK=1 aktiviert Buero-Modus)
set NETZWERK=0
for /f "tokens=1,* delims==" %%a in ('type "apps\backend\.env" ^| findstr /i "AILIZA_NETZWERK"') do (
    if /i "%%b"=="1" set NETZWERK=1
    if /i "%%b"=="true" set NETZWERK=1
)

if "%NETZWERK%"=="1" (
    echo  BUERO-MODUS: Alle im gleichen WLAN koennen AILIZA nutzen.
    echo  Lokale Adresse:  http://127.0.0.1:8001/dashboard
    echo  Netzwerkadresse: http://%LAN_IP%:8001/dashboard
    echo  ^(Diese Adresse an Ihre Kollegen weitergeben^)
    echo.
    start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8001/dashboard"
    "%PYTHON%" -m uvicorn apps.backend.main:app --port 8001 --host 0.0.0.0
) else (
    echo  AILIZA laeuft auf: http://127.0.0.1:8001/dashboard
    echo  Browser oeffnet sich gleich...
    echo  Tipp: AILIZA_NETZWERK=1 in .env aktiviert den Buero-Modus fuer alle Kollegen.
    echo.
    start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8001/dashboard"
    "%PYTHON%" -m uvicorn apps.backend.main:app --port 8001 --host 127.0.0.1
)

echo.
echo  AILIZA wurde beendet.
pause
