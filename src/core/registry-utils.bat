@echo off
:: ============================================
:: Registry Utilities Module
:: Handles registry-based optimizations
:: ============================================

if "%~1"==":apply_telemetry_tweaks" goto :apply_telemetry_tweaks
if "%~1"==":apply_gaming_tweaks" goto :apply_gaming_tweaks
if "%~1"==":apply_visual_tweaks" goto :apply_visual_tweaks
if "%~1"==":apply_kernel_input_tweaks" goto :apply_kernel_input_tweaks
if "%~1"==":reset_all" goto :reset_all
exit /b 0

:apply_telemetry_tweaks
set "MODULE_FAILURES=0"
:: Privacy and telemetry settings
call :reg_set "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" "AllowTelemetry" "REG_DWORD" "0"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" "AllowTelemetry" "REG_DWORD" "0"
call :reg_set "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" "Enabled" "REG_DWORD" "0"
call :reg_set "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" "PublishUserActivities" "REG_DWORD" "0"
call :reg_set "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" "UploadUserActivities" "REG_DWORD" "0"
call :reg_set "HKCU\SOFTWARE\Microsoft\Siuf\Rules" "NumberOfSIUFInPeriod" "REG_DWORD" "0"
call :reg_set "HKCU\SOFTWARE\Microsoft\Siuf\Rules" "PeriodInNanoSeconds" "REG_DWORD" "0"
call :reg_set "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy" "TailoredExperiencesWithDiagnosticDataEnabled" "REG_DWORD" "0"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\appDiagnostics" "Value" "REG_SZ" "Deny"
if %MODULE_FAILURES% GTR 0 exit /b 1
exit /b 0

:apply_gaming_tweaks
set "MODULE_FAILURES=0"
:: Gaming optimizations: Game Mode, DVR, MMCSS, and priority settings
call :reg_set "HKCU\SOFTWARE\Microsoft\GameBar" "AllowAutoGameMode" "REG_DWORD" "1"
call :reg_set "HKCU\SOFTWARE\Microsoft\GameBar" "AutoGameModeEnabled" "REG_DWORD" "1"
call :reg_set "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" "AppCaptureEnabled" "REG_DWORD" "0"
call :reg_set "HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR" "AllowGameDVR" "REG_DWORD" "0"
call :reg_set "HKCU\SOFTWARE\Microsoft\GameBar" "ShowStartupPanel" "REG_DWORD" "0"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "SystemResponsiveness" "REG_DWORD" "0"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "NetworkThrottlingIndex" "REG_DWORD" "4294967295"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "GPU Priority" "REG_DWORD" "8"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "Priority" "REG_DWORD" "6"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "Scheduling Category" "REG_SZ" "High"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "SFIO Priority" "REG_SZ" "High"
call :reg_set "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" "Win32PrioritySeparation" "REG_DWORD" "38"
if %MODULE_FAILURES% GTR 0 exit /b 1
exit /b 0

:apply_visual_tweaks
set "MODULE_FAILURES=0"
:: Visual effects reduction
call :reg_set "HKCU\Control Panel\Desktop" "MenuShowDelay" "REG_SZ" "0"
call :reg_set "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "EnableTransparency" "REG_DWORD" "0"
call :reg_set "HKCU\Control Panel\Desktop\WindowMetrics" "MinAnimate" "REG_SZ" "0"
call :reg_set "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" "DisallowShaking" "REG_DWORD" "1"
call :reg_set "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "SoftLandingEnabled" "REG_DWORD" "0"
call :reg_set "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "SubscribedContent-338389Enabled" "REG_DWORD" "0"
call :reg_set "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" "SystemPaneSuggestionsEnabled" "REG_DWORD" "0"
if %MODULE_FAILURES% GTR 0 exit /b 1
exit /b 0

:apply_kernel_input_tweaks
set "MODULE_FAILURES=0"
:: Kernel and input optimizations
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "GPU Priority" "REG_DWORD" "8"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "Priority" "REG_DWORD" "6"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "Scheduling Category" "REG_SZ" "High"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "SFIO Priority" "REG_SZ" "High"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "Network Throttling Index" "REG_DWORD" "4294967295"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "SystemResponsiveness" "REG_DWORD" "0"
call :reg_set "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "NetworkThrottlingIndex" "REG_DWORD" "4294967295"
call :reg_set "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" "MouseDataQueueSize" "REG_DWORD" "16"
call :reg_set "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" "Win32PrioritySeparation" "REG_DWORD" "38"
if %MODULE_FAILURES% GTR 0 exit /b 1
exit /b 0

:reset_all
set "MODULE_FAILURES=0"
echo     Resetting registry tweaks...
call :reg_delete_if_present "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" "AllowTelemetry"
call :reg_delete_if_present "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" "Enabled"
call :reg_delete_if_present "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" "AppCaptureEnabled"
call :reg_delete_if_present "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" "SystemResponsiveness"
call :reg_delete_if_present "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "GPU Priority"
call :reg_delete_if_present "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "Priority"
call :reg_delete_if_present "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" "Network Throttling Index"
call :reg_set "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" "Win32PrioritySeparation" "REG_DWORD" "2"
call :reg_delete_if_present "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" "MouseDataQueueSize"
call :reg_set "HKCU\Control Panel\Desktop" "MenuShowDelay" "REG_SZ" "400"
call :reg_delete_if_present "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize" "EnableTransparency"
if %MODULE_FAILURES% GTR 0 (
    call :log_registry "Reset registry tweaks" "FAILED - One or more required commands failed"
    exit /b 1
)
call :log_registry "Reset all registry tweaks" "SUCCESS"
exit /b 0

:reg_set
:: Safely set a registry value with backup.
set "REG_KEY=%~1"
set "REG_VALUE=%~2"
set "REG_TYPE=%~3"
set "REG_DATA=%~4"

if defined BACKUP_FOLDER (
    reg query "%REG_KEY%" /v "%REG_VALUE%" >> "%BACKUP_FOLDER%\registry_backup.txt" 2>nul
)
reg add "%REG_KEY%" /v "%REG_VALUE%" /t %REG_TYPE% /d "%REG_DATA%" /f >nul 2>&1
if errorlevel 1 (
    call :log_registry "%REG_KEY%\%REG_VALUE%=%REG_DATA%" "FAILED"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
call :log_registry "%REG_KEY%\%REG_VALUE%=%REG_DATA%" "SUCCESS"
set /a TWEAK_SUCCESS+=1
exit /b 0

:reg_delete_if_present
set "REG_KEY=%~1"
set "REG_VALUE=%~2"
reg query "%REG_KEY%" /v "%REG_VALUE%" >nul 2>&1
if errorlevel 1 (
    call :log_registry "%REG_KEY%\%REG_VALUE%" "SKIPPED - Value not present"
    set /a TWEAK_SKIPPED+=1
    exit /b 0
)
reg delete "%REG_KEY%" /v "%REG_VALUE%" /f >nul 2>&1
if errorlevel 1 (
    call :log_registry "%REG_KEY%\%REG_VALUE%" "FAILED - Could not delete value"
    set /a MODULE_FAILURES+=1
    set /a TWEAK_FAILED+=1
    exit /b 1
)
call :log_registry "%REG_KEY%\%REG_VALUE%" "DELETED"
set /a TWEAK_SUCCESS+=1
exit /b 0

:log_registry
if defined LOGFILE (
    echo [%TIME%] [Registry] %~1: %~2 >> "%LOGFILE%"
)
exit /b 0
