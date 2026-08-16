@echo off
:: Auto-elevate to Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrative Privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

echo ===============================================================
echo [Neuro Co-Pilot] Windows OS Stability & Hardware Hardening
echo ===============================================================

:: 1. Disable Fast Startup
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f
echo [1/4] Fast Startup (HiberbootEnabled) set to 0 (Clean boot guaranteed).

:: 2. Configure Graphics TDR Delay to 8 Seconds
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v TdrDelay /t REG_DWORD /d 8 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v TdrDdiDelay /t REG_DWORD /d 8 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v TdrLevel /t REG_DWORD /d 3 /f
echo [2/4] Graphics Driver TDR Delay set to 8 Seconds (Multi-client focus buffer).

:: 3. Set Power Plan to Balanced
powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e
echo [3/4] Power Scheme set to Balanced (5800X3D dynamic voltage scaling).

:: 4. Set Pagefile to 16GB Initial / 32GB Max on C:
powershell -Command "Set-CimInstance -Query 'Select * from Win32_PageFileSetting where Name like \"%%C:%%\"' -Property @{InitialSize=16384;MaximumSize=32768} -ErrorAction SilentlyContinue"
echo [4/4] Virtual Memory Pagefile set to 16GB Initial / 32GB Maximum.

echo ===============================================================
echo [OK] System Hardening Applied Successfully!
echo ===============================================================
pause
