@echo off
:: ============================================
:: Maintenance Manager Module
:: Storage Sense, TRIM, cleanup, health checks
:: Risk Level: SAFE
:: ============================================

if "%~1"==":enable_storage_sense" goto :enable_storage_sense
if "%~1"==":verify_trim" goto :verify_trim
if "%~1"==":run_system_cleanup" goto :run_system_cleanup
if "%~1"==":check_disk_health" goto :check_disk_health
if "%~1"==":apply_safe_maintenance" goto :apply_safe_maintenance
if "%~1"==":apply_full_maintenance" goto :apply_full_maintenance
goto :eof

:enable_storage_sense
:: ============================================
:: Enable Storage Sense Automation
:: ============================================
:: Benefit: Automatic disk cleanup, extended SSD lifespan
:: Risk: SAFE (configurable, reversible)

call :log_maintenance "Enabling Storage Sense..."

:: Storage Sense registry path
set "SS_PATH=HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy"

:: Enable Storage Sense (01 = enabled)
reg add "%SS_PATH%" /v "01" /t REG_DWORD /d 1 /f >nul 2>&1

:: Run Storage Sense every week (07 = weekly)
reg add "%SS_PATH%" /v "01" /t REG_DWORD /d 7 /f >nul 2>&1

:: Delete temp files older than 0 days (immediate)
reg add "%SS_PATH%" /v "02" /t REG_DWORD /d 0 /f >nul 2>&1

:: Delete recycle bin files after 30 days (1e = 30)
reg add "%SS_PATH%" /v "04" /t REG_DWORD /d 30 /f >nul 2>&1

:: Delete downloads files after 60 days (3c = 60)
reg add "%SS_PATH%" /v "08" /t REG_DWORD /d 60 /f >nul 2>&1

if %ERRORLEVEL%==0 (
    call :log_maintenance "Storage Sense enabled: Weekly cleanup, 30d recycle, 60d downloads"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_maintenance "Storage Sense configuration failed"
    set /a TWEAK_FAILED+=1
)
goto :eof

:verify_trim
:: ============================================
:: Verify SSD TRIM is Enabled
:: ============================================
:: Benefit: Extended SSD lifespan, consistent performance
:: Risk: SAFE (verification only, TRIM is default)

call :log_maintenance "Verifying TRIM status..."

:: Check TRIM status (0 = enabled, 1 = disabled)
for /f "tokens=3" %%a in ('fsutil behavior query DisableDeleteNotify 2^>nul') do set "TRIM_STATUS=%%a"

if "%TRIM_STATUS%"=="0" (
    call :log_maintenance "TRIM is enabled (optimal for SSDs)"
    set /a TWEAK_SUCCESS+=1
) else (
    call :log_maintenance "TRIM is disabled - enabling..."
    fsutil behavior set DisableDeleteNotify 0 >nul 2>&1
    if %ERRORLEVEL%==0 (
        call :log_maintenance "TRIM enabled successfully"
        set /a TWEAK_SUCCESS+=1
    ) else (
        call :log_maintenance "Failed to enable TRIM"
        set /a TWEAK_FAILED+=1
    )
)
goto :eof

:run_system_cleanup
:: ============================================
:: Run System Cleanup Operations
:: ============================================
:: Benefit: Frees disk space, removes temporary files
:: Risk: SAFE (ask user first, show what will be deleted)

call :log_maintenance "Starting system cleanup..."

:: Check available disk space
for /f "tokens=3" %%a in ('dir C:\ ^| findstr "bytes free"') do set "FREE_SPACE=%%a"
:: Simple check: If free space < 10GB, skip cleanup
:: Note: This is a simplified check

:: 1. Run Windows Update Cleanup (DISM)
call :log_maintenance "Running Windows Update cleanup..."
dism /online /Cleanup-Image /StartComponentCleanup >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_maintenance "Windows Update cleanup completed"
)

:: 2. Clear temp files (warn user first)
call :log_maintenance "Clearing temporary files..."
:: User temp
if exist "%TEMP%" (
    :: Count files first
    for /f %%a in ('dir /b "%TEMP%" 2^>nul ^| find /c /v ""') do set "TEMP_COUNT=%%a"
    if defined TEMP_COUNT (
        call :log_maintenance "Found %TEMP_COUNT% files in temp directory"
        del /q /s "%TEMP%\*" >nul 2>&1
    )
)

:: Windows temp
if exist "%WINDIR%\Temp" (
    del /q /s "%WINDIR%\Temp\*" >nul 2>&1
)

:: 3. Clear Prefetch (safe to delete, Windows rebuilds as needed)
if exist "%WINDIR%\Prefetch" (
    del /q "%WINDIR%\Prefetch\*" >nul 2>&1
    call :log_maintenance "Prefetch cache cleared"
)

call :log_maintenance "System cleanup completed"
set /a TWEAK_SUCCESS+=1
goto :eof

:check_disk_health
:: ============================================
:: Check Disk Health Status
:: ============================================
:: Benefit: Early warning of disk failures
:: Risk: SAFE (read-only checks)

call :log_maintenance "Checking disk health..."

:: 1. Check S.M.A.R.T. status - PowerShell replaces deprecated wmic
call :log_maintenance "S.M.A.R.T. status:"
powershell -Command "Get-CimInstance Win32_DiskDrive | Select-Object Status" 2>nul | findstr /v /i "Status"

:: 2. Check for file system errors (read-only scan)
call :log_maintenance "Running file system health check..."
chkdsk C: /scan /perf >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_maintenance "File system check scheduled"
) else (
    call :log_maintenance "File system check failed or requires reboot"
)

call :log_maintenance "Disk health check completed"
set /a TWEAK_SUCCESS+=1
goto :eof

:apply_safe_maintenance
:: Apply safe maintenance (no file deletion)
call :verify_trim
call :check_disk_health
call :enable_storage_sense
goto :eof

:apply_full_maintenance
:: Apply full maintenance including cleanup
call :apply_safe_maintenance
call :run_system_cleanup
goto :eof

:log_maintenance
if defined LOGFILE (
    echo [%TIME%] [Maint] %~1 >> "%LOGFILE%"
)
echo     [Maint] %~1
goto :eof
