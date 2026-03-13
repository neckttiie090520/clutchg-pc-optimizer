# Windows-Tweaks Analysis

> **Repository:** [github.com/kubsonxtm/Windows-Tweaks](https://github.com/kubsonxtm/Windows-Tweaks)
> **Primary Focus:** Gaming Performance & Privacy
> **Platform:** Windows 10/11 Pro
> **Language:** PowerShell (.ps1), Batch (.bat), Registry (.reg)
> **Last Updated:** 2024

## Overview

Windows-Tweaks is a comprehensive Windows optimization repository created by kubsonxtm that focuses on reducing gaming latency and minimizing performance drops. The collection includes driver installation scripts, bloatware removal, power plan optimization, and privacy enhancements through registry tweaks.

**Warning:** This repository contains scripts that permanently remove system components, modify critical power settings, and disable important Windows services without adequate safety checks or rollback mechanisms.

## Primary Goals

1. **Gaming Performance** - Optimize system settings for reduced latency and maximum FPS
2. **Driver Installation** - Automated installation of Visual C++, DirectX, and LAN drivers
3. **System Debloating** - Remove Windows Store apps and built-in components
4. **Privacy Enhancement** - Disable telemetry and data collection
5. **Power Optimization** - Configure aggressive power settings for maximum performance

## Repository Structure

```
Windows-Tweaks/
├── 1 Enable powershell scripts.cmd (17 lines)
├── 2 Drivers/
│   ├── C++.ps1 (145 lines) - Visual C++ Redistributables installer
│   ├── DirectX.ps1 (109 lines) - DirectX June 2010 installer
│   └── Lan Driver.ps1 (19 lines) - Opens Google search for motherboard drivers
├── 3 Automation/
│   ├── 7-Zip/7-Zip.ps1 (89 lines)
│   ├── Debloat Windows Apps/
│   │   ├── Debloat (all)/Debloat all Windows Apps.ps1 (186 lines)
│   │   ├── Debloat (keep some apps)/Debloat Windows Apps but keep daily use.ps1 (183 lines)
│   │   ├── Uninstall Microsoft Edge/Edge Uninstall.bat (179 lines) ⚠️ DANGEROUS
│   │   └── Uninstall OneDrive/Uninstall OneDrive.bat (149 lines) ⚠️ DANGEROUS
│   ├── Hardened Firefox/
│   │   ├── Hardened Firefox.ps1 (99 lines)
│   │   └── After Installing/Enable|Disable Firefox Telemetry.bat
│   └── Spotify (without ads)/Spotify.ps1 (1 line)
├── 4 Windows Tweaks/Additional/
│   ├── This PC user folders/*.reg
│   └── Windows 11/*.reg (File Explorer navigation tweaks)
├── 5 Programs to tweak or increase privacy/
│   ├── 1 CTT/ (Chris Titus Tool integration)
│   ├── 2 Powerplan/
│   │   ├── Power plan.ps1 (175 lines) ⚠️ DANGEROUS
│   │   └── Restore Power Plan.ps1
│   ├── 3 Registry/Registry.reg (894 lines)
│   ├── 4 O&O Shutup/O&O ShutUp.ps1
│   └── 7 Privacy.sexy/privacy-script.bat
├── 6 Cleaning/Uninstall Tool/App/
└── 7 BIOS/Reboot to Bios.bat (3 lines)
```

## Script Analysis

### 1. Enable powershell scripts.cmd

**Purpose:** Configure PowerShell execution policy to "Unrestricted" and unblock all downloaded scripts

**Key Commands:**
```batch
reg add "HKCR\Applications\powershell.exe\shell\open\command" /ve /t REG_SZ /d "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -ExecutionPolicy unrestricted -File \"%%1\"" /f
reg add "HKCU\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell" /v "ExecutionPolicy" /t REG_SZ /d "Unrestricted" /f
reg add "HKLM\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell" /v "ExecutionPolicy" /t REG_SZ /d "Unrestricted" /f
powershell -Command "Get-ChildItem -Path '%~dp0' -Recurse | Unblock-File"
```

**Risk Level:** 🔴 **CRITICAL SECURITY RISK**
- Sets execution policy to "Unrestricted" system-wide
- Removes all security protections from PowerShell scripts
- Allows any script to run without user confirmation
- Creates permanent security vulnerability

**Effectiveness:** Achieves stated goal but with dangerous methods

**Quality Notes:** No warnings about security implications, assumes all scripts are safe

---

### 2. Drivers/C++.ps1

**Purpose:** Download and install all Visual C++ Redistributables from 2005 to 2022

**Key Commands:**
```powershell
# Downloads from official Microsoft sources
$vcredistList = @(
    @{version = "2005"; urlX86 = "https://download.microsoft.com/..."; urlX64 = "..."},
    @{version = "2008"; ...},
    @{version = "2010"; ...},
    @{version = "2012"; ...},
    @{version = "2013"; ...},
    @{version = "2015_2017_2019_2022"; ...}
)

foreach ($vcredist in $vcredistList) {
    if (Is-VCRedistInstalled $vcredist.version) {
        Write-Host "Already installed"
    } else {
        Install-VCRedist $vcredist.urlX86 $vcredist.urlX64 $vcredist.version
    }
}
```

**Risk Level:** ⚠️ MODERATE
- Downloads executables from internet without hash verification
- Installs software silently (`/q` flag) with no user confirmation
- Uses official Microsoft sources (reduces risk)
- No cleanup of temporary files if installation fails

**Effectiveness:** High - correctly checks existing installations and installs missing versions

**Quality Notes:**
- Good custom download function with progress bar
- Properly checks for existing installations before downloading
- Missing hash verification for downloaded files
- Uses `Get-WmiObject` which is deprecated (should use `Get-CimInstance`)

---

### 3. Drivers/DirectX.ps1

**Purpose:** Install DirectX June 2010 redistributable

**Key Commands:**
```powershell
# Check if already installed
$directXFilePath = "$env:SystemRoot\System32\d3dx11_43.dll"
if (Test-Path $directXFilePath) {
    [System.Windows.Forms.MessageBox]::Show("DirectX is already installed. Install anyway?")
}

# Download DirectX
Get-FileFromWeb -URL "https://download.microsoft.com/download/8/4/A/84A35BF1-DAFE-4AE8-82AF-AD2AE20B6B14/directx_Jun2010_redist.exe"

# Download and install 7-Zip to extract DirectX installer
Get-FileFromWeb -URL "https://www.7-zip.org/a/7z2301-x64.exe"
Start-Process -wait "$env:TEMP\7-Zip.exe" /S

# Extract using 7-Zip and install
cmd /c "C:\Program Files\7-Zip\7z.exe" x "$env:TEMP\DirectX.exe" -o"$env:TEMP\DirectX" -y
Start-Process "$env:TEMP\DirectX\DXSETUP.exe"
```

**Risk Level:** ⚠️ MODERATE
- Downloads without hash verification
- Installs 7-Zip without user consent
- Installs 7-Zip to fixed path (may fail if already installed elsewhere)
- No cleanup of downloaded files

**Effectiveness:** Low - DirectX June 2010 is obsolete for modern games
- Most modern games use DirectX 11/12 included with Windows 10/11
- This legacy DirectX 9 installer is only needed for very old games
- Windows 10/11 already includes DirectX 11/12 runtimes

**Quality Notes:**
- Poor approach - using legacy installer for modern systems
- Downloads 7-Zip unnecessarily (Windows has built-in extraction)
- Hardcoded 7-Zip path assumptions

---

### 4. Drivers/Lan Driver.ps1

**Purpose:** Open Google Search for motherboard drivers

**Key Commands:**
```powershell
$motherboard = Get-WmiObject Win32_BaseBoard | Select-Object -ExpandProperty Product
$searchUrl = "https://www.google.com/search?q=$motherboard"
Start-Process $searchUrl
```

**Risk Level:** ✅ SAFE
- Only opens a web browser
- No system modifications

**Effectiveness:** Low - could be more helpful
- Could automate driver download process
- Doesn't identify the actual network adapter
- User must manually find and download drivers

**Quality Notes:** Too simplistic to be genuinely useful

---

### 5. Automation/Debloat Windows Apps/Debloat all Windows Apps.ps1

**Purpose:** Remove ALL Windows Store apps including system utilities

**Key Commands:**
```powershell
$Bloatware = @(
    "Microsoft.3DBuilder", "Microsoft.BingFinance", "Microsoft.BingNews",
    "Microsoft.BingWeather", "Microsoft.Copilot", "Microsoft.Getstarted",
    "Microsoft.WindowsCalculator", "Microsoft.WindowsPhotos",
    "Microsoft.WindowsTerminal", "Microsoft.WindowsCamera",
    # ... 139 total apps ...
)

foreach ($app in $Bloatware) {
    $packages = Get-AppxPackage -Name $app -AllUsers
    Remove-AppxPackage -Package $pkg.PackageFullName

    $provisioned = Get-AppxProvisionedPackage -Online | Where-Object { $_.DisplayName -like $app }
    Remove-AppxProvisionedPackage -Online -PackageName $pkg.PackageName
}

Stop-Process -Name explorer -Force
Start-Sleep -Seconds 3
Start-Process explorer.exe
```

**Risk Level:** 🔴 **HIGH RISK**
- Removes 139 apps without distinction between bloat and useful utilities
- **Removes Windows Calculator** - essential utility
- **Removes Windows Terminal** - modern terminal emulator
- **Removes Windows Camera** - breaks camera functionality
- **Removes Photos app** - default image viewer
- **Removes Snipping Tool** - screenshot functionality
- Kills explorer.exe forcefully - could cause data loss
- No confirmation or warning dialogs
- No backup/restore mechanism

**Effectiveness:** High at removing apps, but too aggressive
- Many removed apps are actually useful
- No selectivity between true bloat and utilities

**Quality Notes:**
- No categorization of apps (essential vs. bloat)
- Dangerous removal of core functionality
- Forcibly killing Explorer is poor practice
- The "Debloat (keep some apps)" version has identical code (copy-paste error?)

---

### 6. Automation/Debloat Windows Apps/Uninstall Microsoft Edge/Edge Uninstall.bat

**Purpose:** Completely remove Microsoft Edge browser from Windows

**Key Commands:**
```batch
:: Kill Edge processes
taskkill /f /t /im msedge.exe
taskkill /f /t /im MicrosoftEdgeUpdate.exe
taskkill /f /t /im msedgewebview2.exe

:: Delete Edge registry keys
reg delete "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge" /f
reg delete "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Microsoft Edge Update" /f
:: ... 10+ registry deletions ...

:: Stop and delete Edge services
net stop MicrosoftEdgeElevationService
sc delete MicrosoftEdgeElevationService
net stop edgeupdate
sc delete edgeupdate

:: Remove Edge directories
rd /s /q "%ProgramFiles(x86)%\Microsoft\Edge"
rd /s /q "%ProgramFiles(x86)%\Microsoft\EdgeCore"
rd /s /q "%ProgramFiles(x86)%\Microsoft\EdgeUpdate"
rd /s /q "%ProgramFiles(x86)%\Microsoft\EdgeWebView"

:: Remove Edge AppxPackages
for /f "delims=" %%a in ('powershell -Command "Get-AppxPackage -AllUsers | Where-Object { $_.PackageFullName -like '*microsoftedge*' } | Select-Object -ExpandProperty PackageFullName"') do (
    reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Appx\AppxAllUserStore\EndOfLife\!USER_SID!\!APP!" /f
    powershell -Command "Remove-AppxPackage -Package '!APP!' -AllUsers"
)

:: Remove SystemApps and System32 executables
for /f "delims=" %%f in ('dir /s /b %SystemRoot%\SystemApps\Microsoft.MicrosoftEdge*') do (
    takeown /f "%%f"
    icacls "%%f" /grant everyone:F
    del /f /q "%%f"
)

:: Remove from WindowsApps
set "basePath=C:\Program Files\WindowsApps"
for /d %%D in ("%basePath%\Microsoft.MicrosoftEdge.Stable_*") do (
    takeown /f "%%D" /r /d y
    icacls "%%D" /grant %username%:F /t
    rmdir /s /q "%%D"
)
```

**Risk Level:** 🔴 **CRITICAL - EXTREMELY DANGEROUS**
- **Breaks Windows 11** - Edge is integrated into the OS shell
- **Breaks WebView2** - Many apps depend on Edge WebView2 (Teams, Outlook, etc.)
- **Modifies protected system files** - Taking ownership of System32 files
- **Deletes WindowsApps packages** - Violates Windows integrity
- **Forces removal with takeown/icacls** - Bypasses security protections
- **Removes registry entries for file associations** - Breaks HTML/PDF viewing
- **Removes core OS components** - Edge is required for Windows features
- **No restore mechanism** - Cannot easily reinstall Edge
- **Windows Update will fail** - May try to reinstall Edge and cause conflicts
- **Intranet zones and security policies may break** - Edge manages these

**Effectiveness:** May superficially remove Edge but breaks system
- Windows will likely reinstall Edge via Windows Update
- System instability and broken features are guaranteed
- Web-based components in Windows will fail

**Quality Notes:**
- Extremely dangerous script with no safety checks
- No version detection (Windows 10 vs 11)
- No warning about consequences
- Should NEVER be run on Windows 11
- Even on Windows 10, causes significant problems

**Recommendation:** **DO NOT USE** - This script can permanently damage Windows installation

---

### 7. Automation/Debloat Windows Apps/Uninstall OneDrive/Uninstall OneDrive.bat

**Purpose:** Completely remove OneDrive cloud storage integration

**Key Commands:**
```batch
:: Kill OneDrive process
taskkill /f /im OneDrive.exe

:: Remove OneDrive from startup
PowerShell -Command "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'OneDrive'"

:: Uninstall OneDrive using official uninstaller
"%SYSTEMROOT%\System32\OneDriveSetup.exe" /uninstall

:: Check if user folders point to OneDrive before deletion
PowerShell -Command "Check if user shell folders point to OneDrive; if yes, skip deletion to protect data"

:: Remove OneDrive directories with permissions handling
PowerShell -Command "takeown /f '%LOCALAPPDATA%\Microsoft\OneDrive'; icacls ... /grant everyone:F; Remove-Item ..."

:: Remove OneDrive from File Explorer navigation pane
reg add "HKCU\Software\Classes\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}" /v "System.IsPinnedToNameSpaceTree" /t REG_DWORD /d 0

:: Disable OneDrive via group policy
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive" /v "DisableFileSyncNGSC" /t REG_DWORD /d 1

:: Disable OneDrive scheduled tasks
PowerShell -Command "Disable-ScheduledTask -TaskName 'OneDrive Reporting Task-*'"
```

**Risk Level:** ⚠️ MODERATE
- Removes cloud backup - user data could be lost if not synced
- Checks if folders point to OneDrive before deletion (good safety measure)
- Modifies user shell folder registry keys
- May break "Backup" settings in Windows Settings

**Effectiveness:** High - thorough OneDrive removal
- Properly uses official uninstaller
- Cleans up all OneDrive components
- Disables automatic reinstall

**Quality Notes:**
- **Excellent safety check** for shell folders before deletion
- Validates user data isn't accidentally deleted
- Comprehensive cleanup of all OneDrive traces
- Much better quality than the Edge uninstaller

---

### 8. Automation/Hardened Firefox/Hardened Firefox.ps1

**Purpose:** Download and apply Betterfox privacy configuration to Firefox

**Key Commands:**
```powershell
# Download Betterfox user.js from GitHub
$userJsUrl = "https://raw.githubusercontent.com/yokoffing/Betterfox/main/user.js"
$firefoxExePath = "C:\Program Files\Mozilla Firefox\firefox.exe"

# Get Firefox profile path
$profilesPath = "$env:APPDATA\Mozilla\Firefox\Profiles\"
$profileFolder = Get-ChildItem -Path $profilesPath | Where-Object { $_.PSIsContainer } | Select-Object -First 1

# Download and install user.js
Download-UserJsFile -url $userJsUrl -outputPath "$profilePath\user.js"

# Download uBlock Origin extension
$ublockXpiUrl = "https://github.com/gorhill/uBlock/releases/download/1.61.0/uBlock0_1.61.0.firefox.signed.xpi"
Download-XPIFile -url $ublockXpiUrl -outputPath "$env:TEMP\ublock_origin.xpi"

# Open Firefox for manual extension installation
Start-Process -FilePath $firefoxExePath -ArgumentList "--new-tab `"$xpiPath`""
```

**Risk Level:** ✅ LOW RISK
- Downloads from reputable GitHub repositories
- Only modifies Firefox profile settings
- User can manually review/remove changes
- No system modifications

**Effectiveness:** High - applies proven privacy configuration
- Betterfox is well-maintained privacy project
- uBlock Origin is excellent ad blocker
- Non-destructive approach

**Quality Notes:**
- Excellent approach - leverages existing privacy tools
- Forces Firefox close before modifying profile (good)
- Manual extension install is safer than automated
- Only works if Firefox installed in default location

---

### 9. Automation/Spotify (without ads)/Spotify.ps1

**Purpose:** Install SpotX ad-blocker for Spotify

**Key Commands:**
```powershell
iex "& { $(iwr -useb 'https://raw.githubusercontent.com/SpotX-Official/spotx-official.github.io/main/run.ps1') } -confirm_uninstall_ms_spoti -podcasts_off -block_update_on -new_theme -adsections_off"
```

**Risk Level:** ⚠️ MODERATE
- Downloads and executes script from internet without validation
- Modifies Spotify installation files
- Violates Spotify Terms of Service
- May break with Spotify updates
- Uses `iex` (Invoke-Expression) which is dangerous practice

**Effectiveness:** High at blocking ads, but...
- Not officially supported by Spotify
- Could stop working at any time
- May result in account termination

**Quality Notes:**
- Single line script - minimal functionality
- No error handling
- No version checking
- Dangerous use of `iex` without script review

---

### 10. 5 Programs to tweak or increase privacy/2 Powerplan/Power plan.ps1

**Purpose:** Create aggressive power plan for maximum performance at cost of battery life

**Key Commands:**
```powershell
# Duplicate "Ultimate Performance" power plan
cmd /c "powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 99999999-9999-9999-9999-999999999999"

# Set as active and DELETE all other power plans
$output = powercfg /L
foreach ($plan in $powerPlans) {
    cmd /c "powercfg /delete $plan"
}

# Disable hibernation completely
powercfg /hibernate off
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power" /v "HibernateEnabled" /t REG_DWORD /d 0

# Hide lock and sleep options from power menu
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Explorer\FlyoutMenuSettings" /v "ShowLockOption" /t REG_DWORD /d 0
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Explorer\FlyoutMenuSettings" /v "ShowSleepOption" /t REG_DWORD /d 0

# Disable fast startup
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v "HiberbootEnabled" /t REG_DWORD /d 0

# Unpark CPU cores
reg add "HKLM\SYSTEM\ControlSet001\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\0cc5b647-c1df-4637-891a-dec35c318583" /v "ValueMax" /t REG_DWORD /d 0

# Disable power throttling
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling" /v "PowerThrottlingOff" /t REG_DWORD /d 1

# Configure desktop power settings (AC power)
# Turn off hard disk: Never (0 minutes)
# Turn off display: Never (0 minutes)
# Sleep: Never (0 minutes)
# USB selective suspend: Disabled
# PCI Express power management: Off
# Minimum processor state: 100%
# Maximum processor state: 100%
# System cooling policy: Active
# Disable wake timers
# Disable hybrid sleep
# Disable hibernate

# Configure battery power settings (DC power)
# Same aggressive settings on battery!

# Battery warnings all disabled
# Critical battery notification: Off
# Critical battery action: Do nothing
# Low battery level: 0%
# Critical battery level: 0%
# Low battery notification: Off
# Battery saver: Never

# Graphics settings
# Intel Graphics: Maximum Performance
# AMD Power Slider: Best Performance
# ATI PowerPlay: Maximize Performance
# Switchable Graphics: Maximize Performance
```

**Risk Level:** 🔴 **CRITICAL - DANGEROUS FOR LAPTOPS**
- **Deletes ALL power plans** - loses user customization
- **Disables ALL battery warnings** - laptop will shut down without warning
- **Critical battery action = "Do nothing"** - data loss guaranteed
- **Aggressive settings on battery** - drains battery in minutes
- **Disables hibernation** - may lose data if battery dies
- **Disables fast startup** - slower boot times
- **No sleep option** - must fully shutdown laptop
- **No restore script automatically run** - user must manually run "Restore Power Plan.ps1"

**Effectiveness:** High for performance, terrible for battery life
- Desktop: Might improve gaming performance slightly
- Laptop: **Unusable on battery** - battery will drain in <30 minutes
- May reduce hardware lifespan (constant max performance)

**Quality Notes:**
- Extremely aggressive approach
- No detection of laptop vs desktop
- Should warn laptop users
- "Restore Power Plan.ps1" exists but isn't run automatically
- Using hardcoded GUID for power plan (works but hacky)

**Recommendation:** Only suitable for gaming desktops, NEVER use on laptops

---

### 11. 5 Programs to tweak or increase privacy/3 Registry/Registry.reg

**Purpose:** Comprehensive registry modifications for privacy, performance, and UX improvements

**Key Sections:**

**A. Search & Web (Lines 3-27):**
```reg
; Disable search highlights, safe search, cloud search, web search in start menu
; Disable search history
HKCU\Software\Microsoft\Windows\CurrentVersion\SearchSettings\IsDynamicSearchBoxEnabled = 0
HKCU\Software\Policies\Microsoft\Windows\Explorer\DisableSearchBoxSuggestions = 1
```
✅ Generally safe and effective

**B. UWP Apps & Updates (Lines 30-46):**
```reg
; Disable auto-update apps and maps
HKLM\SOFTWARE\Policies\Microsoft\WindowsStore\AutoDownload = 2
HKLM\SYSTEM\Maps\AutoUpdateEnabled = 0
; Disable widgets
HKLM\SOFTWARE\Microsoft\PolicyManager\default\NewsAndInterests\AllowNewsAndInterests = 0
```
✅ Safe - reduces bandwidth and background activity

**C. Sync & Typing (Lines 49-92):**
```reg
; Disable all settings sync (accessibility, apps, browser, credentials, themes, etc.)
; Disable autocorrect, spellchecking, text prediction
HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\*\Enabled = 0
HKCU\SOFTWARE\Microsoft\TabletTip\1.7\EnableAutocorrection = 0
HKCU\SOFTWARE\Microsoft\Input\Settings\InsightsEnabled = 0
```
✅ Good for privacy, but typing assistance may be missed

**D. Edge Tweaks (Lines 95-118):**
```reg
; Disable Edge startup boost, hardware acceleration, background mode
; Disable Edge update services
HKLM\SYSTEM\CurrentControlSet\Services\MicrosoftEdgeElevationService\Start = 4 (Disabled)
HKLM\SYSTEM\CurrentControlSet\Services\edgeupdate\Start = 4 (Disabled)
```
⚠️ May break Edge functionality and security updates

**E. Performance Tweaks (Lines 121-173):**
```reg
; Unpark CPU cores
; Disable power throttling
; Disable hibernation and fast boot
; Enable hardware accelerated GPU scheduling
; Set "Adjust for best performance of programs"
; Disable automatic maintenance
; Disable "Lazy Mode" for multimedia
; Set Games task to High priority
HKLM\SYSTEM\ControlSet001\Control\Power\PowerSettings\...\ValueMax = 0
HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling\PowerThrottlingOff = 1
HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\HwSchMode = 2
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games\GPU Priority = 8
```
✅ Generally effective for gaming performance
⚠️ Unparking all CPU cores may not help on modern CPUs
⚠️ Disabling hibernation affects fast startup

**F. Personalization (Lines 176-199):**
```reg
; Disable all content delivery, tips, suggestions, featured apps
; Disable Windows Spotlight
HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager\* = 0
```
✅ Excellent privacy improvements

**G. Xbox & Game Bar (Lines 202-255):**
```reg
; Disable Game DVR, Game Bar, Xbox features
; Enable Game Mode
HKCU\System\GameConfigStore\GameDVR_Enabled = 0
HKCU\Software\Microsoft\GameBar\AutoGameModeEnabled = 1
```
✅ Good for gaming - disables background recording

**H. Privacy Settings (Lines 258-378):**
```reg
; Disable location, contacts, calendar, phone calls, messaging, radios, diagnostics
; Disable handwriting data sharing, linguistic data collection, input personalization
; Disable advertising ID, feedback, activity history
; Disable delivery optimization, remote assistance
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\*\Value = "Deny"
```
✅ Comprehensive privacy hardening

**I. Services (Lines 433-465):**
```reg
; Disable Windows Search, Printing, SysMain (Superfetch), Error Reporting, Remote Registry, Diagnostics
HKLM\SYSTEM\CurrentControlSet\Services\WSearch\Start = 4
HKLM\SYSTEM\CurrentControlSet\Services\SysMain\Start = 4
HKLM\SYSTEM\CurrentControlSet\Services\WerSvc\Start = 4
```
⚠️ Disabling Windows Search breaks Start Menu search
⚠️ Disabling printing will break printer functionality
⚠️ Disabling SysMain may reduce app launch performance

**J. Additional Privacy (Lines 468-893):**
```reg
; Disable telemetry, cloud content, biometrics, sensors, location
; Disable Windows Copilot
; Disable Cortana and web search
; Extensive Windows Error Reporting disable
; Disable many telemetry-related services and tasks
HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI\DisableAIDataAnalysis = 1
HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search\AllowCortana = 0
```
✅ Very comprehensive privacy hardening

**Risk Level:** ⚠️ MODERATE
- Some changes are reversible, some require manual intervention
- Disabling Windows Search and Printing will break features
- Disabling Edge updates creates security vulnerabilities
- No explanations of what each change does
- No selective application (all or nothing)

**Effectiveness:** High for privacy and gaming performance
- Well-researched privacy settings
- Game performance optimizations are solid
- Some changes are outdated (Windows 10 specific)

**Quality Notes:**
- Extremely comprehensive (894 lines)
- No documentation of what each setting does
- No version detection (Windows 10 vs 11)
- Some settings are redundant (set multiple times)
- Good categorization with comments
- No uninstall mechanism

---

### 12. 5 Programs to tweak or increase privacy/1 CTT/cttoffline.ps1

**Purpose:** Apply Chris Titus Tech privacy and performance tweaks (offline version)

**Key Commands:**
```powershell
# Disable Consumer Features, Telemetry, Activity History
# Disable Location Tracking, Storage Sense, WiFi Sense
# Disable GameDVR, Hibernation, HomeGroup
# Disable Recall (Windows 11 24H2+)
# Debloat Edge (20+ registry settings)
# Disable IPv6 (controversial - can break networking)
# Disable Background Apps
# Disable Copilot, remove Copilot package
# Disable Intel vPro LMS service (aggressive)

# Remove OneDrive
# Uninstall OneDrive
# Move files from OneDrive to user profile
# Remove OneDrive registry entries and scheduled tasks
# Fix all user shell folder paths

# Set Dark Mode, disable Bing Search, hide Start Menu recommendations
# Show hidden files and file extensions
# Detailed BSOD instead of sad emoji

# Set Services to Manual/Disabled
# 200+ services configured to Manual, Disabled, Automatic, etc.
```

**Risk Level:** ⚠️ MODERATE TO HIGH
- Disables IPv6 - **can break network connectivity and applications**
- Aggressively removes Intel LMS - may break enterprise management features
- Modifies 200+ services - may break Windows functionality
- Removes Copilot package - may not be reversible
- No backup of original settings

**Effectiveness:** High for privacy, moderate for performance
- Well-established Chris Titus Tech methodology
- Some tweaks are controversial (IPv6, service disabling)
- OneDrive removal is well-implemented

**Quality Notes:**
- Based on reputable source (Chris Titus Tech)
- Comprehensive approach
- Some settings are too aggressive for average users
- IPv6 disabling is particularly problematic
- Good feedback with colored output
- No undo mechanism

---

### 13. 7 BIOS/Reboot to Bios.bat

**Purpose:** Reboot directly into BIOS/UEFI firmware settings

**Key Commands:**
```batch
shutdown /r /fw /f /t 0
```

**Risk Level:** ✅ SAFE
- Standard Windows command
- Forces reboot to firmware

**Effectiveness:** High - works as intended
- `/r` = reboot
- `/fw` = boot to firmware
- `/f` = force close apps
- `/t 0` = immediate

**Quality Notes:**
- Simple, effective utility
- Could use a countdown timer instead of immediate reboot
- No warning that all unsaved work will be lost

---

## Overall Assessment

### Strengths

1. **Comprehensive Coverage**
   - Driver installation automation
   - Extensive debloating options
   - Privacy hardening
   - Gaming performance optimization
   - Multiple approaches for different use cases

2. **Good Practices in Some Scripts**
   - OneDrive uninstaller has excellent safety checks
   - Firefox hardening leverages proven external tools
   - Chris Titus Tech integration is well-regarded
   - Some scripts check for existing installations

3. **Gaming Performance Focus**
   - Registry tweaks are well-researched
   - Power plan optimization is thorough
   - Game DVR and Game Bar settings are appropriate

### Critical Weaknesses

1. **🔴 EXTREMELY DANGEROUS SCRIPTS**
   - **Edge Uninstall.bat** can break Windows 11 permanently
   - **Power plan.ps1** will destroy laptop battery life and remove all battery warnings
   - **Enable powershell scripts.cmd** creates permanent security vulnerability
   - **Debloat all** removes essential utilities like Calculator and Terminal

2. **⚠️ Poor Risk Assessment**
   - No warnings about laptop vs desktop scenarios
   - No Windows version detection (10 vs 11)
   - No confirmation dialogs before destructive actions
   - No backup mechanisms

3. **⚠️ Quality Inconsistency**
   - Some scripts are excellent (OneDrive, Firefox)
   - Others are extremely dangerous (Edge, Power Plan)
   - No standardized error handling
   - Copy-paste errors between scripts (debloat scripts are identical)

4. **⚠️ Controversial Optimizations**
   - IPv6 disabling breaks modern networking
   - Aggressive service disabling may reduce performance
   - Unparking CPU cores doesn't help on modern hardware
   - Disabling Windows Search breaks Start Menu

5. **⚠️ Missing Safeguards**
   - No system restore points
   - No registry backups
   - No undo mechanisms
   - No detection of incompatible configurations

## Risk Summary by Category

| Category | Risk Level | Notes |
|----------|------------|-------|
| PowerShell Security | 🔴 CRITICAL | Sets execution policy to Unrestricted system-wide |
| Edge Removal | 🔴 CRITICAL | Breaks Windows 11, WebView2, and web-based features |
| Power Plan | 🔴 HIGH | Deletes all power plans, disables battery warnings - dangerous for laptops |
| Debloat | ⚠️ MODERATE | Removes useful utilities, no categorization |
| OneDrive Removal | ⚠️ MODERATE | Good safety checks, but removes cloud backup |
| Registry Tweaks | ⚠️ MODERATE | Comprehensive but no undo, some break features |
| CTT Script | ⚠️ MODERATE | IPv6 disabling controversial, many service changes |
| Firefox Hardening | ✅ LOW | Safe, leverages proven privacy tools |
| Driver Installers | ⚠️ MODERATE | No hash verification, obsolete DirectX |
| BIOS Reboot | ✅ SAFE | Standard Windows command |

## Windows 10/11 Compatibility

| Script | Win10 | Win11 | Notes |
|--------|-------|-------|-------|
| Enable PowerShell | ✅ | ✅ | Works but dangerous on both |
| C++ Installer | ✅ | ✅ | Compatible |
| DirectX | ✅ | ✅ | Obsolete for both |
| Debloat | ✅ | ⚠️ | Removes Windows 11 specific apps |
| Edge Removal | ⚠️ | 🔴 | Breaks Win11, dangerous on Win10 |
| OneDrive Removal | ✅ | ✅ | Compatible |
| Firefox | ✅ | ✅ | Compatible |
| Spotify | ✅ | ✅ | Compatible (but violates ToS) |
| Power Plan | ✅ | ✅ | Dangerous on laptops (both) |
| Registry.reg | ✅ | ⚠️ | Some settings don't apply to Win11 |
| CTT Script | ✅ | ✅ | Detects Windows version |
| BIOS Reboot | ✅ | ✅ | Compatible |

## Recommendations

### For Users

1. **AVOID ENTIRELY:**
   - Edge Uninstall.bat - will break your system
   - Power plan.ps1 if using a laptop
   - Debloat all Windows Apps.ps1 - removes too much
   - Enable powershell scripts.cmd - security risk

2. **USE WITH CAUTION:**
   - Registry.reg - review changes first, don't apply blindly
   - CTT Script - understand what it changes
   - Spotify.ps1 - violates ToS, may break

3. **GENERALLY SAFE:**
   - OneDrive uninstaller (if you don't use OneDrive)
   - Firefox hardening
   - BIOS reboot utility
   - C++ redistributables installer

4. **RECOMMENDED IMPROVEMENTS:**
   - Create System Restore point before running any scripts
   - Export registry backup before applying Registry.reg
   - Review all code before execution
   - Test in virtual machine first

### For the Developer

1. **Critical Safety Improvements Needed:**
   - Add Windows version detection (10 vs 11)
   - Detect laptop vs desktop before power plan changes
   - Add confirmation dialogs for destructive actions
   - Create undo/restore scripts
   - Remove Edge uninstaller or add massive warnings

2. **Code Quality:**
   - Fix copy-paste errors in debloat scripts
   - Add hash verification for downloaded files
   - Remove obsolete DirectX installer or add version checks
   - Use `Get-CimInstance` instead of deprecated `Get-WmiObject`
   - Standardize error handling

3. **Documentation:**
   - Explain what each registry setting does
   - Document prerequisites and known issues
   - Add risk levels to script descriptions
   - Provide troubleshooting guide

4. **Architecture:**
   - Create modular, opt-in approach instead of all-or-nothing
   - Separate safe tweaks from aggressive optimizations
   - Add configuration files for selective application
   - Implement logging and rollback capabilities

## Conclusion

Windows-Tweaks is a mixed bag of excellent and extremely dangerous scripts. The repository shows deep knowledge of Windows internals but lacks responsible safety practices. While the gaming performance optimizations are well-researched and the privacy enhancements are comprehensive, the inclusion of system-breaking scripts like the Edge uninstaller and aggressive power plan changes make this repository unsuitable for inexperienced users.

**The repository would benefit significantly from:**
1. Removing or heavily warning about dangerous scripts
2. Adding detection mechanisms (laptop vs desktop, Win10 vs Win11)
3. Implementing backup and rollback capabilities
4. Providing selective application of tweaks
5. Improving documentation and risk disclosure

**Overall Grade:** ⚠️ **C- (60/100)**

**Scoring Breakdown:**
- Effectiveness at Stated Goals: 8/10
- Code Quality: 5/10
- Safety Practices: 2/10
- Documentation: 4/10
- Reversibility: 2/10
- Windows 10/11 Compatibility: 6/10

**Verdict:** Contains some useful scripts but requires expert knowledge to use safely. Not recommended for general users without significant improvements to safety mechanisms and documentation.
