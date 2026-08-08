@echo off
:: ============================================
:: ClutchG Optimizer v2.0 (Enhanced)
:: Evidence-Based Windows Performance Tuning
:: ============================================
::
:: This optimizer is designed with safety, transparency,
:: and effectiveness as core principles. All tweaks are
:: documented and reversible.
::
:: Based on research of 28+ Windows optimization tools
:: and comprehensive analysis in research.md
::
:: Updated: 2025-02-02 (Evidence-based optimizations)
:: ============================================
:: EVIDENCE-BASED PRINCIPLES:
:: - Realistic 5-15% improvement (not 200% like snake-oil tools)
:: - Safety-first: Never disable Defender, UAC, or security features
:: - All optimizations backed by research.md benchmarks
:: - Complete rollback capability via flight-recorder
:: ============================================

setlocal EnableDelayedExpansion

:: Initialize paths
set "SCRIPT_DIR=%~dp0"
set "CORE_DIR=%SCRIPT_DIR%core"
set "PROFILES_DIR=%SCRIPT_DIR%profiles"
set "SAFETY_DIR=%SCRIPT_DIR%safety"
set "BACKUP_DIR=%SCRIPT_DIR%backup"
set "LOGGING_DIR=%SCRIPT_DIR%logging"
set "LOGS_DIR=%SCRIPT_DIR%logs"
set "BACKUPS_DIR=%SCRIPT_DIR%backups"
set "VALIDATION_DIR=%SCRIPT_DIR%validation"

:: Non-interactive API used by the Python GUI. Keep profile declaration and
:: mutation in this CMD process so the declared TWEAK_* variables remain scoped.
if /i "%~1"=="apply-profile" goto :cli_apply_profile
if not "%~1"=="" goto :cli_usage_error

:: Initialize counters
set /a TWEAK_SUCCESS=0
set /a TWEAK_FAILED=0
set /a TWEAK_SKIPPED=0

:: Check for core modules
if not exist "%CORE_DIR%\system-detect.bat" (
    echo ERROR: Core modules not found.
    echo Please ensure all files are present.
    pause
    exit /b 1
)

:: Initialize logging
call "%LOGGING_DIR%\logger.bat" :init_log

:: Display header
call :show_header

:: Check admin privileges
call "%SAFETY_DIR%\validator.bat" :check_admin
if %ERRORLEVEL%==1 (
    echo.
    echo This application requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Detect system
call "%CORE_DIR%\system-detect.bat" :detect_all
goto :main_menu

:: ============================================================================
:: Non-interactive profile contract
:: Usage: optimizer.bat apply-profile SAFE|COMPETITIVE|EXTREME
:: ============================================================================
:cli_apply_profile
set "PROFILE_NAME=%~2"
set "PROFILE_FILE="
if not "%~3"=="" goto :cli_usage_error
if /i "!PROFILE_NAME!"=="SAFE" set "PROFILE_FILE=safe-profile.bat"
if /i "!PROFILE_NAME!"=="COMPETITIVE" set "PROFILE_FILE=competitive-profile.bat"
if /i "!PROFILE_NAME!"=="EXTREME" set "PROFILE_FILE=extreme-profile.bat"
if not defined PROFILE_FILE goto :cli_usage_error

if not exist "%CORE_DIR%\system-detect.bat" (
    echo ERROR: Core modules not found.
    exit /b 1
)
if not exist "%PROFILES_DIR%\!PROFILE_FILE!" (
    echo ERROR: Profile declaration not found: !PROFILE_FILE!
    exit /b 1
)

call "%LOGGING_DIR%\logger.bat" :init_log
call "%SAFETY_DIR%\validator.bat" :check_admin
if errorlevel 1 (
    echo ERROR: Administrator privileges are required.
    exit /b 1
)
call "%CORE_DIR%\system-detect.bat" :detect_all
if errorlevel 1 (
    echo ERROR: System detection failed.
    exit /b 1
)

call :reset_profile_flags
call "%PROFILES_DIR%\!PROFILE_FILE!"
if errorlevel 1 (
    echo ERROR: Profile declaration failed to load.
    exit /b 1
)
call :apply_profile "!PROFILE_NAME!"
exit /b !ERRORLEVEL!

:cli_usage_error
echo Usage: optimizer.bat apply-profile SAFE^|COMPETITIVE^|EXTREME
exit /b 2

:: Main menu loop
:main_menu
cls
call :show_header
echo.
echo  System: Windows %OS_VERSION% (Build %OS_BUILD%)
echo  CPU: %CPU_NAME%
echo  GPU: %GPU_NAME%
echo.
echo  ============================================
echo.
echo   [1] Apply SAFE Profile (Recommended)
echo   [2] Apply COMPETITIVE Profile
echo   [3] Apply EXTREME Profile (Advanced)
echo.
echo   [4] Custom Tweak Selection
echo   [5] View Current System Status
echo   [6] Restore from Backup
echo   [7] Reset All Tweaks to Default
echo.
echo   [8] View Documentation
echo   [9] About / Help
echo   [0] Exit
echo.
echo  ============================================
choice /c 1234567890 /n /m "  Select option: "

if %ERRORLEVEL%==1 goto :profile_safe
if %ERRORLEVEL%==2 goto :profile_competitive
if %ERRORLEVEL%==3 goto :profile_extreme
if %ERRORLEVEL%==4 goto :custom_menu
if %ERRORLEVEL%==5 goto :view_status
if %ERRORLEVEL%==6 goto :restore_menu
if %ERRORLEVEL%==7 goto :reset_all
if %ERRORLEVEL%==8 goto :view_docs
if %ERRORLEVEL%==9 goto :about
if %ERRORLEVEL%==10 goto :exit_optimizer

goto :main_menu

:: ============================================
:: Profile Application
:: ============================================

:profile_safe
call :reset_profile_flags
call "%PROFILES_DIR%\safe-profile.bat"
if errorlevel 1 goto :profile_load_failed
call :apply_profile "SAFE"
if errorlevel 1 goto :profile_apply_failed
pause
goto :main_menu

:profile_competitive
call :reset_profile_flags
call "%PROFILES_DIR%\competitive-profile.bat"
if errorlevel 1 goto :profile_load_failed
call :apply_profile "COMPETITIVE"
if errorlevel 1 goto :profile_apply_failed
pause
goto :main_menu

:profile_extreme
echo.
echo  ============================================
echo           EXTREME PROFILE WARNING
echo  ============================================
echo.
echo  This profile applies aggressive but reversible optimizations.
echo  Security-reducing and irreversible actions require separate consent.
echo.
choice /c YN /m "  I understand and accept these risks"
if %ERRORLEVEL%==2 goto :main_menu
call :reset_profile_flags
call "%PROFILES_DIR%\extreme-profile.bat"
if errorlevel 1 goto :profile_load_failed
call :apply_profile "EXTREME"
if errorlevel 1 goto :profile_apply_failed
pause
goto :main_menu

:apply_profile
set "PROFILE_NAME=%~1"
set /a TWEAK_SUCCESS=0
set /a TWEAK_FAILED=0
set /a TWEAK_SKIPPED=0
set "CLUTCHG_BACKUP_READY=0"
echo.
echo  ============================================
echo   Applying %PROFILE_NAME% Profile
echo  ============================================
echo.

:: Recovery gates must complete before the first mutation.
echo  [1/4] Creating System Restore Point...
call "%BACKUP_DIR%\restore-point.bat" create_restore_point
if errorlevel 1 (
    echo ERROR: Restore point creation failed. No optimizations were applied.
    exit /b 1
)

echo  [2/4] Creating journaled backup transaction...
call "%SAFETY_DIR%\flight-recorder.bat" create_snapshot
if errorlevel 1 (
    echo ERROR: Backup transaction failed. No optimizations were applied.
    exit /b 1
)
if not "!CLUTCHG_BACKUP_READY!"=="1" (
    echo ERROR: Backup transaction did not produce a committed recovery artifact.
    exit /b 1
)
echo        Backup committed: !BACKUP_FOLDER!
echo.

echo  [3/4] Applying optimizations...
if "%TWEAK_POWER%"=="1" call :run_tweak_module "Power settings" "%CORE_DIR%\power-manager.bat" ":apply_power_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_BCDEDIT_SAFE%"=="1" call :run_tweak_module "BCDEdit safe tweaks" "%CORE_DIR%\bcdedit-manager.bat" ":apply_safe_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_BCDEDIT_ADVANCED%"=="1" call :run_tweak_module "BCDEdit advanced tweaks" "%CORE_DIR%\bcdedit-manager.bat" ":apply_advanced_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_SERVICES%"=="1" call :run_tweak_module "Service optimization" "%CORE_DIR%\service-manager.bat" ":apply_service_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_TELEMETRY%"=="1" call :run_tweak_module "Privacy and telemetry" "%CORE_DIR%\registry-utils.bat" ":apply_telemetry_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_GAMING%"=="1" call :run_tweak_module "Gaming optimizations" "%CORE_DIR%\registry-utils.bat" ":apply_gaming_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_VISUAL%"=="1" call :run_tweak_module "Visual effects" "%CORE_DIR%\registry-utils.bat" ":apply_visual_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_NETWORK_SAFE%"=="1" call :run_tweak_module "Safe network optimizations" "%CORE_DIR%\network-optimizer-enhanced.bat" "apply_safe_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_NETWORK_AGGRESSIVE%"=="1" call :run_tweak_module "Aggressive network optimizations" "%CORE_DIR%\network-optimizer-enhanced.bat" "apply_aggressive_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_NETWORK%"=="1" call :run_tweak_module "Legacy network optimization" "%CORE_DIR%\network-manager.bat" ":apply_network_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_GPU%"=="1" call :run_tweak_module "GPU optimizations" "%CORE_DIR%\gpu-optimizer.bat" "apply_gpu_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_POWER_ENHANCED%"=="1" call :run_tweak_module "Enhanced power management" "%CORE_DIR%\power-manager-enhanced.bat" ":apply_all_enhanced"
if errorlevel 1 exit /b 1
if "%TWEAK_GPU_ENHANCED%"=="1" call :run_tweak_module "Vendor-specific GPU optimizations" "%CORE_DIR%\gpu-optimizer-enhanced.bat" ":apply_all_vendor_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_KERNEL_INPUT%"=="1" call :run_tweak_module "Kernel and input optimizations" "%CORE_DIR%\registry-utils.bat" ":apply_kernel_input_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_STORAGE%"=="1" call :run_tweak_module "Storage optimizations" "%CORE_DIR%\storage-optimizer.bat" "apply_storage_tweaks"
if errorlevel 1 exit /b 1
if "%TWEAK_MAINTENANCE%"=="1" call :run_tweak_module "Safe maintenance" "%CORE_DIR%\maintenance-manager.bat" ":apply_safe_maintenance"
if errorlevel 1 exit /b 1
if "%TWEAK_BENCHMARK%"=="1" call :run_tweak_module "Performance benchmark" "%VALIDATION_DIR%\benchmark-runner.bat" ":run_benchmark"
if errorlevel 1 exit /b 1

echo.
echo  [4/4] Optimization Complete
echo  ============================================
echo   Profile Applied: %PROFILE_NAME%
echo   Backup saved to: !BACKUP_FOLDER!
echo   Security-reducing and irreversible actions: not included
echo  ============================================
exit /b 0

:run_tweak_module
set "MODULE_DESCRIPTION=%~1"
set "MODULE_SCRIPT=%~2"
set "MODULE_ARGUMENT=%~3"
echo        - !MODULE_DESCRIPTION!...
if not exist "!MODULE_SCRIPT!" (
    echo ERROR: Missing module: !MODULE_SCRIPT!
    set /a TWEAK_FAILED+=1
    exit /b 2
)
call "!MODULE_SCRIPT!" "!MODULE_ARGUMENT!"
set "MODULE_CODE=!ERRORLEVEL!"
if not "!MODULE_CODE!"=="0" (
    echo ERROR: !MODULE_DESCRIPTION! failed with exit code !MODULE_CODE!.
    set /a TWEAK_FAILED+=1
    exit /b !MODULE_CODE!
)
set /a TWEAK_SUCCESS+=1
exit /b 0

:reset_profile_flags
set "TWEAK_POWER=0"
set "TWEAK_BCDEDIT_SAFE=0"
set "TWEAK_BCDEDIT_ADVANCED=0"
set "TWEAK_SERVICES=0"
set "TWEAK_TELEMETRY=0"
set "TWEAK_GAMING=0"
set "TWEAK_VISUAL=0"
set "TWEAK_NETWORK_SAFE=0"
set "TWEAK_NETWORK_AGGRESSIVE=0"
set "TWEAK_NETWORK=0"
set "TWEAK_GPU=0"
set "TWEAK_POWER_ENHANCED=0"
set "TWEAK_GPU_ENHANCED=0"
set "TWEAK_KERNEL_INPUT=0"
set "TWEAK_STORAGE=0"
set "TWEAK_MAINTENANCE=0"
set "TWEAK_BENCHMARK=0"
set "TWEAK_TELEMETRY_FULL=0"
set "TWEAK_INPUT=0"
set "TWEAK_DEBLOAT=0"
set "TWEAK_NETWORK_TCP=0"
exit /b 0

:profile_load_failed
echo ERROR: Profile declaration failed to load. No changes were made.
pause
goto :main_menu

:profile_apply_failed
echo ERROR: Profile application stopped. Review the recovery journal before retrying.
pause
goto :main_menu

:: ============================================
:: Custom Menu
:: ============================================

:custom_menu
cls
call :show_header
echo.
echo   Custom Tweak Selection
echo   ----------------------
echo.
echo   [1] Power Management Tweaks
echo   [2] BCDEdit Safe Tweaks
echo   [3] BCDEdit Advanced Tweaks (Caution)
echo   [4] Service Optimization
echo   [5] Privacy/Telemetry Tweaks
echo   [6] Gaming Tweaks (MMCSS)
echo   [7] Visual Effects
echo   [8] Network Tweaks
echo.
echo   [9] Apply Selected
echo   [0] Back to Main Menu
echo.
choice /c 1234567890 /n /m "  Select option: "

if %ERRORLEVEL%==1 set /a CUSTOM_POWER=1-CUSTOM_POWER
if %ERRORLEVEL%==2 set /a CUSTOM_BCDEDIT_SAFE=1-CUSTOM_BCDEDIT_SAFE
if %ERRORLEVEL%==3 set /a CUSTOM_BCDEDIT_ADV=1-CUSTOM_BCDEDIT_ADV
if %ERRORLEVEL%==4 set /a CUSTOM_SERVICES=1-CUSTOM_SERVICES
if %ERRORLEVEL%==5 set /a CUSTOM_TELEMETRY=1-CUSTOM_TELEMETRY
if %ERRORLEVEL%==6 set /a CUSTOM_GAMING=1-CUSTOM_GAMING
if %ERRORLEVEL%==7 set /a CUSTOM_VISUAL=1-CUSTOM_VISUAL
if %ERRORLEVEL%==8 set /a CUSTOM_NETWORK=1-CUSTOM_NETWORK
if %ERRORLEVEL%==9 goto :apply_custom
if %ERRORLEVEL%==10 goto :main_menu

goto :custom_menu

:apply_custom
:: Reset every profile flag before mapping the explicit custom selection.
call :reset_profile_flags
set "TWEAK_POWER=%CUSTOM_POWER%"
set "TWEAK_BCDEDIT_SAFE=%CUSTOM_BCDEDIT_SAFE%"
set "TWEAK_BCDEDIT_ADVANCED=%CUSTOM_BCDEDIT_ADV%"
set "TWEAK_SERVICES=%CUSTOM_SERVICES%"
set "TWEAK_TELEMETRY=%CUSTOM_TELEMETRY%"
set "TWEAK_GAMING=%CUSTOM_GAMING%"
set "TWEAK_VISUAL=%CUSTOM_VISUAL%"
set "TWEAK_NETWORK=%CUSTOM_NETWORK%"

call :apply_profile "CUSTOM"
if errorlevel 1 goto :profile_apply_failed
pause
goto :main_menu

:: ============================================
:: View Status
:: ============================================

:view_status
cls
call :show_header
echo.
echo   Current System Status
echo   ----------------------
echo.
echo   [Power Plan]
for /f "tokens=4*" %%a in ('powercfg /getactivescheme') do echo     Active: %%b
echo.
echo   [BCDEdit Settings]
for %%s in (disabledynamictick useplatformtick tscsyncpolicy hypervisorlaunchtype) do (
    for /f "tokens=2 delims=:" %%v in ('bcdedit /enum {current} ^| findstr /i "%%s"') do (
        echo     %%s: %%v
    )
)
echo.
echo   [Key Services]
for %%s in (DiagTrack SysMain WSearch WinDefend) do (
    for /f "tokens=3" %%v in ('sc query "%%s" ^| findstr "STATE"') do (
        echo     %%s: %%v
    )
)
echo.
pause
goto :main_menu

:: ============================================
:: Restore Menu
:: ============================================

:restore_menu
cls
call :show_header
echo.
echo   Restore from Backup
echo   ----------------------
echo.
echo   Available backups:
echo.
if not exist "%BACKUPS_DIR%" (
    echo   No backups found.
    echo.
    pause
    goto :main_menu
)
dir /b "%BACKUPS_DIR%" 2>nul
if %ERRORLEVEL%==1 (
    echo   No backups found.
    echo.
    pause
    goto :main_menu
)
echo.
set /p BACKUP_SELECT="  Enter backup folder name (or 'cancel'): "
if /i "%BACKUP_SELECT%"=="cancel" goto :main_menu

call "%SAFETY_DIR%\rollback.bat" :restore_from_backup "%BACKUP_SELECT%"
pause
goto :main_menu

:: ============================================
:: Reset All
:: ============================================

:reset_all
cls
call :show_header
echo.
echo   Reset All Tweaks to Default
echo   ----------------------------
echo.
echo   This will reset:
echo   - BCDEdit settings to Windows defaults
echo   - Services to automatic startup
echo   - Registry tweaks to original values
echo.
echo   Note: This requires a recent backup to work correctly.
echo.
choice /c YN /m "  Proceed with reset?"
if %ERRORLEVEL%==2 goto :main_menu

call "%CORE_DIR%\bcdedit-manager.bat" :reset_all
call "%CORE_DIR%\service-manager.bat" :reset_all
call "%CORE_DIR%\registry-utils.bat" :reset_all

echo.
echo   Reset complete. Please restart your computer.
echo.
pause
goto :main_menu

:: ============================================
:: Documentation
:: ============================================

:view_docs
cls
call :show_header
echo.
echo   Documentation
echo   -------------
echo.
echo   Documentation files are located in:
echo   %SCRIPT_DIR%..\docs\
echo.
echo   Key documents:
echo   - 03-tweak-taxonomy.md    (All tweaks explained)
echo   - 04-risk-classification.md (Risk levels)
echo   - 05-windows-internals.md (Technical details)
echo   - 07-best-practices.md   (Recommendations)
echo.
echo   Would you like to open the docs folder?
choice /c YN /m "  "
if %ERRORLEVEL%==1 start "" "%SCRIPT_DIR%..\docs"
goto :main_menu

:: ============================================
:: About
:: ============================================

:about
cls
call :show_header
echo.
echo   About Windows Optimizer
echo   -----------------------
echo.
echo   Version: 1.0.0
echo   License: MIT
echo.
echo   This optimizer was designed based on research of
echo   27+ Windows optimization tools, synthesizing best
echo   practices and avoiding common pitfalls.
echo.
echo   Core Principles:
echo   - Safety First: Never compromise security
echo   - Transparency: All tweaks documented
echo   - Reversibility: Every change can be undone
echo   - Evidence-Based: No placebo tweaks
echo.
echo   DISCLAIMER:
echo   This software modifies Windows settings. Always
echo   create backups before making changes. The author
echo   is not liable for any system issues.
echo.
pause
goto :main_menu

:: ============================================
:: Exit
:: ============================================

:exit_optimizer
echo.
echo  Thank you for using Windows Optimizer.
echo.
call "%LOGGING_DIR%\logger.bat" :log "Optimizer closed"
endlocal
exit /b 0

:: ============================================
:: Helper Functions
:: ============================================

:show_header
echo.
echo  ============================================
echo       Windows Optimizer v1.0
echo       Professional Performance Tuning
echo  ============================================
goto :eof
