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

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

:: Start the engine & auto-open web UI in default browser
echo Launching backend at http://127.0.0.1:8000...
start http://127.0.0.1:8000
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Engine stopped unexpectedly with error code %errorlevel%.
    pause
)
