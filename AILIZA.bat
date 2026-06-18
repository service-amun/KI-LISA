@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
set ROOT=%~dp0
set PYTHON=%ROOT%_python\python.exe
set PYTHONW=%ROOT%_python\pythonw.exe

:: ── Bereits eingerichtet? Direkt starten ────────────────────────────────────
if exist "%PYTHONW%" goto :STARTEN

:: ── Einmalige Einrichtung (nur beim allerersten Start) ──────────────────────
title AILIZA — Einmalige Einrichtung
mode con cols=60 lines=20
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   AILIZA — Einmalige Einrichtung                    ║
echo  ║                                                      ║
echo  ║   Bitte warten — dauert ca. 2-3 Minuten.            ║
echo  ║   Dieses Fenster schließt sich danach automatisch.  ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
echo  Schritt 1 von 3: Python wird heruntergeladen ...
echo  (ca. 25 MB — nur einmalig)
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop';" ^
  "$root = '%ROOT%';" ^
  "$pyDir = $root + '_python';" ^
  "$pyVer = '3.12.9';" ^
  "$pyUrl = 'https://www.python.org/ftp/python/' + $pyVer + '/python-' + $pyVer + '-embed-amd64.zip';" ^
  "$pipUrl = 'https://bootstrap.pypa.io/get-pip.py';" ^
  "$pyZip  = $env:TEMP + '\ailiza_py.zip';" ^
  "$getPip = $env:TEMP + '\get-pip.py';" ^
  "try {" ^
  "  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
  "  Write-Host '  Lade Python ...' -ForegroundColor Cyan;" ^
  "  (New-Object Net.WebClient).DownloadFile($pyUrl, $pyZip);" ^
  "  Write-Host '  Entpacke ...' -ForegroundColor Cyan;" ^
  "  Expand-Archive -Path $pyZip -DestinationPath $pyDir -Force;" ^
  "  Remove-Item $pyZip -Force;" ^
  "  $pth = Get-ChildItem $pyDir -Filter 'python*._pth' | Select -First 1;" ^
  "  if ($pth) { (Get-Content $pth.FullName) -replace '#import site','import site' | Set-Content $pth.FullName }" ^
  "  (New-Object Net.WebClient).DownloadFile($pipUrl, $getPip);" ^
  "  & ($pyDir + '\python.exe') $getPip --no-warn-script-location -q;" ^
  "  Remove-Item $getPip -Force;" ^
  "  Write-Host '  Python OK.' -ForegroundColor Green;" ^
  "} catch { Write-Host ('FEHLER: ' + $_.Exception.Message) -ForegroundColor Red; exit 1 }"

if errorlevel 1 (
    echo.
    echo  *** FEHLER beim Herunterladen von Python ***
    echo  Bitte Internetverbindung pruefen und erneut starten.
    echo.
    pause
    exit /b 1
)

echo.
echo  Schritt 2 von 3: Pakete werden installiert ...
echo.

set PYTHONPATH=%ROOT%
"%ROOT%_python\python.exe" -m pip install -r "%ROOT%requirements-desktop.txt" -q --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo  *** FEHLER beim Installieren der Pakete ***
    echo  Bitte Internetverbindung pruefen und erneut starten.
    echo.
    pause
    exit /b 1
)

echo.
echo  Schritt 3 von 3: Desktop-Symbol wird erstellt ...
echo.

:: Icon erzeugen
"%ROOT%_python\python.exe" -c "import sys,os; sys.path.insert(0,r'%ROOT%'); os.chdir(r'%ROOT%'); exec(open('ailiza_app.pyw').read().split('if __name__')[0]); _icon_als_ico_speichern(__import__('pathlib').Path('ailiza.ico'))" >nul 2>&1

:: Desktop-Verknuepfung
powershell -NoProfile -Command ^
  "$ws  = New-Object -ComObject WScript.Shell;" ^
  "$lnk = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\AILIZA.lnk');" ^
  "$lnk.TargetPath      = '%ROOT%AILIZA.bat';" ^
  "$lnk.WorkingDirectory= '%ROOT%';" ^
  "$lnk.Description     = 'AILIZA KI-Assistent starten';" ^
  "if (Test-Path '%ROOT%ailiza.ico') { $lnk.IconLocation = '%ROOT%ailiza.ico' };" ^
  "$lnk.Save()" >nul 2>&1

:: Autostart (optional)
schtasks /delete /tn "AILIZA" /f >nul 2>&1
schtasks /create /tn "AILIZA" /tr "\"%ROOT%AILIZA.bat\"" /sc onlogon /rl limited /f >nul 2>&1

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   Einrichtung abgeschlossen!                        ║
echo  ║                                                      ║
echo  ║   AILIZA startet jetzt zum ersten Mal.              ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
timeout /t 2 /nobreak >nul

:: ── AILIZA starten ────────────────────────────────────────────────────────────
:STARTEN
title AILIZA
set PYTHONPATH=%ROOT%
start "" "%ROOT%_python\pythonw.exe" "%ROOT%ailiza_app.pyw"
