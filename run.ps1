# Uroboros Knowledge Engine - High-Performance PowerShell Launcher
$ErrorActionPreference = 'Stop'
$Host.UI.RawUI.WindowTitle = "Uroboros Knowledge Engine"
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting Uroboros Knowledge Engine (Vulkan AMD GPU)..." -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan

$env:PYTHONOPTIMIZE = "1"
$env:PYTHONPYCACHEPREFIX = "$env:LOCALAPPDATA\pycache"
$env:FORCE_CMAKE = "1"
$env:CMAKE_ARGS = "-DGGML_VULKAN=on"

python main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nEngine stopped unexpectedly with error code $LASTEXITCODE." -ForegroundColor Red
    Read-Host 'Press Enter to exit'
}
