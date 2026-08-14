# ==============================================================================
# Uroboros Knowledge Engine: Automated Docker Disk & Cache Maintenance
# Zero-Dependency PowerShell Utility for BuildKit & Dangling Layer Pruning
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   UROBOROS DOCKER ENGINE: DISK & CACHE MAINTENANCE      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Inspect Initial Disk Usage
Write-Host "`n[1/4] Inspecting current Docker disk allocation..." -ForegroundColor Yellow
try {
    docker system df
} catch {
    Write-Error "Docker daemon is not reachable. Please ensure Docker Desktop is running."
    exit 1
}

# 2. Prune BuildKit Builder Cache
Write-Host "`n[2/4] Pruning BuildKit builder cache layers..." -ForegroundColor Yellow
docker builder prune -af

# 3. Prune Dangling & Unused Images
Write-Host "`n[3/4] Pruning dangling and untagged images..." -ForegroundColor Yellow
docker image prune -f

# 4. Prune Stopped Containers
Write-Host "`n[4/4] Pruning stopped ephemeral containers..." -ForegroundColor Yellow
docker container prune -f

# 5. Display Post-Cleanup Status
Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "   DOCKER DISK MAINTENANCE COMPLETE                       " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
docker system df
