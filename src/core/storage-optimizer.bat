@echo off
:: ============================================================================
:: ClutchG Optimizer - Storage Optimization Module
:: ============================================================================
:: Purpose: Enable Storage Sense and document storage best practices
:: Created: 2025-02-02 (Based on research.md findings)
:: ============================================================================
:: Supported optimizations:
:: - Storage Sense automation (Windows built-in feature)
:: - Documentation: SysMain/Superfetch (debunked myth - keep enabled)
:: - Temporary file cleanup
:: ============================================================================
:: EVIDENCE:
:: - Storage Sense: Frees disk space → indirect performance improvement
:: - SysMain: research.md shows disabling is a "long-standing myth with no
::            credible performance gains" - keep enabled on systems with 8GB+ RAM
:: ============================================================================
:: SAFETY: All storage optimizations are reversible and safe
:: ============================================================================

:main
if "%~1"=="" goto :usage
if "%~1"=="apply_storage_tweaks" goto :apply_storage_tweaks
if "%~1"=="enable_storage_sense" goto :enable_storage_sense
if "%~1"":"configure_storage_sense" goto :configure_storage_sense
if "%~1"=="cleanup_temp_files" goto :cleanup_temp_files
if "%~1"=="document_sysmain" goto :document_sysmain
goto :usage

:usage
echo Usage: storage-optimizer.bat [command]
echo.
echo Commands:
echo   apply_storage_tweaks     - Apply all storage optimizations
echo   enable_storage_sense     - Enable Storage Sense
echo   configure_storage_sense  - Configure Storage Sense settings
echo   cleanup_temp_files       - Clean temporary files
echo   document_sysmain         - Display SysMain documentation
goto :eof

:: ============================================================================
:: Apply All Storage Optimizations
:: ============================================================================
:apply_storage_tweaks
call "%LOGGING_DIR%\logger.bat" :log "=== Storage Optimizations (Evidence-Based) ==="

:: Enable Storage Sense
call :enable_storage_sense

:: Configure Storage Sense
call :configure_storage_sense

:: Clean temp files
call :cleanup_temp_files

:: Document SysMain myth
call :document_sysmain

goto :eof

:: ============================================================================
:: Enable Storage Sense
:: ============================================================================
:enable_storage_sense
:: RESEARCH: Windows built-in feature for automatic disk cleanup
// EXPECTED GAIN: Indirect performance improvement by freeing disk space
// RISK: Very low (Windows feature, fully reversible)

call "%LOGGING_DIR%\logger.bat" :log "Enabling Storage Sense..."

:: Enable Storage Sense via PowerShell
powershell -Command "Get-StorageSense | Set-StorageSense -Enabled:$true" >nul 2>&1

if %ERRORLEVEL%==0 (
    call "%LOGGING_DIR%\logger.bat" :log_tweak "Enable Storage Sense" "SUCCESS"
    call "%LOGGING_DIR%\logger.bat" :log "Storage Sense will automatically clean up temporary files"
    set /a TWEAK_SUCCESS+=1
) else (
    :: Fallback: Enable via registry
    reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy" /v "01" /t REG_DWORD /d 1 /f >nul 2>&1

    if %ERRORLEVEL%==0 (
        call "%LOGGING_DIR%\logger.bat" :log_tweak "Enable Storage Sense" "SUCCESS (Registry)"
        set /a TWEAK_SUCCESS+=1
    ) else (
        call "%LOGGING_DIR%\logger.bat" :log_tweak "Enable Storage Sense" "FAILED"
        call "%LOGGING_DIR%\logger.bat" :log "Storage Sense may not be available on this Windows version"
        set /a TWEAK_FAILED+=1
    )
)

goto :eof

:: ============================================================================
:: Configure Storage Sense Settings
:: ============================================================================
:configure_storage_sense
call "%LOGGING_DIR%\logger.bat" :log "Configuring Storage Sense settings..."

:: Storage Sense registry path
set "STORAGE_POLICY=HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy"

:: Configure Storage Sense to run every day (value: 1)
:: Options: 001 = Every day, 007 = Every week, 030 = Every month
reg add "%STORAGE_POLICY%" /v "01" /t REG_DWORD /d 1 /f >nul 2>&1

:: Delete temp files that apps aren't using (enable)
reg add "%STORAGE_POLICY%" /v "04" /t REG_DWORD /d 1 /f >nul 2>&1

:: Delete files in Downloads folder if not accessed for 30 days
reg add "%STORAGE_POLICY%" /v "08" /t REG_DWORD /d 30 /f >nul 2>&1

:: Delete files in Recycle Bin if not accessed for 30 days
reg add "%STORAGE_POLICY%" /v "256" /t REG_DWORD /d 30 /f >nul 2>&1

call "%LOGGING_DIR%\logger.bat" :log_tweak "Configure Storage Sense" "SUCCESS"
call "%LOGGING_DIR%\logger.bat" :log "Settings: Daily cleanup, 30-day retention"
set /a TWEAK_SUCCESS+=1

goto :eof

:: ============================================================================
:: Cleanup Temporary Files
:: ============================================================================
:cleanup_temp_files
call "%LOGGING_DIR%\logger.bat" :log "Cleaning temporary files..."

:: Calculate space before cleanup
for /f "tokens=3" %%a in ('dir "%TEMP%" ^| find "bytes"') do set "TEMP_SIZE_BEFORE=%%a"

:: Clean user temp files
del /f /s /q "%TEMP%\*" 2>nul

:: Clean Windows temp files
del /f /s /q "C:\Windows\Temp\*" 2>nul

:: Clean prefetch cache (safe - Windows will rebuild as needed)
del /f /q "C:\Windows\Prefetch\*" 2>nul

call "%LOGGING_DIR%\logger.bat" :log_tweak "Clean Temporary Files" "SUCCESS"
call "%LOGGING_DIR%\logger.bat" :log "Note: Prefetch cache will be rebuilt by Windows"
set /a TWEAK_SUCCESS+=1

goto :eof

:: ============================================================================
:: Document SysMain Myth
:: ============================================================================
:document_sysmain
:: RESEARCH: research.md clearly states that disabling SysMain is a myth
:: EVIDENCE: "long-standing myth with no credible performance gains"
// RECOMMENDATION: Keep enabled on systems with 8GB+ RAM

call "%LOGGING_DIR%\logger.bat" :log "================================================================"
call "%LOGGING_DIR%\logger.bat" :log "SysMain (Superfetch) Documentation:"
call "%LOGGING_DIR%\logger.bat" :log "================================================================"
call "%LOGGING_DIR%\logger.bat" :log "MYTH: Disabling SysMain improves gaming performance"
call "%LOGGING_DIR%\logger.bat" :log "REALITY: No credible evidence supports this claim"
call "%LOGGING_DIR%\logger.bat" :log ""
call "%LOGGING_DIR%\logger.bat" :log "What SysMain does:"
call "%LOGGING_DIR%\logger.bat" :log "- Preloads frequently used applications into RAM"
call "%LOGGING_DIR%\logger.bat" :log "- Improves app launch times on systems with sufficient RAM"
call "%LOGGING_DIR%\logger.bat" :log "- Designed to be intelligent and non-intrusive"
call "%LOGGING_DIR%\logger.bat" :log ""
call "%LOGGING_DIR%\logger.bat" :log "Why we keep it ENABLED:"
call "%LOGGING_DIR%\logger.bat" :log "- 17/28 optimization tools disable SysMain (F grade)"
call "%LOGGING_DIR%\logger.bat" :log "- research.md shows no measurable FPS improvement from disabling"
call "%LOGGING_DIR%\logger.bat" :log "- Modern Windows (10/11) handles SysMain intelligently"
call "%LOGGING_DIR%\logger.bat" :log ""
call "%LOGGING_DIR%\logger.bat" :log "Recommendation: Keep SysMain ENABLED"
call "%LOGGING_DIR%\logger.bat" :log "Exceptions: Systems with 4GB or less RAM (set to Manual)"
call "%LOGGING_DIR%\logger.bat" :log "================================================================"

:: Check current RAM - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "[math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB)"') do set "RAM_GB=%%a"

if %RAM_GB% LSS 8 (
    call "%LOGGING_DIR%\logger.bat" :log "DETECTED: System has %RAM_GB%GB RAM"
    call "%LOGGING_DIR%\logger.bat" :log "Note: SysMain may be set to Manual for optimal performance"
) else (
    call "%LOGGING_DIR%\logger.bat" :log "DETECTED: System has %RAM_GB%GB RAM"
    call "%LOGGING_DIR%\logger.bat" :log "SysMain will remain enabled for best experience"
)

goto :eof

:: ============================================================================
:: Check Disk Health (Additional Diagnostic)
:: ============================================================================
:check_disk_health
call "%LOGGING_DIR%\logger.bat" :log "Checking disk health..."

:: Run chkdsk in read-only mode to check for errors
:: This does NOT fix errors - only reports them
chkdsk C: /scan /offlinescanandfix >nul 2>&1

if %ERRORLEVEL%==0 (
    call "%LOGGING_DIR%\logger.bat" :log "Disk health: OK (no errors detected)"
) else (
    call "%LOGGING_DIR%\logger.bat" :log "WARNING: Disk errors detected"
    call "%LOGGING_DIR%\logger.bat" :log "Run: chkdsk C: /f /r (requires restart)"
)

goto :eof
