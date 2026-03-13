@echo off
:: ============================================
:: Power Manager Enhanced Module
:: Advanced power optimizations: AMD CPPC, EPP, GPU P-State
:: Risk Level: MODERATE
:: ============================================

if "%~1"==":apply_cppc_tweaks" goto :apply_cppc_tweaks
if "%~1"==":apply_epp_performance" goto :apply_epp_performance
if "%~1"==":apply_gpu_pstate" goto :apply_gpu_pstate
if "%~1"==":apply_all_enhanced" goto :apply_all_enhanced
goto :eof

:apply_cppc_tweaks
:: ============================================
:: AMD CPPC Preferred Core Optimization
:: ============================================
:: Only for AMD Ryzen CPUs (Ryzen 2000 series and later)
:: Benefit: Better CPU thread scheduling (1-3% improvement)

:: Check if AMD CPU
if /i not "%CPU_VENDOR%"=="AMD" (
    call :log_power_enhanced "CPPC tweaks skipped: Not AMD CPU"
    goto :eof
)

:: Enable AMD CPPC Preferred Core
:: Registry: HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\cc4b4f14-5ea2-4f98-9b3f-b38c8af0a7f0
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\cc4b4f14-5ea2-4f98-9b3f-b38c8af0a7f0" /v "SettingValue" /t REG_DWORD /d 0 /f >nul 2>&1

if %ERRORLEVEL%==0 (
    call :log_power_enhanced "AMD CPPC Preferred Core enabled"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_power_enhanced "AMD CPPC Preferred Core failed"
    set /a TWEAK_FAILED+=1
)
goto :eof

:apply_epp_performance
:: ============================================
:: Energy Performance Preference (EPP)
:: ============================================
:: Set EPP to maximum performance (0 = max performance, 100 = max power saving)
:: Benefit: 2-5% CPU performance increase
:: Risk: May increase heat/power consumption

:: Set EPP to 0 (maximum performance) for AC power
powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR 54533251-82be-4824-96c1-47b60b740d00 0 >nul 2>&1

:: Set EPP to 50 (balanced) for DC power (battery)
powercfg /setdcvalueindex SCHEME_CURRENT SUB_PROCESSOR 54533251-82be-4824-96c1-47b60b740d00 50 >nul 2>&1

:: Apply power scheme changes
powercfg /setactive SCHEME_CURRENT >nul 2>&1

if %ERRORLEVEL%==0 (
    call :log_power_enhanced "EPP set to maximum performance (AC), balanced (DC)"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_power_enhanced "EPP configuration failed"
    set /a TWEAK_FAILED+=1
)
goto :eof

:apply_gpu_pstate
:: ============================================
:: NVIDIA GPU P-State Control
:: ============================================
:: Disable NVIDIA P-state limiting for maximum performance
:: Benefit: 2-10% FPS improvement
:: Risk: May increase GPU power consumption

:: Check if NVIDIA GPU
if /i not "%GPU_VENDOR%"=="NVIDIA" (
    call :log_power_enhanced "GPU P-State skipped: Not NVIDIA GPU"
    goto :eof
)

:: Find NVIDIA GPU in registry
:: Path: HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}\####

:: Backup GPU registry first
reg export "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}" "%BACKUP_DIR%\gpu_registry_backup.reg" >nul 2>&1

:: Loop through GPU subkeys to find NVIDIA
for /f "tokens=*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}" /s 2^>nul ^| findstr /i "NVIDIA"') do (
    set "GPU_PATH=%%a"
)

:: Apply P-State tweak if NVIDIA GPU found
if defined GPU_PATH (
    :: Disable P-state limiting
    reg add "%GPU_PATH%\PowerManagement" /v "DisablePstate" /t REG_DWORD /d 0 /f >nul 2>&1

    if %ERRORLEVEL%==0 (
        call :log_power_enhanced "NVIDIA GPU P-State limiting disabled"
        set /a TWEAK_SUCCESS+=1
    ) else (
        call :log_power_enhanced "NVIDIA GPU P-State tweak failed"
        set /a TWEAK_FAILED+=1
    )
) else (
    call :log_power_enhanced "NVIDIA GPU not found in registry"
)
goto :eof

:apply_all_enhanced
:: Apply all enhanced power tweaks
call :apply_cppc_tweaks
call :apply_epp_performance
call :apply_gpu_pstate
call :apply_power_throttling
call :apply_modern_standby
call :apply_coalescence_timers
goto :eof

:: ============================================================================
:: Disable Power Throttling
:: Source: Ghost-Optimizer (performanceapply)
:: Benefit: Prevents Windows from throttling CPU for power saving
:: ============================================================================
:apply_power_throttling
call :log_power_enhanced "Disabling power throttling..."

:: Disable power throttling
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling" /v "PowerThrottlingOff" /t REG_DWORD /d 1 /f >nul 2>&1

:: Disable Connected Standby (prevent idle throttling)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power" /v "CsEnabled" /t REG_DWORD /d 0 /f >nul 2>&1

:: Set platform to always on (no AOAC power management)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power" /v "PlatformAoAcOverride" /t REG_DWORD /d 0 /f >nul 2>&1

call :log_power_enhanced "Power throttling disabled"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Disable Modern Standby, Hibernation & Fast Startup
:: Source: Ghost-Optimizer (generalapply + performanceapply)
:: Benefit: Prevents wake issues, saves disk space, cleaner boot
:: ============================================================================
:apply_modern_standby
call :log_power_enhanced "Disabling hibernation and fast startup..."

:: Disable hibernation (saves disk space = RAM size)
powercfg /hibernate off >nul 2>&1

:: Disable fast startup (HiberBootEnabled)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v "HiberBootEnabled" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable SleepStudy (telemetry for sleep)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v "SleepStudyDisabled" /t REG_DWORD /d 1 /f >nul 2>&1

call :log_power_enhanced "Hibernation and fast startup disabled"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Coalescence Timer Optimization
:: Source: Ghost-Optimizer (performanceapply)
:: Benefit: Reduces timer coalescing delay for shorter DPC latency
:: ============================================================================
:apply_coalescence_timers
call :log_power_enhanced "Optimizing coalescence timers..."

:: Set global coalescence timer resolution to 1
powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP 7bc4a2f9-d8fc-4469-b07b-33eb785aaca0 1 >nul 2>&1

:: Apply
powercfg /setactive SCHEME_CURRENT >nul 2>&1

call :log_power_enhanced "Coalescence timers optimized"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Disable Spectre/Meltdown Mitigations (EXTREME profile only)
:: Source: Ghost-Optimizer (performanceapply)
:: WARNING: Reduces security — significant CPU performance gain (5-15%)
:: ============================================================================
:apply_spectre_disable
call :log_power_enhanced "WARNING: Disabling Spectre/Meltdown mitigations (EXTREME)..."

:: FeatureSettingsOverride = 3 (disable all mitigations)
:: FeatureSettingsOverrideMask = 3 (apply override)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "FeatureSettingsOverride" /t REG_DWORD /d 3 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "FeatureSettingsOverrideMask" /t REG_DWORD /d 3 /f >nul 2>&1

call :log_power_enhanced "Spectre/Meltdown mitigations disabled (restart required)"
set /a TWEAK_SUCCESS+=1
goto :eof

:log_power_enhanced
if defined LOGFILE (
    echo [%TIME%] [PowerEnh] %~1 >> "%LOGFILE%"
)
echo     [PowerEnh] %~1
goto :eof
