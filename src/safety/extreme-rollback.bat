@echo off
:: ============================================================================
:: EXTREME Profile Exact-State Rollback
:: ============================================================================
:: Restores a committed pre-mutation backup. It does not guess Windows defaults.
:: Usage: extreme-rollback.bat BACKUP_ID [--plan]
:: ============================================================================

setlocal EnableExtensions
set "BACKUP_ID=%~1"
set "PLAN_ARGUMENT=%~2"

if not defined BACKUP_ID goto :usage
if /i "%BACKUP_ID%"=="--plan" goto :usage
if /i not "%PLAN_ARGUMENT%"=="" if /i not "%PLAN_ARGUMENT%"=="--plan" goto :usage_error

call "%~dp0rollback.bat" restore_from_backup "%BACKUP_ID%" %PLAN_ARGUMENT%
set "RETURN_CODE=%ERRORLEVEL%"
endlocal & exit /b %RETURN_CODE%

:usage
echo Usage: extreme-rollback.bat BACKUP_ID [--plan]
echo Restores all recorded registry, service, BCD, and power components.
endlocal & exit /b 2

:usage_error
echo ERROR: Unknown argument: %PLAN_ARGUMENT%
goto :usage
