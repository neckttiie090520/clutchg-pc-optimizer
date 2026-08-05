@echo off
:: ============================================================================
:: Recovery Mechanism Verification Harness
:: ============================================================================
:: Proves that the capture/restore mechanism used by backup-registry.bat and
:: rollback.bat actually round-trips a registry value — the one claim plan mode
:: cannot establish, because plan mode never calls reg add.
::
:: This operates ONLY on a scratch key it creates and deletes itself:
::     HKCU\Software\ClutchG-VV-Scratch
:: It never touches a real Windows setting, so it is safe on a dev machine and
:: needs no VM. The capture and restore blocks below are copied verbatim from the
:: shipped engine; if they drift, test_recovery_mechanism_contract.py fails.
::
:: Usage: verify-recovery-mechanism.bat <state-dir>
:: Exit:  0 = every case round-tripped, 1 = a case failed
:: ============================================================================

setlocal EnableExtensions EnableDelayedExpansion

set "STATE_DIR=%~1"
if not defined STATE_DIR (
    echo ERROR: state directory required.
    endlocal & exit /b 2
)
if not exist "!STATE_DIR!" mkdir "!STATE_DIR!" >nul 2>&1

set "SCRATCH_KEY=HKCU\Software\ClutchG-VV-Scratch"
set "SCRATCH_VALUE=ProbeValue"
set /a CASES_PASSED=0
set /a CASES_FAILED=0

call :cleanup_scratch

:: --- Case 1: value exists with data; mutate it; restore must return the data --
call :case_existing_value
:: --- Case 2: value absent, key present; mutate; restore must remove value ----
call :case_absent_value
:: --- Case 3: key absent entirely; mutate; restore must remove the key --------
call :case_absent_key

call :cleanup_scratch

echo RESULT^|passed=!CASES_PASSED!^|failed=!CASES_FAILED!
if !CASES_FAILED! GTR 0 (
    endlocal & exit /b 1
)
endlocal & exit /b 0

:: ============================================================================
:case_existing_value
set "CASE=existing_value"
reg add "!SCRATCH_KEY!" /v "!SCRATCH_VALUE!" /t REG_DWORD /d 7 /f >nul 2>&1
call :capture "!CASE!"
:: Mutate, exactly as a tweak would.
reg add "!SCRATCH_KEY!" /v "!SCRATCH_VALUE!" /t REG_DWORD /d 999 /f >nul 2>&1
call :restore "!CASE!"
call :read_current
if "!CURRENT_FOUND!"=="1" if "!CURRENT_DATA!"=="0x7" (
    echo CASE^|!CASE!^|PASS^|restored=0x7
    set /a CASES_PASSED+=1
    call :cleanup_scratch
    exit /b 0
)
echo CASE^|!CASE!^|FAIL^|found=!CURRENT_FOUND!^|data=!CURRENT_DATA!^|expected=0x7
set /a CASES_FAILED+=1
call :cleanup_scratch
exit /b 0

:case_absent_value
set "CASE=absent_value"
:: Key exists, probe value does not.
reg add "!SCRATCH_KEY!" /v "Placeholder" /t REG_DWORD /d 1 /f >nul 2>&1
call :capture "!CASE!"
reg add "!SCRATCH_KEY!" /v "!SCRATCH_VALUE!" /t REG_DWORD /d 555 /f >nul 2>&1
call :restore "!CASE!"
call :read_current
reg query "!SCRATCH_KEY!" >nul 2>&1 && set "KEY_STILL=1" || set "KEY_STILL=0"
if "!CURRENT_FOUND!"=="0" if "!KEY_STILL!"=="1" (
    echo CASE^|!CASE!^|PASS^|value-removed-key-kept
    set /a CASES_PASSED+=1
    call :cleanup_scratch
    exit /b 0
)
echo CASE^|!CASE!^|FAIL^|value_found=!CURRENT_FOUND!^|key_present=!KEY_STILL!
set /a CASES_FAILED+=1
call :cleanup_scratch
exit /b 0

:case_absent_key
set "CASE=absent_key"
call :cleanup_scratch
call :capture "!CASE!"
reg add "!SCRATCH_KEY!" /v "!SCRATCH_VALUE!" /t REG_DWORD /d 42 /f >nul 2>&1
call :restore "!CASE!"
reg query "!SCRATCH_KEY!" >nul 2>&1 && set "KEY_STILL=1" || set "KEY_STILL=0"
if "!KEY_STILL!"=="0" (
    echo CASE^|!CASE!^|PASS^|key-removed
    set /a CASES_PASSED+=1
    exit /b 0
)
echo CASE^|!CASE!^|FAIL^|key-still-present
set /a CASES_FAILED+=1
call :cleanup_scratch
exit /b 0

:: ============================================================================
:: Capture — copied verbatim from backup-registry.bat :backup_registry_value
:: ============================================================================
:capture
set "COMPONENT_ID=%~1"
set "REGISTRY_KEY=!SCRATCH_KEY!"
set "REGISTRY_VALUE=!SCRATCH_VALUE!"
set "ARTIFACT=!STATE_DIR!\!COMPONENT_ID!.state"
set "KEY_EXISTED=0"
set "VALUE_FOUND=0"
set "VALUE_EXISTED=0"
set "VALUE_TYPE="
set "VALUE_DATA="
reg query "!REGISTRY_KEY!" >nul 2>&1 && set "KEY_EXISTED=1"
for /f "skip=2 tokens=1,2,*" %%A in ('reg query "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" 2^>nul') do (
    if /i "%%A"=="!REGISTRY_VALUE!" (
        set "VALUE_FOUND=1"
        set "VALUE_TYPE=%%B"
        set "VALUE_DATA=%%C"
    )
)
if "!VALUE_FOUND!"=="1" set "VALUE_EXISTED=1"
>"!ARTIFACT!" echo key_existed=!KEY_EXISTED!
>>"!ARTIFACT!" echo value_existed=!VALUE_EXISTED!
>>"!ARTIFACT!" echo data=!VALUE_DATA!
exit /b 0

:: ============================================================================
:: Restore — copied verbatim from rollback.bat :restore_registry_value
:: ============================================================================
:restore
set "COMPONENT_ID=%~1"
set "REGISTRY_KEY=!SCRATCH_KEY!"
set "REGISTRY_VALUE=!SCRATCH_VALUE!"
set "STATE_FILE=!STATE_DIR!\!COMPONENT_ID!.state"
set "KEY_EXISTED="
set "VALUE_EXISTED="
set "VALUE_DATA="
for /f "tokens=1,2 delims==" %%A in ('findstr /r /x /c:"key_existed=[01]" "!STATE_FILE!" 2^>nul') do set "KEY_EXISTED=%%B"
for /f "tokens=1,2 delims==" %%A in ('findstr /r /x /c:"value_existed=[01]" "!STATE_FILE!" 2^>nul') do set "VALUE_EXISTED=%%B"
for /f "tokens=1,2 delims==" %%A in ('findstr /r /x /c:"data=" /c:"data=0x[0-9A-Fa-f][0-9A-Fa-f]*" "!STATE_FILE!" 2^>nul') do set "VALUE_DATA=%%B"
if "!VALUE_EXISTED!"=="1" (
    reg add "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" /t REG_DWORD /d "!VALUE_DATA!" /f >nul 2>&1
    exit /b 0
)
if "!KEY_EXISTED!"=="0" (
    reg delete "!REGISTRY_KEY!" /f >nul 2>&1
) else (
    reg delete "!REGISTRY_KEY!" /v "!REGISTRY_VALUE!" /f >nul 2>&1
)
exit /b 0

:read_current
set "CURRENT_FOUND=0"
set "CURRENT_DATA="
for /f "skip=2 tokens=1,2,*" %%A in ('reg query "!SCRATCH_KEY!" /v "!SCRATCH_VALUE!" 2^>nul') do (
    if /i "%%A"=="!SCRATCH_VALUE!" (
        set "CURRENT_FOUND=1"
        set "CURRENT_DATA=%%C"
    )
)
exit /b 0

:cleanup_scratch
reg delete "!SCRATCH_KEY!" /f >nul 2>&1
exit /b 0
