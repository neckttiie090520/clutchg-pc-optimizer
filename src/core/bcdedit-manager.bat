@echo off
:: ============================================
:: BCDEdit Manager Module
:: Handles boot configuration tweaks
:: ============================================

if "%~1"==":apply_safe_tweaks" goto :apply_safe_tweaks
if "%~1"==":apply_advanced_tweaks" goto :apply_advanced_tweaks
if "%~1"==":reset_all" goto :reset_all
if "%~1"==":export_current" goto :export_current
exit /b 0

:apply_safe_tweaks
:: ============================================
:: These tweaks are SAFE and do not compromise
:: system security. They can improve timer
:: consistency and multi-core coordination.
:: ============================================
set "MODULE_FAILURES=0"

:: Disable dynamic tick (consistent timer behavior)
call :bcd_set "disabledynamictick" "yes"

:: Use platform tick (hardware timer)
call :bcd_set "useplatformtick" "yes"

:: Enhanced TSC synchronization
call :bcd_set "tscsyncpolicy" "enhanced"

:: Disable legacy APIC mode (modern interrupt handling)
call :bcd_set "uselegacyapicmode" "no"

:: Optimize logical processor handling
call :bcd_set "usephysicaldestination" "no"

:: Enable x2APIC mode (improved interrupt handling on modern CPUs)
call :bcd_set "x2apicpolicy" "Enable"

:: Set configaccesspolicy to default (faster MMIO access)
call :bcd_set "configaccesspolicy" "Default"

if %MODULE_FAILURES% GTR 0 exit /b 1
exit /b 0

:apply_advanced_tweaks
:: ============================================
:: These tweaks have potential side effects.
:: They should only be applied by users who
:: understand the implications.
:: ============================================
set "MODULE_FAILURES=0"

echo.
echo  NOTE: Disabling hypervisor will break:
echo        - WSL2 (Windows Subsystem for Linux 2)
echo        - Docker Desktop
echo        - Hyper-V virtual machines
echo        - Windows Sandbox
echo.

call :bcd_set "hypervisorlaunchtype" "off"

if %MODULE_FAILURES% GTR 0 exit /b 1
exit /b 0

:reset_all
:: ============================================
:: Reset all BCDEdit values to Windows defaults
:: ============================================
set "MODULE_FAILURES=0"
echo     Resetting BCDEdit to defaults...

call :bcd_delete "disabledynamictick"
call :bcd_delete "useplatformtick"
call :bcd_delete "tscsyncpolicy"
call :bcd_delete "uselegacyapicmode"
call :bcd_delete "usephysicaldestination"
call :bcd_delete "x2apicpolicy"
call :bcd_delete "configaccesspolicy"
call :bcd_delete "hypervisorlaunchtype"

:: Reset security values to safe defaults
call :bcd_set "nx" "OptIn"
call :bcd_set "nointegritychecks" "off"
call :bcd_set "testsigning" "off"

if %MODULE_FAILURES% GTR 0 (
    call :log_bcdedit "Reset all values" "FAILED"
    exit /b 1
)
call :log_bcdedit "Reset all values" "SUCCESS"
exit /b 0

:export_current
set "MODULE_FAILURES=0"
if not defined BACKUP_FOLDER set "BACKUP_FOLDER=%~dp0..\backups\manual"
if not exist "%BACKUP_FOLDER%" mkdir "%BACKUP_FOLDER%" >nul 2>&1
if errorlevel 1 (
    call :log_bcdedit "Failed to create backup folder %BACKUP_FOLDER%" "FAILED"
    set /a MODULE_FAILURES+=1
)
if %MODULE_FAILURES% EQU 0 (
    bcdedit /export "%BACKUP_FOLDER%\bcd_backup" >nul 2>&1
    if errorlevel 1 (
        call :log_bcdedit "Failed to export BCD" "FAILED"
        set /a MODULE_FAILURES+=1
        set /a TWEAK_FAILED+=1
    )
)
if %MODULE_FAILURES% GTR 0 exit /b 1
call :log_bcdedit "Exported BCD to %BACKUP_FOLDER%\bcd_backup" "SUCCESS"
set /a TWEAK_SUCCESS+=1
exit /b 0

:bcd_set
bcdedit /set %~1 %~2 >nul 2>&1
if errorlevel 1 (
    call :log_bcdedit "%~1=%~2" "FAILED"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
call :log_bcdedit "%~1=%~2" "SUCCESS"
set /a TWEAK_SUCCESS+=1
exit /b 0

:bcd_delete
bcdedit /deletevalue %~1 >nul 2>&1
if errorlevel 1 (
    call :log_bcdedit "delete %~1" "FAILED"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
call :log_bcdedit "delete %~1" "SUCCESS"
set /a TWEAK_SUCCESS+=1
exit /b 0

:log_bcdedit
if defined LOGFILE (
    echo [%TIME%] [BCDEdit] %~1: %~2 >> "%LOGFILE%"
)
echo     [BCDEdit] %~1: %~2
exit /b 0
