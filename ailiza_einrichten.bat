@echo off
chcp 65001 >nul 2>&1
title AILIZA Einrichten

cd /d "%~dp0"
set PYTHONPATH=%~dp0
set ROOT=%~dp0

echo.
echo  *** AILIZA - Desktop-App einrichten ***
echo.

:: Pakete installieren (braucht pystray + Pillow)
echo  Installiere Pakete...
python -m pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    echo  FEHLER: Pakete konnten nicht installiert werden.
    pause
    exit /b 1
)
echo  Pakete OK.
echo.

:: Icon als .ico generieren
echo  Erstelle Icon...
python -c "
import sys, os
sys.path.insert(0, r'%ROOT%')
os.chdir(r'%ROOT%')
exec(open('ailiza_app.pyw').read().split('if __name__')[0])
_icon_als_ico_speichern(__import__('pathlib').Path('ailiza.ico'))
print('  ailiza.ico erstellt.')
"
if not exist "ailiza.ico" (
    echo  Hinweis: Icon konnte nicht erstellt werden — Verknuepfung ohne Icon.
)
echo.

:: Desktop-Verknuepfung erstellen
echo  Erstelle Desktop-Verknuepfung...
powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $lnk = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\AILIZA.lnk'); ^
   $lnk.TargetPath = (Get-Command pythonw -ErrorAction SilentlyContinue).Source; ^
   if (-not $lnk.TargetPath) { $lnk.TargetPath = 'pythonw.exe' }; ^
   $lnk.Arguments = '\"' + '%ROOT%ailiza_app.pyw' + '\"'; ^
   $lnk.WorkingDirectory = '%ROOT%'; ^
   $lnk.Description = 'AILIZA KI-Assistent starten'; ^
   if (Test-Path '%ROOT%ailiza.ico') { $lnk.IconLocation = '%ROOT%ailiza.ico' }; ^
   $lnk.Save()"

if errorlevel 1 (
    echo  Verknuepfung konnte nicht erstellt werden.
) else (
    echo  Desktop-Verknuepfung 'AILIZA' erstellt.
)
echo.

:: Autostart per Task Scheduler aktualisieren (auf neue .pyw umstellen)
schtasks /delete /tn "AILIZA" /f >nul 2>&1
powershell -NoProfile -Command ^
  "$pythonw = (Get-Command pythonw -ErrorAction SilentlyContinue).Source; ^
   if (-not $pythonw) { $pythonw = 'pythonw.exe' }; ^
   schtasks /create /tn 'AILIZA' /tr ('\"' + $pythonw + '\" \"' + '%ROOT%ailiza_app.pyw' + '\"') /sc onlogon /rl limited /f" >nul 2>&1

if not errorlevel 1 (
    echo  Autostart eingerichtet: AILIZA startet automatisch beim Einloggen.
) else (
    echo  Autostart konnte nicht eingerichtet werden ^(optional^).
)
echo.

echo  ============================================================
echo   Fertig! So nutzen Sie AILIZA:
echo.
echo   Doppelklick auf das AILIZA-Icon auf dem Desktop
echo   AILIZA erscheint als gruenes Icon in der Taskleiste (rechts unten)
echo   Ein Klick auf das Icon oeffnet AILIZA im Browser
echo  ============================================================
echo.
pause
