@echo off
chcp 65001 >nul 2>&1
title AILIZA DPIA-Update einrichten

cd /d "%~dp0"
set ROOT=%~dp0
set PYTHON=python
set SKRIPT=%ROOT%apps\backend\compliance\dpia_updater.py

echo.
echo  *** AILIZA — Monatlicher DPIA-Rechtsupdater einrichten ***
echo.

:: Prüfen ob Python verfügbar
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo  FEHLER: Python nicht gefunden. Bitte Python installieren.
    pause
    exit /b 1
)

:: Einmalig sofort ausführen um Basis-Stand zu speichern
echo  Erstprüfung läuft (speichert aktuellen Gesetzesstand) ...
%PYTHON% "%SKRIPT%"
echo  Erstprüfung abgeschlossen.
echo.

:: Task Scheduler: monatlich am 1. des Monats um 08:00 Uhr
echo  Richte monatliche Aufgabe im Windows Task-Planer ein ...

schtasks /delete /tn "AILIZA-DPIA-Update" /f >nul 2>&1

powershell -NoProfile -Command ^
  "$python = (Get-Command python -ErrorAction SilentlyContinue).Source; ^
   if (-not $python) { $python = 'python.exe' }; ^
   schtasks /create /tn 'AILIZA-DPIA-Update' ^
     /tr ('\"' + $python + '\" \"' + '%ROOT%apps\backend\compliance\dpia_updater.py' + '\"') ^
     /sc monthly /d 1 /st 08:00 /rl limited /f" >nul 2>&1

if errorlevel 1 (
    echo  Task-Planer konnte nicht eingerichtet werden.
    echo  Bitte monatlich manuell ausfuehren:
    echo  python "%SKRIPT%"
) else (
    echo  Aufgabe eingerichtet: laeuft automatisch am 1. jeden Monats um 08:00.
)
echo.

:: Bericht anzeigen
echo  Letzter Bericht:
for /f "tokens=*" %%f in ('dir /b /od "%ROOT%docs\DPIA_updates\*.md" 2^>nul') do set LETZTER=%%f
if defined LETZTER (
    echo  docs\DPIA_updates\%LETZTER%
) else (
    echo  (noch kein Bericht vorhanden)
)
echo.

echo  ============================================================
echo   DPIA-Updater eingerichtet. Was passiert jeden 1. des Monats:
echo.
echo   1. Alle relevanten Gesetze werden auf Aenderungen geprueft
echo      (DSGVO, EU AI Act, BDSG, DDG, TDDDG)
echo   2. Ein Bericht wird in docs\DPIA_updates\ gespeichert
echo   3. Bei Aenderungen: DPIA-Datei wird mit neuem Datum versehen
echo   4. Sie erhalten einen Hinweis zum manuellen Nacharbeiten
echo  ============================================================
echo.
pause
