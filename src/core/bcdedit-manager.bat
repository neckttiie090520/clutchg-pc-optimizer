@echo off
:: ============================================
:: BCDEdit Manager Module
:: Handles boot configuration tweaks
:: ============================================

if "%~1"==":apply_safe_tweaks" goto :apply_safe_tweaks
if "%~1"==":apply_advanced_tweaks" goto :apply_advanced_tweaks
if "%~1"==":reset_all" goto :reset_all
if "%~1"==":export_current" goto :export_current
goto :eof

:apply_safe_tweaks
:: ============================================
:: These tweaks are SAFE and do not compromise
:: system security. They can improve timer
:: consistency and multi-core coordination.
:: ============================================

:: Disable dynamic tick (consistent timer behavior)
:: Benefit: More predictable tick timing
:: Trade-off: Slightly higher power consumption
bcdedit /set disabledynamictick yes >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_bcdedit "disabledynamictick=yes" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_bcdedit "disabledynamictick=yes" "FAILED"
    set /a TWEAK_FAILED+=1
)

:: Use platform tick (hardware timer)
:: Benefit: More accurate timer resolution
bcdedit /set useplatformtick yes >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_bcdedit "useplatformtick=yes" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_bcdedit "useplatformtick=yes" "FAILED"
    set /a TWEAK_FAILED+=1
)

:: Enhanced TSC synchronization
:: Benefit: Better multi-core timer coordination
bcdedit /set tscsyncpolicy enhanced >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_bcdedit "tscsyncpolicy=enhanced" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_bcdedit "tscsyncpolicy=enhanced" "FAILED"
    set /a TWEAK_FAILED+=1
)

:: Disable legacy APIC mode (modern interrupt handling)
:: Benefit: More efficient interrupt processing
bcdedit /set uselegacyapicmode no >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_bcdedit "uselegacyapicmode=no" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_bcdedit "uselegacyapicmode=no" "FAILED"
    set /a TWEAK_FAILED+=1
)

:: Optimize logical processor handling
bcdedit /set usephysicaldestination no >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_bcdedit "usephysicaldestination=no" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_bcdedit "usephysicaldestination=no" "FAILED"
    set /a TWEAK_FAILED+=1
)

:: Enable x2APIC mode (improved interrupt handling on modern CPUs)
:: Source: Ghost-Optimizer (performanceapply)
bcdedit /set x2apicpolicy Enable >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_bcdedit "x2apicpolicy=Enable" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_bcdedit "x2apicpolicy=Enable" "FAILED"
    set /a TWEAK_FAILED+=1
)

:: Set configaccesspolicy to default (faster MMIO access)
:: Source: Ghost-Optimizer (performanceapply)
bcdedit /set configaccesspolicy Default >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_bcdedit "configaccesspolicy=Default" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_bcdedit "configaccesspolicy=Default" "FAILED"
    set /a TWEAK_FAILED+=1
)

goto :eof

:apply_advanced_tweaks
:: ============================================
:: These tweaks have potential side effects.
:: They should only be applied by users who
:: understand the implications.
:: ============================================

:: Disable hypervisor (if not using VMs)
:: Benefit: Removes virtualization overhead
:: Trade-off: Breaks WSL2, Docker, Hyper-V
echo.
echo  NOTE: Disabling hypervisor will break:
echo        - WSL2 (Windows Subsystem for Linux 2)
echo        - Docker Desktop
echo        - Hyper-V virtual machines
echo        - Windows Sandbox
echo.

bcdedit /set hypervisorlaunchtype off >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_bcdedit "hypervisorlaunchtype=off" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_bcdedit "hypervisorlaunchtype=off" "FAILED"
    set /a TWEAK_FAILED+=1
)

goto :eof

:reset_all
:: ============================================
:: Reset all BCDEdit values to Windows defaults
:: ============================================

echo     Resetting BCDEdit to defaults...

bcdedit /deletevalue disabledynamictick >nul 2>&1
bcdedit /deletevalue useplatformtick >nul 2>&1
bcdedit /deletevalue tscsyncpolicy >nul 2>&1
bcdedit /deletevalue uselegacyapicmode >nul 2>&1
bcdedit /deletevalue usephysicaldestination >nul 2>&1
bcdedit /deletevalue x2apicpolicy >nul 2>&1
bcdedit /deletevalue configaccesspolicy >nul 2>&1
bcdedit /deletevalue hypervisorlaunchtype >nul 2>&1

:: Reset security values to safe defaults
bcdedit /set nx OptIn >nul 2>&1
bcdedit /set nointegritychecks off >nul 2>&1
bcdedit /set testsigning off >nul 2>&1

call :log_bcdedit "Reset all values" "SUCCESS"
goto :eof

:export_current
:: Export current BCD configuration
if not defined BACKUP_FOLDER set "BACKUP_FOLDER=%~dp0..\backups\manual"
mkdir "%BACKUP_FOLDER%" 2>nul
bcdedit /export "%BACKUP_FOLDER%\bcd_backup" >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_bcdedit "Exported BCD to %BACKUP_FOLDER%\bcd_backup" "SUCCESS"
) else (
    call :log_bcdedit "Failed to export BCD" "FAILED"
)
goto :eof

:log_bcdedit
if defined LOGFILE (
    echo [%TIME%] [BCDEdit] %~1: %~2 >> "%LOGFILE%"
)
echo     [BCDEdit] %~1: %~2
goto :eof
