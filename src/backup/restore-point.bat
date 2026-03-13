@echo off
:: ============================================
:: Restore Point Module
:: Creates Windows System Restore points
:: ============================================

if "%~1"==":create_restore_point" goto :create_restore_point
goto :eof

:create_restore_point
echo     Creating System Restore Point...

:: Check if System Restore is enabled
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore" /v RPSessionInterval >nul 2>&1
if %ERRORLEVEL%==1 (
    echo     NOTE: System Restore may be disabled.
    echo     Attempting to enable...
    powershell -Command "Enable-ComputerRestore -Drive 'C:\'" 2>nul
)

:: Create restore point using PowerShell
powershell -Command "Checkpoint-Computer -Description 'Windows Optimizer Pre-Optimization' -RestorePointType 'MODIFY_SETTINGS'" 2>nul

if %ERRORLEVEL%==0 (
    echo     System Restore Point created successfully.
) else (
    echo     WARNING: Could not create System Restore Point.
    echo     This may happen if:
    echo       - System Restore is disabled
    echo       - A restore point was recently created
    echo       - Insufficient disk space
    echo.
    echo     Continuing without restore point...
)

goto :eof

:enable_system_restore
:: Enable System Restore for C: drive
powershell -Command "Enable-ComputerRestore -Drive 'C:\'" 2>nul
goto :eof

:list_restore_points
:: List available restore points
powershell -Command "Get-ComputerRestorePoint | Format-Table -Property SequenceNumber, Description, CreationTime -AutoSize"
goto :eof
