#ifndef BuildRoot
  #define BuildRoot SourcePath + "..\build"
#endif
#ifndef OutputRoot
  #define OutputRoot SourcePath + "..\dist"
#endif
#ifndef SourceArchive
  #define SourceArchive BuildRoot + "\SonosDial-Source-1.2.0.zip"
#endif
#ifndef LegalRoot
  #define LegalRoot SourcePath + "..\licenses"
#endif
[Setup]
#ifdef IsolatedTest
AppId={{DD8B30EA-F342-4360-9DA4-70BE86BA6BBF}
#else
AppId={{8C993A74-E394-4D7E-9C70-E8CE931FF511}
#endif
AppName=SonosDial
AppVersion=1.2.0
AppPublisher=SonosDial
DefaultDirName={localappdata}\Programs\SonosDial-Mini-USB
DefaultGroupName=SonosDial
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputBaseFilename=SonosDial-Setup-1.2.0-Windows
OutputDir={#OutputRoot}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
LicenseFile=..\licenses\GPL-3.0.txt
UninstallDisplayIcon={app}\SonosDial.exe
SetupLogging=yes
SetupIconFile=..\assets\sonosdial.ico
WizardSmallImageFile=..\assets\installer-small.bmp
ShowLanguageDialog=yes
LanguageDetectionMethod=uilanguage

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[CustomMessages]
english.ShortcutName=SonosDial Setup
german.ShortcutName=SonosDial einrichten
english.DesktopShortcut=Create a &desktop shortcut
german.DesktopShortcut=Verknüpfung auf dem &Desktop erstellen
english.Shortcuts=Shortcuts:
german.Shortcuts=Verknüpfungen:
english.LaunchApp=Launch SonosDial Setup
german.LaunchApp=SonosDial-Einrichtung starten

[Files]
Source: "{#BuildRoot}\app\SonosDial\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourceArchive}"; DestDir: "{app}\Sources"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "..\THIRD-PARTY-NOTICES.md"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "..\tools\README.md"; DestDir: "{app}\Documentation"; DestName: "BUILDING.md"; Flags: ignoreversion
Source: "INSTALLER-ANLEITUNG.md"; DestDir: "{app}\Documentation"; Flags: ignoreversion
Source: "{#LegalRoot}\*"; DestDir: "{app}\Licenses"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "..\tests\README.md"; DestDir: "{app}\Documentation"; DestName: "TESTING.md"; Flags: ignoreversion

[Icons]
Name: "{group}\{cm:ShortcutName}"; Filename: "{app}\SonosDial.exe"
Name: "{autodesktop}\{cm:ShortcutName}"; Filename: "{app}\SonosDial.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; GroupDescription: "{cm:Shortcuts}"

[Run]
Filename: "{app}\SonosDial.exe"; Parameters: "--lang {language}"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent
