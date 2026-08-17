# ==============================================================================
# Uroboros Knowledge Engine: WSL 2 & Docker VM Hardware Optimizer
# Zero-Dependency PowerShell Utility to Tune Docker Desktop CPU & Memory
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   WSL 2 & DOCKER DESKTOP HARDWARE OPTIMIZER             " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$wslConfigPath = Join-Path $env:USERPROFILE ".wslconfig"
Write-Host "`nTarget configuration: $wslConfigPath" -ForegroundColor Yellow

$recommendedConfig = @"
# ==============================================================================
# WSL 2 Hardware Profile Optimized for Uroboros & EVE Multi-Client Zero-Stutter
# ==============================================================================
[wsl2]
memory=4GB
processors=4
swap=1GB
pageReporting=true
autoProxy=true
"@

if (Test-Path $wslConfigPath) {
    $existing = Get-Content $wslConfigPath -Raw
    Write-Host "`nExisting .wslconfig detected:" -ForegroundColor Gray
    Write-Host $existing -ForegroundColor DarkGray
    
    $backupPath = "$wslConfigPath.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $wslConfigPath $backupPath
    Write-Host "Backup created at: $backupPath" -ForegroundColor Green
}

Set-Content -Path $wslConfigPath -Value $recommendedConfig -Encoding utf8
Write-Host "`n[OK] .wslconfig successfully updated with 4GB RAM and 4 Cores for EVE Zero-Stutter Gaming!" -ForegroundColor Green

Write-Host "`n----------------------------------------------------------" -ForegroundColor Cyan
Write-Host "NOTE: To apply these hardware limits to Docker Desktop:" -ForegroundColor Yellow
Write-Host "1. Open a terminal and run: wsl --shutdown" -ForegroundColor White
Write-Host "2. Restart Docker Desktop from your start menu or tray." -ForegroundColor White
Write-Host "----------------------------------------------------------" -ForegroundColor Cyan
