#define AppName "WA Desktop Connector"
#define AppVersion "1.0.0"
#define AppExe "WA Desktop Connector.exe"
[Setup]
SetupIconFile=..\assets\wa_desktop_connector.ico
AppId={{6F03A20C-BE15-4F96-94DC-4196C8C9B7E8}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\WA Desktop Connector
DefaultGroupName=WA Desktop Connector
OutputDir=..\dist
OutputBaseFilename=WA_Desktop_Connector_Setup_{#AppVersion}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\wa_desktop_connector.ico
[Files]
Source: "..\assets\wa_desktop_connector.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\WA Desktop Connector\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Registry]
Root: HKCU; Subkey: "Software\Classes\wa"; ValueType: string; ValueName: ""; ValueData: "URL:WA Desktop Connector"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\wa"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\wa\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExe}"" ""%1"""
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "WA Desktop Connector"; ValueData: """{app}\{#AppExe}"""; Flags: uninsdeletevalue
[Icons]
Name: "{group}\WA Desktop Connector"; Filename: "{app}\{#AppExe}"
Name: "{userdesktop}\WA Desktop Connector"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
[Run]
Filename: "{app}\{#AppExe}"; Parameters: "--install-protocol"; Flags: runhidden waituntilterminated
