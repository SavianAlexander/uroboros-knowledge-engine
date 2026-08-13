# PowerShell Unified Production Deployment Script for Uroboros Knowledge Engine
# Builds Docker containers, enables AMD GPU acceleration passthrough, pre-fetches Ollama models, and runs E2E verification.

Param(
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " 🚀 Uroboros Knowledge Engine — Production Deployment Lifecycle" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Check Docker Availability
Write-Host "`n[1/4] Checking Docker and Docker Compose environment..." -ForegroundColor Yellow
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker executable was not found on PATH. Please install Docker Desktop for Windows."
    exit 1
}

# 2. Build and Launch Containers
Write-Host "`n[2/4] Building and launching containers (FastAPI, Nginx, Ollama AMD GPU)..." -ForegroundColor Yellow
docker compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker compose deployment failed with exit code $LASTEXITCODE."
    exit $LASTEXITCODE
}

# 3. Pre-fetch LLM & Vector Embedding Models into Ollama
Write-Host "`n[3/4] Pre-fetching qwen2.5:7b model into Ollama container..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

docker exec uroboros_ollama ollama pull qwen2.5:7b
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Failed to pre-fetch qwen2.5:7b automatically into Ollama container. Backend will fallback gracefully."
} else {
    Write-Host "  ✅ qwen2.5:7b model pre-fetched successfully." -ForegroundColor Green
}

# 4. Automated E2E Test Suite Verification
if (-not $SkipTests) {
    Write-Host "`n[4/4] Running automated backend test suite verification..." -ForegroundColor Yellow
    python -m pytest tests/test_system_maintenance.py tests/test_graph_export.py tests/test_search_benchmark.py tests/test_search_bookmarks.py tests/test_backup_scheduler.py -v
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 DEPLOYMENT VERIFIED SUCCESSFULLY! Engine running at http://localhost:8000 and UI at http://localhost" -ForegroundColor Green
    } else {
        Write-Error "E2E verification tests failed with exit code $LASTEXITCODE."
        exit $LASTEXITCODE
    }
} else {
    Write-Host "`n🎉 DEPLOYMENT COMPLETED! (Tests skipped)" -ForegroundColor Green
}
