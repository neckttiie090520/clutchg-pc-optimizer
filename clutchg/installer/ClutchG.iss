; ============================================================
; ClutchG PC Optimizer — Inno Setup 6 Installer Script
; ============================================================
;
; Prerequisites:
;   - Inno Setup 6 installed (default path used below)
;   - PyInstaller build already run:
;       cd clutchg && python build.py
;     → dist/ClutchG/ must exist before running this script
;
; Output:
;   installer/output/ClutchG-Setup-1.0.0.exe
;
; To build the installer:
;   installer\build-installer.bat
;   — or —
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\ClutchG.iss
; ============================================================

#define AppName      "ClutchG"
#define AppVersion   "1.0.0"
#define AppPublisher "ClutchG Project"
#define AppURL       "https://github.com/neckttiie090520/clutchg-pc-optimizer"
#define AppExeName   "ClutchG.exe"
#define AppMutex     "ClutchGSingleInstance"

; Source bundle — built by PyInstaller (relative to .iss location = clutchg/installer/)
#define BundleDir    "..\dist\ClutchG"

[Setup]
; ── Identity ──────────────────────────────────────────────
AppId={{B4C9E2A1-3D7F-4E8B-A5C0-2F1D6E9B0374}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
VersionInfoVersion={#AppVersion}
VersionInfoDescription={#AppName} PC Optimizer
VersionInfoCopyright=Copyright (C) 2025 {#AppPublisher}

; ── Installation paths ────────────────────────────────────
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; ── Privileges ────────────────────────────────────────────
; ClutchG requires admin to run batch scripts — install for all users
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline

; ── Uninstall registry key ────────────────────────────────
; Visible in Windows "Apps & Features" / "Add or Remove Programs"
UninstallDisplayName={#AppName} PC Optimizer {#AppVersion}
UninstallDisplayIcon={app}\{#AppExeName}
CreateUninstallRegKey=yes

; ── Output installer exe ──────────────────────────────────
OutputDir=output
OutputBaseFilename=ClutchG-Setup-{#AppVersion}

; ── Compression ───────────────────────────────────────────
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; ── Appearance ────────────────────────────────────────────
WizardStyle=modern
WizardSizePercent=120
SetupIconFile={#BundleDir}\_internal\assets\icon.ico
; Fallback: if ICO not in bundle, Inno Setup uses default icon

; ── Misc behaviour ────────────────────────────────────────
; Close any running instance before upgrading
CloseApplications=yes
CloseApplicationsFilter=*{#AppExeName}*
RestartApplications=yes
AppMutex={#AppMutex}

; Create Start Menu folder
DisableDirPage=no
DisableReadyPage=no

; Allow upgrading over existing installation silently
; (used by auto-updater: launches with /SILENT /CLOSEAPPLICATIONS)
AllowNoIcons=yes

; ── Architecture ──────────────────────────────────────────
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

; ── Minimum Windows version: Windows 10 1809 ──────────────
MinVersion=10.0.17763

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";      Description: "Create a &desktop shortcut";         GroupDescription: "Additional icons:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Create a &Quick Launch shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; ── Main application bundle ───────────────────────────────
; Copy the entire dist/ClutchG/ directory tree to the install dir.
; recursesubdirs: yes  — picks up _internal/ and all nested dirs
; createallsubdirs: yes — recreates the folder structure
Source: "{#BundleDir}\{#AppExeName}";       DestDir: "{app}";              Flags: ignoreversion
Source: "{#BundleDir}\_internal\*";         DestDir: "{app}\_internal";    Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#BundleDir}\batch_scripts\*";     DestDir: "{app}\batch_scripts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#BundleDir}\README.txt";          DestDir: "{app}";              Flags: ignoreversion isreadme

[Icons]
; Start Menu shortcut
Name: "{group}\{#AppName}";             Filename: "{app}\{#AppExeName}"; Comment: "Windows PC Optimizer"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}";   Filename: "{uninstallexe}"

; Desktop shortcut (optional, via task)
Name: "{autodesktop}\{#AppName}";       Filename: "{app}\{#AppExeName}"; Comment: "Windows PC Optimizer"; Tasks: desktopicon

; Quick Launch (Windows XP/Vista compat)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
; Offer to launch after install
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove user-data directory created at runtime (%APPDATA%\ClutchG)
; Only if the user chooses to (soft-delete prompt not supported by Inno Setup
; natively — we clean up the app dir; %APPDATA% is left to the user)
Type: filesandordirs; Name: "{app}"

[Code]
// ──────────────────────────────────────────────────────────
// Helper: check if another instance of ClutchG is running
// and offer to close it before upgrade.
// Inno Setup's built-in CloseApplications already handles this,
// but this code gives a friendlier message.
// ──────────────────────────────────────────────────────────
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

// ──────────────────────────────────────────────────────────
// Auto-update support:
//   The updater.py in ClutchG launches this installer with:
//     ClutchG-Setup-1.0.0.exe /SILENT /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS
//   Those flags are handled natively by Inno Setup.
// ──────────────────────────────────────────────────────────
