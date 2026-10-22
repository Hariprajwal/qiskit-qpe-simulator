@echo off
setlocal
title Quantum Phase Estimation - Launcher

echo ============================================================
echo   QUANTUM PHASE ESTIMATION (QPE) - STREAMLIT DASHBOARD
echo ============================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if errorlevel 1 goto NO_PYTHON

:: 2. Resolve directory
set "BASE_DIR=%~dp0"
if exist "%BASE_DIR%New Folder With Items\app.py" (
    cd /d "%BASE_DIR%New Folder With Items"
) else if exist "%BASE_DIR%app.py" (
    cd /d "%BASE_DIR%"
) else (
    goto NO_APP
)

echo [*] Project directory: %CD%
echo.

:: 3. Check / create Windows virtual environment
if not exist "venv\Scripts\activate.bat" goto CREATE_VENV
goto ACTIVATE_VENV

:CREATE_VENV
echo [*] Creating fresh Windows Python virtual environment (venv)...
python -m venv venv
if errorlevel 1 goto VENV_FAIL
echo [*] Virtual environment created successfully.
echo.

:ACTIVATE_VENV
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: 4. Check dependencies
python -c "import streamlit, qiskit, qiskit_aer, plotly, pyarrow" >nul 2>nul
if errorlevel 1 goto INSTALL_DEPS
goto RUN_APP

:INSTALL_DEPS
echo [*] Installing required packages from requirements.txt...
echo [*] This only happens once on first setup. Please wait...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto DEPS_FAIL
echo [*] Dependencies installed successfully!
echo.

:RUN_APP
echo ============================================================
echo [*] Launching Quantum Phase Estimation Dashboard...
echo [*] Starting local server at: http://localhost:8501
echo [*] Press Ctrl+C in this window anytime to stop the server.
echo ============================================================
echo.
python -m streamlit run app.py
goto END

:NO_PYTHON
echo [ERROR] Python is not found in your system PATH!
echo Please install Python 3.10 or 3.11 from python.org and check "Add Python to PATH".
goto PAUSE_EXIT

:NO_APP
echo [ERROR] Could not locate app.py!
goto PAUSE_EXIT

:VENV_FAIL
echo [ERROR] Failed to create virtual environment.
goto PAUSE_EXIT

:DEPS_FAIL
echo [ERROR] Failed to install dependencies.
goto PAUSE_EXIT

:PAUSE_EXIT
echo.
pause
exit /b 1

:END
