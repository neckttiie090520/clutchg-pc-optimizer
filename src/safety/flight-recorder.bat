@echo off
:: ============================================================================
:: ClutchG Flight Recorder Command Contract
:: ============================================================================
:: Stable facade for complete backup transactions and exact rollback.
:: Set CLUTCHG_DRY_RUN=1 or pass --plan to print actions without mutation.
:: ============================================================================

setlocal EnableExtensions EnableDelayedExpansion
set "COMMAND=%~1"
set "PLAN_MODE=0"
if /i "%CLUTCHG_DRY_RUN%"=="1" set "PLAN_MODE=1"
if /i "%~2"=="--plan" set "PLAN_MODE=1"
if /i "%~3"=="--plan" set "PLAN_MODE=1"

if /i "%COMMAND%"==":create_registry_snapshot" goto :dispatch_create_snapshot
if /i "%COMMAND%"=="create_registry_snapshot" goto :dispatch_create_snapshot
if /i "%COMMAND%"==":create_snapshot" goto :dispatch_create_snapshot
if /i "%COMMAND%"=="create_snapshot" goto :dispatch_create_snapshot
if /i "%COMMAND%"==":create_restore_point" goto :dispatch_create_restore_point
if /i "%COMMAND%"=="create_restore_point" goto :dispatch_create_restore_point
if /i "%COMMAND%"==":restore_registry_snapshot" goto :dispatch_restore_snapshot
if /i "%COMMAND%"=="restore_registry_snapshot" goto :dispatch_restore_snapshot
if /i "%COMMAND%"==":restore_snapshot" goto :dispatch_restore_snapshot
if /i "%COMMAND%"=="restore_snapshot" goto :dispatch_restore_snapshot
if /i "%COMMAND%"==":list_snapshots" goto :dispatch_list_snapshots
if /i "%COMMAND%"=="list_snapshots" goto :dispatch_list_snapshots
if /i "%COMMAND%"==":capture_registry_state" goto :unsupported_partial_capture
if /i "%COMMAND%"=="capture_registry_state" goto :unsupported_partial_capture
if not defined COMMAND goto :usage

echo ERROR: Unknown flight-recorder command: %COMMAND%
goto :usage_error

:dispatch_create_snapshot
call :create_snapshot
set "RETURN_CODE=!ERRORLEVEL!"
set "EXPORTED_BACKUP_FOLDER=!BACKUP_FOLDER!"
set "EXPORTED_BACKUP_ID=!BACKUP_ID!"
set "EXPORTED_BACKUP_READY=!CLUTCHG_BACKUP_READY!"
for %%R in (!RETURN_CODE!) do endlocal & set "BACKUP_FOLDER=%EXPORTED_BACKUP_FOLDER%" & set "BACKUP_ID=%EXPORTED_BACKUP_ID%" & set "CLUTCHG_BACKUP_READY=%EXPORTED_BACKUP_READY%" & exit /b %%R

:dispatch_create_restore_point
call :create_restore_point
set "RETURN_CODE=!ERRORLEVEL!"
for %%R in (!RETURN_CODE!) do endlocal & exit /b %%R

:dispatch_restore_snapshot
call :restore_snapshot "%~2"
set "RETURN_CODE=!ERRORLEVEL!"
for %%R in (!RETURN_CODE!) do endlocal & exit /b %%R

:dispatch_list_snapshots
call :list_snapshots
set "RETURN_CODE=!ERRORLEVEL!"
for %%R in (!RETURN_CODE!) do endlocal & exit /b %%R

:unsupported_partial_capture
echo ERROR: Partial registry capture is not a restorable transaction.
echo Use create_snapshot before mutation.
endlocal & exit /b 2

:usage
echo Usage: flight-recorder.bat COMMAND [BACKUP_ID] [--plan]
echo.
echo Commands:
echo   create_snapshot              Create a complete journaled backup
echo   create_restore_point         Create a Windows restore point
echo   restore_snapshot BACKUP_ID   Restore one committed backup leaf
echo   list_snapshots               List committed backup IDs
endlocal & exit /b 0

:usage_error
call :usage
exit /b 2

:create_snapshot
set "PLAN_ARGUMENT="
if "!PLAN_MODE!"=="1" set "PLAN_ARGUMENT=--plan"
call "%~dp0..\backup\backup-registry.bat" create_backup !PLAN_ARGUMENT!
exit /b !ERRORLEVEL!

:create_restore_point
set "PLAN_ARGUMENT="
if "!PLAN_MODE!"=="1" set "PLAN_ARGUMENT=--plan"
call "%~dp0..\backup\restore-point.bat" create_restore_point !PLAN_ARGUMENT!
exit /b !ERRORLEVEL!

:restore_snapshot
set "REQUESTED_BACKUP_ID=%~1"
if not defined REQUESTED_BACKUP_ID (
    echo ERROR: restore_snapshot requires an exact backup leaf ID.
    exit /b 2
)
set "PLAN_ARGUMENT="
if "!PLAN_MODE!"=="1" set "PLAN_ARGUMENT=--plan"
call "%~dp0rollback.bat" restore_from_backup "!REQUESTED_BACKUP_ID!" !PLAN_ARGUMENT!
exit /b !ERRORLEVEL!

:list_snapshots
if defined BACKUPS_DIR (
    for %%D in ("%BACKUPS_DIR%") do set "BACKUPS_ROOT=%%~fD"
) else (
    for %%D in ("%~dp0..\backups") do set "BACKUPS_ROOT=%%~fD"
)
if not exist "!BACKUPS_ROOT!" (
    echo No committed backups found.
    exit /b 0
)
set "SNAPSHOT_COUNT=0"
for /d %%D in ("!BACKUPS_ROOT!\*") do call :list_one_snapshot "%%~fD" "%%~nxD"
if "!SNAPSHOT_COUNT!"=="0" echo No committed backups found.
exit /b 0

:list_one_snapshot
set "CANDIDATE_DIR=%~1"
set "CANDIDATE_ID=%~2"
echo(!CANDIDATE_ID!| findstr /r /x "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]_[0-9][0-9]-[0-9][0-9]-[0-9][0-9]" >nul 2>&1
if errorlevel 1 exit /b 0
if not exist "!CANDIDATE_DIR!\manifest.ini" exit /b 0
if not exist "!CANDIDATE_DIR!\journal.log" exit /b 0
findstr /x /c:"backup_id=!CANDIDATE_ID!" "!CANDIDATE_DIR!\manifest.ini" >nul 2>&1
if errorlevel 1 exit /b 0
findstr /x /c:"state=COMMITTED" "!CANDIDATE_DIR!\manifest.ini" >nul 2>&1
if errorlevel 1 exit /b 0
findstr /b /c:"END|COMMITTED|" "!CANDIDATE_DIR!\journal.log" >nul 2>&1
if errorlevel 1 exit /b 0
echo !CANDIDATE_ID!
set /a SNAPSHOT_COUNT+=1
exit /b 0
