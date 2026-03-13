@echo off
:: ============================================
:: Rollback Module
:: Restore system from backup
:: ============================================

if "%~1"==":restore_from_backup" goto :restore_from_backup
if "%~1"==":restore_bcd" goto :restore_bcd
if "%~1"==":restore_registry" goto :restore_registry
goto :eof

:restore_from_backup
:: Restore from a specific backup folder
set "BACKUP_NAME=%~2"
set "RESTORE_DIR=%~dp0..\backups\%BACKUP_NAME%"

if not exist "%RESTORE_DIR%" (
    echo ERROR: Backup folder not found: %RESTORE_DIR%
    exit /b 1
)

echo.
echo  Restoring from: %RESTORE_DIR%
echo.

:: Restore registry files
if exist "%RESTORE_DIR%\*.reg" (
    echo  Restoring registry...
    for %%f in ("%RESTORE_DIR%\*.reg") do (
        reg import "%%f" >nul 2>&1
        echo     Imported: %%~nxf
    )
)

:: Restore BCD
if exist "%RESTORE_DIR%\bcd_backup" (
    echo  Restoring boot configuration...
    bcdedit /import "%RESTORE_DIR%\bcd_backup" >nul 2>&1
    if %ERRORLEVEL%==0 (
        echo     BCD restored successfully
    ) else (
        echo     WARNING: BCD restore failed - may need manual reset
    )
)

:: Restore power plan
if exist "%RESTORE_DIR%\power_plan.pow" (
    echo  Restoring power plan...
    powercfg /import "%RESTORE_DIR%\power_plan.pow" >nul 2>&1
)

echo.
echo  Restore complete. A restart is required.
echo.
exit /b 0

:restore_bcd
:: Reset BCD to defaults only
echo  Resetting BCDEdit to defaults...

bcdedit /deletevalue disabledynamictick >nul 2>&1
bcdedit /deletevalue useplatformtick >nul 2>&1
bcdedit /deletevalue tscsyncpolicy >nul 2>&1
bcdedit /deletevalue uselegacyapicmode >nul 2>&1
bcdedit /deletevalue usephysicaldestination >nul 2>&1
bcdedit /deletevalue hypervisorlaunchtype >nul 2>&1
bcdedit /set nx OptIn >nul 2>&1
bcdedit /set nointegritychecks off >nul 2>&1
bcdedit /set testsigning off >nul 2>&1

echo  BCDEdit reset complete.
goto :eof

:restore_registry
:: Restore from registry backup file
set "REG_FILE=%~2"

if not exist "%REG_FILE%" (
    echo ERROR: Registry file not found: %REG_FILE%
    exit /b 1
)

reg import "%REG_FILE%" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo  Registry restored from: %REG_FILE%
) else (
    echo  ERROR: Failed to restore registry
    exit /b 1
)
goto :eof
