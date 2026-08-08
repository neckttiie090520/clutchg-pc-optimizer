@echo off
setlocal EnableExtensions EnableDelayedExpansion

if /i "%~1"==":apply_power_tweaks" goto :apply_power_tweaks
if /i "%~1"==":reset_all" goto :reset_all
if not "%~1"=="" goto :usage_error
endlocal & exit /b 0

:apply_power_tweaks
:: Change only the active scheme. The journaled transaction records the
:: original active GUID, so rollback can restore it without creating a clone.
powercfg /setactive SCHEME_MIN >nul 2>&1
if errorlevel 1 (
    echo ERROR: Could not activate the High performance power scheme.
    endlocal & exit /b 1
)
echo     [Power] High performance scheme activated
endlocal & exit /b 0

:reset_all
powercfg /setactive SCHEME_BALANCED >nul 2>&1
if errorlevel 1 (
    echo ERROR: Could not activate the Balanced power scheme.
    endlocal & exit /b 1
)
echo     [Power] Balanced scheme activated
endlocal & exit /b 0

:usage_error
echo Usage: power-manager.bat :apply_power_tweaks^|:reset_all
endlocal & exit /b 2
