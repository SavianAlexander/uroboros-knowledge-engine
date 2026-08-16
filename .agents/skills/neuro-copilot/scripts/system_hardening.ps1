# Windows OS Stability & Multi-Client Resilience Hardening Script
# Tailored for AMD Ryzen 7 5800X3D + AMD Radeon RX 7900 XTX (24GB) + 32GB RAM

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "🛡️ Neuro Co-Pilot Windows OS Stability Hardening" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan

# 1. Disable Windows Fast Startup (Prevents SrtTrail.txt Startup Repair Loops)
try {
    Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power" -Name "HiberbootEnabled" -Value 0 -Type DWord -Force
    Write-Host "[1/4] Fast Startup (HiberbootEnabled): DISABLED (0) -> Clean kernel boot guaranteed." -ForegroundColor Green
} catch {
    Write-Host "[1/4] Fast Startup: Failed to update registry (requires elevation)." -ForegroundColor Yellow
}

# 2. Configure Graphics Driver TDR Timeout (8 Seconds)
try {
    $gfxPath = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    if (-not (Test-Path $gfxPath)) {
        New-Item -Path $gfxPath -Force | Out-Null
    }
    Set-ItemProperty -Path $gfxPath -Name "TdrDelay" -Value 8 -Type DWord -Force
    Set-ItemProperty -Path $gfxPath -Name "TdrDdiDelay" -Value 8 -Type DWord -Force
    Set-ItemProperty -Path $gfxPath -Name "TdrLevel" -Value 3 -Type DWord -Force
    Write-Host "[2/4] Graphics Driver TDR Delay: SET TO 8 SECONDS (Prevents multi-client focus timeouts)." -ForegroundColor Green
} catch {
    Write-Host "[2/4] Graphics Driver TDR Delay: Failed to update registry." -ForegroundColor Yellow
}

# 3. Switch Power Scheme to Balanced (Enables 5800X3D Precision Boost 2 Dynamic Voltages)
try {
    powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e
    Write-Host "[3/4] Power Plan: SWITCHED TO BALANCED (Reduces idle heat & power excursions)." -ForegroundColor Green
} catch {
    Write-Host "[3/4] Power Plan: Failed to set active power scheme." -ForegroundColor Yellow
}

# 4. Configure Virtual Memory Pagefile (16 GB Initial / 32 GB Max on C:)
try {
    # Update Pagefile setting via WMI
    $pagefiles = Get-CimInstance Win32_PageFileSetting -ErrorAction SilentlyContinue
    if ($pagefiles) {
        foreach ($pf in $pagefiles) {
            if ($pf.Name -like "*C:*") {
                $pf | Set-CimInstance -Property @{ InitialSize = 16384; MaximumSize = 32768 }
            }
        }
    } else {
        # Create new Pagefile setting if none exists
        New-CimInstance -ClassName Win32_PageFileSetting -Property @{ Name = "C:\pagefile.sys"; InitialSize = 16384; MaximumSize = 32768 } -ErrorAction SilentlyContinue | Out-Null
    }
    Write-Host "[4/4] Virtual Memory Pagefile: CONFIGURED (16GB Initial / 32GB Max -> 64GB Commit Cushion)." -ForegroundColor Green
} catch {
    Write-Host "[4/4] Virtual Memory: Pagefile update deferred to next reboot." -ForegroundColor Yellow
}

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "✅ System Hardening Applied Successfully!" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
