@echo off
:: ============================================================================
:: ClutchG System Restore Point Module
:: ============================================================================
:: Set CLUTCHG_DRY_RUN=1 or pass --plan to print commands without mutation.
:: ============================================================================

setlocal EnableExtensions
set "COMMAND=%~1"
set "PLAN_MODE=0"
if /i "%CLUTCHG_DRY_RUN%"=="1" set "PLAN_MODE=1"
if /i "%~2"=="--plan" set "PLAN_MODE=1"

if /i "%COMMAND%"==":create_restore_point" goto :create_restore_point
if /i "%COMMAND%"=="create_restore_point" goto :create_restore_point
if /i "%COMMAND%"==":enable_system_restore" goto :enable_system_restore
if /i "%COMMAND%"=="enable_system_restore" goto :enable_system_restore
if /i "%COMMAND%"==":list_restore_points" goto :list_restore_points
if /i "%COMMAND%"=="list_restore_points" goto :list_restore_points
if not defined COMMAND goto :usage

echo ERROR: Unknown restore-point command: %COMMAND%
goto :usage_error

:create_restore_point
if "%PLAN_MODE%"=="1" (
    echo PLAN^|QUERY^|reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore" /v RPSessionInterval
    echo PLAN^|MUTATE^|powershell -NoProfile -Command "Checkpoint-Computer -Description 'ClutchG Pre-Optimization' -RestorePointType 'MODIFY_SETTINGS'"
    endlocal & exit /b 0
)
echo     Creating System Restore Point...
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore" /v RPSessionInterval >nul 2>&1
if errorlevel 1 (
    echo ERROR: System Restore is disabled or unavailable. It is not enabled implicitly.
    endlocal & exit /b 1
)
powershell -NoProfile -Command "Checkpoint-Computer -Description 'ClutchG Pre-Optimization' -RestorePointType 'MODIFY_SETTINGS'" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Could not create System Restore Point.
    endlocal & exit /b 1
)
echo     System Restore Point created successfully.
endlocal & exit /b 0

:enable_system_restore
if "%PLAN_MODE%"=="1" (
    echo PLAN^|MUTATE^|powershell -NoProfile -Command "Enable-ComputerRestore -Drive 'C:\'"
    endlocal & exit /b 0
)
powershell -NoProfile -Command "Enable-ComputerRestore -Drive 'C:\'" >nul 2>&1
set "RETURN_CODE=%ERRORLEVEL%"
endlocal & exit /b %RETURN_CODE%

:list_restore_points
if "%PLAN_MODE%"=="1" (
    echo PLAN^|QUERY^|powershell -NoProfile -Command "Get-ComputerRestorePoint"
    endlocal & exit /b 0
)
powershell -NoProfile -Command "Get-ComputerRestorePoint | Format-Table -Property SequenceNumber, Description, CreationTime -AutoSize"
set "RETURN_CODE=%ERRORLEVEL%"
endlocal & exit /b %RETURN_CODE%

:usage
echo Usage: restore-point.bat create_restore_point [--plan]
echo        restore-point.bat enable_system_restore [--plan]
echo        restore-point.bat list_restore_points [--plan]
endlocal & exit /b 0

:usage_error
echo Usage: restore-point.bat COMMAND [--plan]
endlocal & exit /b 2
