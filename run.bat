@echo off
title Uroboros Knowledge Engine
echo ===================================================
echo   Starting Uroboros Knowledge Engine...
echo ===================================================

:: System & Hardware Performance Environment Flags
set PYTHONOPTIMIZE=1
set PYTHONPYCACHEPREFIX=%LOCALAPPDATA%\pycache
set FORCE_CMAKE=1
set CMAKE_ARGS=-DGGML_VULKAN=on
if "%PORT%"=="" set PORT=8085

set "PY_CMD="
if exist ".venv\Scripts\python.exe" set "PY_CMD=.venv\Scripts\python.exe"
if "%PY_CMD%"=="" set "PY_CMD=python"

:: Verify dependencies
"%PY_CMD%" -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Missing dependencies detected. Installing requirements...
    "%PY_CMD%" -m pip install -r requirements.txt
)

:: Start engine and open browser
echo Launching backend at http://127.0.0.1:%PORT%...
start http://127.0.0.1:%PORT%
"%PY_CMD%" main.py
if errorlevel 1 (
    echo.
    echo Engine stopped unexpectedly with error code %errorlevel%.
    pause
    exit /b %errorlevel%
)
