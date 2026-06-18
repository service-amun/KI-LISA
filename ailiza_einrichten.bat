@echo off
chcp 65001 >nul 2>&1
title AILIZA Einrichten
cd /d "%~dp0"
set ROOT=%~dp0
set PYTHONPATH=%ROOT%

:: Gebündeltes Python bevorzugen, sonst System-Python
if exist "%ROOT%_python\python.exe" (
    set PYTHON=%ROOT%_python\python.exe
    set PYTHONW=%ROOT%_python\pythonw.exe
) else (
    set PYTHON=python
    set PYTHONW=pythonw
)

echo.
echo  *** AILIZA - Desktop-App einrichten ***
echo.

:: Pakete installieren
echo  Installiere Pakete...
"%PYTHON%" -m pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    echo  FEHLER: Pakete konnten nicht installiert werden.
    pause
    exit /b 1
)
echo  Pakete OK.
echo.

:: Icon als .ico generieren
echo  Erstelle Icon...
"%PYTHON%" -c "import sys, os; sys.path.insert(0, r'%ROOT%'); os.chdir(r'%ROOT%'); exec(open('ailiza_app.pyw').read().split('if __name__')[0]); _icon_als_ico_speichern(__import__('pathlib').Path('ailiza.ico'))" >nul 2>&1
if not exist "ailiza.ico" (
    echo  Hinweis: Icon konnte nicht erstellt werden.
)
echo.

:: Desktop-Verknuepfung auf AILIZA.bat zeigen
echo  Erstelle Desktop-Verknuepfung...
powershell -NoProfile -Command ^
  "$ws  = New-Object -ComObject WScript.Shell;" ^
  "$lnk = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\AILIZA.lnk');" ^
  "$lnk.TargetPath      = '%ROOT%AILIZA.bat';" ^
  "$lnk.WorkingDirectory= '%ROOT%';" ^
  "$lnk.Description     = 'AILIZA KI-Assistent starten';" ^
  "if (Test-Path '%ROOT%ailiza.ico') { $lnk.IconLocation = '%ROOT%ailiza.ico' };" ^
  "$lnk.Save()"

if errorlevel 1 (
    echo  Verknuepfung konnte nicht erstellt werden.
) else (
    echo  Desktop-Verknuepfung 'AILIZA' erstellt.
)
echo.

:: Autostart
schtasks /delete /tn "AILIZA" /f >nul 2>&1
schtasks /create /tn "AILIZA" /tr "\"%ROOT%AILIZA.bat\"" /sc onlogon /rl limited /f >nul 2>&1
if not errorlevel 1 (
    echo  Autostart eingerichtet.
) else (
    echo  Autostart konnte nicht eingerichtet werden (optional).
)
echo.

echo  ============================================================
echo   Fertig! Doppelklick auf das AILIZA-Icon auf dem Desktop.
echo  ============================================================
echo.
pause
