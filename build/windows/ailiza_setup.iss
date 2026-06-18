; © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
; Inno Setup Script — AILIZA Windows Installer
; Kompilieren: iscc build\windows\ailiza_setup.iss

#define AppName      "AILIZA"
#define AppVersion   "0.3.0"
#define AppPublisher "Karola Fromm-Nasreldin"
#define AppURL       "https://ailiza.de"
#define AppExeName   "AILIZA.exe"

[Setup]
AppId={{A1129AB5-8F23-4E7B-B2C1-AILIZA000001}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\AILIZA
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=..\..\build\output
OutputBaseFilename=AILIZA-Setup
SetupIconFile=..\..\ailiza.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardSmallImageFile=..\..\ailiza.ico
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\AILIZA.exe
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "Desktop-Symbol erstellen"; GroupDescription: "Weitere Symbole:"; Flags: checked
Name: "autostart";   Description: "AILIZA automatisch beim Windows-Start öffnen"; GroupDescription: "Autostart:"; Flags: unchecked

[Files]
Source: "..\..\dist\AILIZA\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\ailiza.ico";    DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\ailiza.ico"
Name: "{autodesktop}\{#AppName}";  Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\ailiza.ico"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "AILIZA"; ValueData: """{app}\{#AppExeName}"""; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\{#AppExeName}"; Description: "AILIZA jetzt starten"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill"; Parameters: "/f /im AILIZA.exe"; Flags: runhidden; RunOnceId: "KillAILIZA"

[Code]
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel2.Caption :=
    'AILIZA ist Ihr EU-konformer KI-Assistent für den Büroalltag.' + #13#10 + #13#10 +
    'Nach der Installation starten Sie AILIZA per Doppelklick auf das Desktop-Symbol.' + #13#10 +
    'Beim ersten Start führt ein Einrichtungs-Assistent Sie durch die Konfiguration.';
end;
