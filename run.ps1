$Error.Clear()
# Uroboros Knowledge Engine - High-Performance PowerShell Launcher
$Host.UI.RawUI.WindowTitle = "Uroboros Knowledge Engine"
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting Uroboros Knowledge Engine (Vulkan AMD GPU)..." -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan

$env:PYTHONOPTIMIZE = "1"
$env:PYTHONPYCACHEPREFIX = "$env:LOCALAPPDATA\pycache"
$env:FORCE_CMAKE = "1"
$env:CMAKE_ARGS = "-DGGML_VULKAN=on"
if (-not $env:PORT) { $env:PORT = "8085" }

$pyCmd = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }

Write-Host "Launching backend at http://127.0.0.1:$($env:PORT)..." -ForegroundColor Yellow

try {
    & $pyCmd main.py
} catch {
    Write-Host "`nFailed to launch Python engine: $_" -ForegroundColor Red
    $global:LASTEXITCODE = 1
}
$exitCode = if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) { $LASTEXITCODE } else { if ($Error.Count -gt 0) { 1 } else { 0 } }
if ($exitCode -ne 0) {
    Write-Host "`nEngine stopped with exit code $exitCode." -ForegroundColor Red
}
Read-Host 'Press Enter to exit'
exit $exitCode
