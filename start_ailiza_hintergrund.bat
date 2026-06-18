@echo off
:: AILIZA Hintergrund-Starter — wird automatisch beim Windows-Login ausgefuehrt.
:: Kein Fenster sichtbar. AILIZA laeuft im Hintergrund auf Port 8001.
:: Zum Beenden: Task-Manager → Python-Prozess beenden.

cd /d "%~dp0"
set PYTHONPATH=%~dp0

:: Kurz warten bis Netzwerk verfuegbar ist
timeout /t 8 /nobreak >nul

:: Modus aus .env lesen
set NETZWERK=0
for /f "tokens=1,* delims==" %%a in ('type "apps\backend\.env" ^| findstr /i "AILIZA_NETZWERK"') do (
    if /i "%%b"=="1" set NETZWERK=1
    if /i "%%b"=="true" set NETZWERK=1
)

if "%NETZWERK%"=="1" (
    start /min "" python -m uvicorn apps.backend.main:app --port 8001 --host 0.0.0.0
) else (
    start /min "" python -m uvicorn apps.backend.main:app --port 8001 --host 127.0.0.1
)
