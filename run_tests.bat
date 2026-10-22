@echo off
setlocal enabledelayedexpansion
title QPE Verification - Automated Test Suite

echo ============================================================
echo   QUANTUM PHASE ESTIMATION (QPE) - AUTOMATED TEST SUITE
echo ============================================================
echo.

set "BASE_DIR=%~dp0"
if exist "%BASE_DIR%New Folder With Items\app.py" (
    cd /d "%BASE_DIR%New Folder With Items"
) else if exist "%BASE_DIR%app.py" (
    cd /d "%BASE_DIR%"
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [*] Running PyTest test suite (14 comprehensive test cases)...
python -m pytest tests/test_qpe.py -v

echo.
pause
