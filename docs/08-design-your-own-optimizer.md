# Designing Your Own Windows Optimizer

> **Purpose:** Complete design document for building a professional-grade Windows optimizer from scratch, based on lessons learned from analyzing 27+ existing tools.

## Design Philosophy

### Core Principles

1. **Safety First**: Never compromise system security
2. **Transparency**: Explain every change to the user
3. **Reversibility**: Every tweak must be undoable
4. **Modularity**: Components work independently
5. **Validation**: Detect OS version and capabilities
6. **Logging**: Track all changes made
7. **Profiles**: Different use cases, different tweaks

### What We Learned from Existing Tools

| Good Practices | Bad Practices |
|----------------|---------------|
| WinUtil's safety approach | Disabling security features |
| BCDEditTweaks' documentation | Aggressive service disabling |
| FR33THY's modularity | Vague "FPS boost" claims |
| Gaming-Script's temp approach | No backup/restore |
| vacisdev's toggle system | Monolithic all-or-nothing scripts |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (ui/)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Main Menu → Profile Selection → Tweak Selection     │   │
│  │  → Confirmation → Progress → Summary                 │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Core Engine (core/)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  system-    │ │   registry  │ │   service   │           │
│  │  detect     │ │   manager   │ │   manager   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   bcdedit   │ │    power    │ │   network   │           │
│  │   manager   │ │   manager   │ │   manager   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│                    Safety Layer (safety/)                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  validator  │ │   rollback  │ │  conflict   │           │
│  │             │ │             │ │   checker   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   backup/   │ │  logging/   │ │  profiles/  │           │
│  │  (registry, │ │  (actions,  │ │  (config    │           │
│  │   services) │ │   results)  │ │   files)    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Specifications

### 1. System Detection Module (`core/system-detect.bat`)

```batch
:: Functions:
:: - Detect Windows version (10/11)
:: - Detect build number (19041, 22000, etc.)
:: - Detect edition (Home/Pro/Enterprise)
:: - Detect CPU (Intel/AMD)
:: - Detect GPU (NVIDIA/AMD/Intel)
:: - Detect system type (Desktop/Laptop)
:: - Check admin privileges
```

**Key Variables to Detect:**

| Variable | Method | Use |
|----------|--------|-----|
| OS Version | `ver`, WMI | Filter incompatible tweaks |
| Build Number | Registry | Version-specific behavior |
| Edition | `systeminfo` | Feature availability |
| CPU Vendor | `wmic cpu` | CPU-specific tweaks |
| GPU Vendor | `wmic path win32_VideoController` | GPU-specific options |
| Power Source | `wmic path Win32_Battery` | Laptop detection |

### 2. Registry Manager (`core/registry-utils.bat`)

```batch
:: Functions:
:: - Read registry value
:: - Write registry value with backup
:: - Delete registry value
:: - Import/export registry files
:: - Check value exists
:: - Compare values
```

**Implementation Pattern:**

```batch
:reg_set
:: Usage: call :reg_set "HKLM\Path" "ValueName" "Type" "Data"
:: Always backup before change
set "KEY=%~1"
set "VALUE=%~2"
set "TYPE=%~3"
set "DATA=%~4"

:: Backup current value
reg query "%KEY%" /v "%VALUE%" >> "%BACKUP_FILE%" 2>nul

:: Set new value
reg add "%KEY%" /v "%VALUE%" /t %TYPE% /d "%DATA%" /f

:: Log the change
call :log "Registry: %KEY%\%VALUE% = %DATA%"
goto :eof
```

### 3. Service Manager (`core/service-manager.bat`)

```batch
:: Functions:
:: - Get service status
:: - Get service start type
:: - Set service start type (with backup)
:: - Start/Stop service
:: - Check dependencies
:: - List dependent services
```

**Safety Checks:**

```batch
:service_disable
set "SERVICE=%~1"

:: Check if critical service
call :is_critical "%SERVICE%"
if %ERRORLEVEL%==1 (
    call :log "BLOCKED: Cannot disable critical service %SERVICE%"
    exit /b 1
)

:: Backup current config
sc qc "%SERVICE%" >> "%BACKUP_FILE%"

:: Set to disabled
sc config "%SERVICE%" start= disabled
call :log "Service: %SERVICE% set to disabled"
goto :eof

:is_critical
:: List of services that should NEVER be disabled
echo %~1 | findstr /i "wuauserv WinDefend CryptSvc RpcSs EventLog" >nul
if %ERRORLEVEL%==0 exit /b 1
exit /b 0
```

### 4. BCDEdit Manager (`core/bcdedit-manager.bat`)

```batch
:: Functions:
:: - Apply safe BCDEdit tweaks
:: - Apply advanced BCDEdit tweaks (with warnings)
:: - Reset BCDEdit to defaults
:: - Export current BCD
:: - Validate BCD health
```

**Safe vs Advanced Separation:**

```batch
:bcdedit_safe
call :log "Applying safe BCDEdit tweaks..."

bcdedit /set disabledynamictick yes
bcdedit /set useplatformtick yes
bcdedit /set tscsyncpolicy enhanced
bcdedit /set uselegacyapicmode no
bcdedit /set usephysicaldestination no

call :log "Safe BCDEdit tweaks applied"
goto :eof

:bcdedit_advanced
echo.
echo WARNING: Advanced BCDEdit tweaks may affect security.
echo These tweaks will:
echo  - Disable hypervisor (breaks WSL2, Docker, Hyper-V)
echo.
choice /c YN /m "Continue?"
if %ERRORLEVEL%==2 goto :eof

bcdedit /set hypervisorlaunchtype off
call :log "Advanced BCDEdit tweaks applied"
goto :eof
```

### 5. Power Manager (`core/power-manager.bat`)

```batch
:: Functions:
:: - List power plans
:: - Activate power plan
:: - Create Ultimate Performance plan
:: - Modify power plan settings
:: - Export/Import power plans
```

**Creating Ultimate Performance:**

```batch
:create_ultimate_performance
:: Check if already exists
powercfg /list | findstr "Ultimate Performance" >nul
if %ERRORLEVEL%==0 (
    call :log "Ultimate Performance plan already exists"
    goto :activate_ultimate
)

:: Duplicate High Performance and modify
powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
call :log "Created Ultimate Performance power plan"

:activate_ultimate
:: Find and activate Ultimate Performance
for /f "tokens=4" %%a in ('powercfg /list ^| findstr "Ultimate Performance"') do (
    powercfg /setactive %%a
)
call :log "Activated Ultimate Performance"
goto :eof
```

---

## Profile System

### Profile Definition Format (`profiles/*.bat`)

```batch
:: Profile: SAFE
:: Description: Daily use optimizations, no risk
:: Target: All users

:: === Tweaks to Apply ===
set "TWEAK_TELEMETRY=1"
set "TWEAK_VISUAL_EFFECTS=1"
set "TWEAK_GAME_MODE=1"
set "TWEAK_BCDEDIT_SAFE=1"

:: === Tweaks NOT Applied ===
set "TWEAK_SERVICES_AGGRESSIVE=0"
set "TWEAK_BCDEDIT_ADVANCED=0"
set "TWEAK_HYPERVISOR=0"
```

### Profile Definitions

#### Safe Profile (`profiles/safe-profile.bat`)

| Category | Tweaks Applied |
|----------|----------------|
| Power | High Performance plan |
| Telemetry | Disable tracking |
| Visual | Reduce animations |
| Game Mode | Enable |
| BCDEdit | Safe tweaks only |
| Services | Minimal changes |
| Security | ALL ENABLED |

#### Competitive Profile (`profiles/competitive-profile.bat`)

| Category | Tweaks Applied |
|----------|----------------|
| Power | Ultimate Performance |
| Telemetry | Full disable |
| Visual | Minimum effects |
| Game Mode | Enable |
| BCDEdit | Safe + hypervisor (optional) |
| Services | Disable Xbox, telemetry |
| Security | ALL ENABLED |
| Network | DNS optimization |
| Input | Raw input settings |

#### Extreme Profile (`profiles/extreme-profile.bat`)

| Category | Tweaks Applied |
|----------|----------------|
| All from Competitive | Yes |
| BCDEdit | Advanced tweaks |
| Services | Aggressive disable |
| Disclaimer | REQUIRED |

**Extreme profile disclaimer:**

```batch
:extreme_disclaimer
echo.
echo ========================================
echo        EXTREME PROFILE WARNING
echo ========================================
echo.
echo This profile applies aggressive optimizations that may:
echo  - Reduce system stability
echo  - Break some Windows features
echo  - Require manual recovery if issues occur
echo.
echo This is intended for experienced users only.
echo.
choice /c YN /m "I understand and accept these risks"
if %ERRORLEVEL%==2 exit /b 1
goto :eof
```

---

## Safety System

### Pre-Execution Validation (`safety/validator.bat`)

```batch
:validate_system
:: Check 1: Admin privileges
net session >nul 2>&1
if %ERRORLEVEL%==1 (
    echo ERROR: Administrator privileges required
    exit /b 1
)

:: Check 2: Supported OS version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%VERSION%" lss "10.0" (
    echo ERROR: Windows 10 or later required
    exit /b 1
)

:: Check 3: Not running in VM (warn only)
systeminfo | findstr /i "VMware VirtualBox Hyper-V" >nul
if %ERRORLEVEL%==0 (
    echo WARNING: Virtual machine detected
    echo Some tweaks may not work as expected
)

:: Check 4: Sufficient disk space
for /f "tokens=2" %%a in ('wmic logicaldisk where "DeviceID='C:'" get FreeSpace /format:value') do set FREESPACE=%%a
:: Convert to GB and check >1GB
:: (simplified check)

:: All checks passed
exit /b 0
```

### Backup System (`backup/backup-registry.bat`)

```batch
:create_backup
set "BACKUP_DIR=%~dp0backups\%DATE:/=-%_%TIME::=-%"
mkdir "%BACKUP_DIR%" 2>nul

:: Backup specific registry hives
reg export "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" "%BACKUP_DIR%\multimedia.reg" /y
reg export "HKLM\SYSTEM\CurrentControlSet\Services" "%BACKUP_DIR%\services.reg" /y
reg export "HKLM\SYSTEM\CurrentControlSet\Control\Power" "%BACKUP_DIR%\power.reg" /y

:: Backup BCD
bcdedit /export "%BACKUP_DIR%\bcd_backup"

:: Backup power plan
powercfg /export "%BACKUP_DIR%\power_plan.pow" SCHEME_CURRENT

:: Backup services list
sc query > "%BACKUP_DIR%\services_list.txt"

echo Backup created: %BACKUP_DIR%
goto :eof
```

### Restore System (`safety/rollback.bat`)

```batch
:restore_menu
echo.
echo Available backups:
dir /b "%~dp0backups" 2>nul
echo.
set /p BACKUP_NAME="Enter backup folder name (or 'cancel'): "
if /i "%BACKUP_NAME%"=="cancel" goto :eof

set "RESTORE_DIR=%~dp0backups\%BACKUP_NAME%"
if not exist "%RESTORE_DIR%" (
    echo Backup not found
    goto :restore_menu
)

echo.
echo Restoring from: %RESTORE_DIR%
choice /c YN /m "Confirm restore?"
if %ERRORLEVEL%==2 goto :eof

:: Restore registry
for %%f in ("%RESTORE_DIR%\*.reg") do (
    reg import "%%f"
    echo Imported: %%f
)

:: Restore BCD
if exist "%RESTORE_DIR%\bcd_backup" (
    bcdedit /import "%RESTORE_DIR%\bcd_backup"
    echo Restored BCD
)

echo.
echo Restore complete. Restart required.
goto :eof
```

### Restore Point Creation (`backup/restore-point.bat`)

```batch
:create_restore_point
echo Creating System Restore Point...

:: Enable restore for C: if disabled
vssadmin list shadows >nul 2>&1
if %ERRORLEVEL%==1 (
    echo Enabling System Protection...
    powershell -Command "Enable-ComputerRestore -Drive 'C:\'"
)

:: Create restore point
powershell -Command "Checkpoint-Computer -Description 'Pre-Optimization Backup' -RestorePointType 'MODIFY_SETTINGS'"

if %ERRORLEVEL%==0 (
    call :log "System Restore Point created successfully"
) else (
    call :log "WARNING: Could not create Restore Point"
)
goto :eof
```

---

## Logging System

### Logger (`logging/logger.bat`)

```batch
:: Initialize log file with timestamp
:init_log
set "LOGFILE=%~dp0logs\optimizer_%DATE:/=-%%TIME::=%.log"
mkdir "%~dp0logs" 2>nul

echo ================================================ >> "%LOGFILE%"
echo Windows Optimizer Log                           >> "%LOGFILE%"
echo Started: %DATE% %TIME%                          >> "%LOGFILE%"
echo System: %COMPUTERNAME%                          >> "%LOGFILE%"
echo User: %USERNAME%                                >> "%LOGFILE%"
echo ================================================ >> "%LOGFILE%"
goto :eof

:log
:: Usage: call :log "Message"
echo [%TIME%] %~1
echo [%TIME%] %~1 >> "%LOGFILE%"
goto :eof

:log_tweak
:: Usage: call :log_tweak "Category" "Tweak" "Result"
echo [%TIME%] [%~1] %~2: %~3 >> "%LOGFILE%"
goto :eof
```

### Log Example Output

```
================================================
Windows Optimizer Log
Started: 01-04-2026 20:45:32.15
System: GAMING-PC
User: John
================================================
[20:45:33.00] Creating System Restore Point...
[20:45:45.00] System Restore Point created successfully
[20:45:45.50] Creating registry backup...
[20:45:47.00] Backup created: backups\01-04-2026_20-45-32
[20:45:48.00] [Power] Setting Ultimate Performance: SUCCESS
[20:45:48.50] [BCDEdit] disabledynamictick=yes: SUCCESS
[20:45:49.00] [BCDEdit] useplatformtick=yes: SUCCESS
[20:45:49.50] [BCDEdit] tscsyncpolicy=enhanced: SUCCESS
[20:45:50.00] [Service] DiagTrack disabled: SUCCESS
[20:45:50.50] [Telemetry] AllowTelemetry=0: SUCCESS
================================================
Completed: 01-04-2026 20:45:52.00
Tweaks applied: 6 successful, 0 failed
================================================
```

---

## User Interface

### Main Menu (`ui/main-menu.bat`)

```batch
:main_menu
cls
echo ============================================
echo     Windows Optimizer v1.0
echo     Professional Performance Tuning
echo ============================================
echo.
echo  [1] Apply SAFE Profile (Recommended)
echo  [2] Apply COMPETITIVE Profile
echo  [3] Apply EXTREME Profile (Advanced Users)
echo.
echo  [4] Custom Tweak Selection
echo  [5] View Current Settings
echo  [6] Restore from Backup
echo.
echo  [7] View Documentation
echo  [8] About / Help
echo  [0] Exit
echo.
echo ============================================
choice /c 12345678 /n /m "Select option: "

if %ERRORLEVEL%==1 call :apply_safe
if %ERRORLEVEL%==2 call :apply_competitive
if %ERRORLEVEL%==3 call :apply_extreme
if %ERRORLEVEL%==4 call :custom_selection
if %ERRORLEVEL%==5 call :view_settings
if %ERRORLEVEL%==6 call :restore_menu
if %ERRORLEVEL%==7 call :view_docs
if %ERRORLEVEL%==8 call :about
if %ERRORLEVEL%==0 exit /b

goto :main_menu
```

### Confirmation Screen

```batch
:confirm_profile
cls
echo ============================================
echo     Profile: %PROFILE_NAME%
echo ============================================
echo.
echo The following changes will be made:
echo.
echo  [Power]
for %%t in (%POWER_TWEAKS%) do echo   - %%t
echo.
echo  [Services]
for %%t in (%SERVICE_TWEAKS%) do echo   - %%t
echo.
echo  [Registry]
for %%t in (%REGISTRY_TWEAKS%) do echo   - %%t
echo.
echo  [BCDEdit]
for %%t in (%BCDEDIT_TWEAKS%) do echo   - %%t
echo.
echo ============================================
echo A backup will be created before changes.
echo ============================================
echo.
choice /c YNC /m "[Y]es, apply / [N]o, cancel / [C]ustomize"

if %ERRORLEVEL%==1 goto :apply_profile
if %ERRORLEVEL%==2 goto :main_menu
if %ERRORLEVEL%==3 goto :custom_selection
```

---

## Tweak Documentation Standard

Each tweak must include:

```batch
:: ============================================
:: Tweak: [Name]
:: Category: [Power/Service/Registry/BCDEdit]
:: Risk Level: [1-5]
:: 
:: What it does:
::   [Technical explanation]
::
:: Why it helps:
::   [Performance benefit]
::
:: Side effects:
::   [What could go wrong]
::
:: Reversibility:
::   [How to undo]
::
:: Valid on:
::   [Windows versions]
:: ============================================
```

---

## File Structure

```
/WindowsOptimizer
├── optimizer.bat          # Main entry point
├── README.md              # User documentation
├── CHANGELOG.md           # Version history
│
├── /core                  # Core modules
│   ├── system-detect.bat
│   ├── registry-utils.bat
│   ├── service-manager.bat
│   ├── bcdedit-manager.bat
│   ├── power-manager.bat
│   └── network-manager.bat
│
├── /profiles              # Profile definitions
│   ├── safe-profile.bat
│   ├── competitive-profile.bat
│   └── extreme-profile.bat
│
├── /safety                # Safety systems
│   ├── validator.bat
│   ├── rollback.bat
│   └── conflict-checker.bat
│
├── /backup                # Backup systems
│   ├── backup-registry.bat
│   ├── restore-point.bat
│   └── /backups           # Backup storage
│
├── /logging               # Logging
│   ├── logger.bat
│   └── /logs              # Log storage
│
├── /ui                    # User interface
│   ├── main-menu.bat
│   ├── progress-bar.bat
│   └── summary.bat
│
└── /docs                  # Documentation
    ├── tweak-reference.md
    └── troubleshooting.md
```

---

*This design document synthesizes best practices from 27+ analyzed repositories into a cohesive, professional optimizer framework.*
