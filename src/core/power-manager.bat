@echo off
:: ============================================
:: Power Manager Module
:: Handles power plan creation and optimization
:: ============================================

if "%~1"==":apply_power_tweaks" goto :apply_power_tweaks
if "%~1"==":create_ultimate_performance" goto :create_ultimate_performance
if "%~1"==":reset_power" goto :reset_power
goto :eof

:apply_power_tweaks
:: Create and activate Ultimate Performance plan
call :create_ultimate_performance

:: Disable USB selective suspend
powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0 2>nul
powercfg /setdcvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0 2>nul

:: Disable hard disk timeout
powercfg /setacvalueindex SCHEME_CURRENT 0012ee47-9041-4b5d-9b77-535fba8b1442 6738e2c4-e8a5-4a42-b16a-e040e769756e 0 2>nul
powercfg /setdcvalueindex SCHEME_CURRENT 0012ee47-9041-4b5d-9b77-535fba8b1442 6738e2c4-e8a5-4a42-b16a-e040e769756e 0 2>nul

:: Set minimum processor state to high
powercfg /setacvalueindex SCHEME_CURRENT 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 100 2>nul
powercfg /setdcvalueindex SCHEME_CURRENT 54533251-82be-4824-96c1-47b60b740d00 893dee8e-2bef-41e0-89c6-b55d0929964c 50 2>nul

:: Set maximum processor state to 100%
powercfg /setacvalueindex SCHEME_CURRENT 54533251-82be-4824-96c1-47b60b740d00 bc5038f7-23e0-4960-96da-33abaf5935ec 100 2>nul
powercfg /setdcvalueindex SCHEME_CURRENT 54533251-82be-4824-96c1-47b60b740d00 bc5038f7-23e0-4960-96da-33abaf5935ec 100 2>nul

:: Disable core parking (modern CPUs)
powercfg /setacvalueindex SCHEME_CURRENT 54533251-82be-4824-96c1-47b60b740d00 0cc5b647-c1df-4637-891a-dec35c318583 100 2>nul

:: Apply changes
powercfg /setactive SCHEME_CURRENT

call :log_power "Power tweaks applied"
set /a TWEAK_SUCCESS+=1
goto :eof

:create_ultimate_performance
:: Check if Ultimate Performance exists
powercfg /list | findstr /i "Ultimate Performance" >nul
if %ERRORLEVEL%==0 (
    :: Activate existing
    for /f "tokens=4" %%a in ('powercfg /list ^| findstr /i "Ultimate Performance"') do (
        powercfg /setactive %%a
    )
    goto :eof
)

:: Try to unhide Ultimate Performance
powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
if %ERRORLEVEL%==0 (
    :: Activate the new plan
    for /f "tokens=4" %%a in ('powercfg /list ^| findstr /i "Ultimate Performance"') do (
        powercfg /setactive %%a
    )
) else (
    :: Fall back to High Performance
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>nul
    if %ERRORLEVEL%==1 (
        :: If that fails, try by name
        for /f "tokens=4" %%a in ('powercfg /list ^| findstr /i "High performance"') do (
            powercfg /setactive %%a
        )
    )
)
goto :eof

:reset_power
:: Reset to Balanced
powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e
call :log_power "Power plan reset to Balanced"
goto :eof

:log_power
if defined LOGFILE (
    echo [%TIME%] [Power] %~1 >> "%LOGFILE%"
)
echo     [Power] %~1
goto :eof
