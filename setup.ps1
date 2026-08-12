# setup.ps1 - Uroboros Knowledge Engine Pure Docker Deployment Lifecycle Script

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " Uroboros Knowledge Engine - Deployment & Setup Lifecycle" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. Pre-flight Check: Verify docker and docker-compose CLI and daemon accessibility
Write-Host "`n[Pre-flight Check] Verifying Docker CLI and daemon availability..." -ForegroundColor Yellow

$dockerCli = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCli) {
    Write-Host "[ERROR] Docker CLI ('docker') is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker daemon is not running or not accessible." -ForegroundColor Red
    exit 1
}
Write-Host "  + Docker CLI and daemon are accessible." -ForegroundColor Green

$composeCmd = "docker-compose"
$composeCli = Get-Command docker-compose -ErrorAction SilentlyContinue
if (-not $composeCli) {
    docker compose version > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        $composeCmd = "docker compose"
        Write-Host "  + Using 'docker compose' plugin." -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Neither 'docker-compose' nor 'docker compose' is available." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  + Using 'docker-compose' CLI." -ForegroundColor Green
}

# 2. Container Orchestration: Execute docker-compose up -d --build
Write-Host "`n[Container Orchestration] Executing $composeCmd up -d --build..." -ForegroundColor Yellow
if ($composeCmd -eq "docker-compose") {
    docker-compose up -d --build --remove-orphans
} else {
    docker compose up -d --build --remove-orphans
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Container orchestration failed with exit code $LASTEXITCODE." -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "  + Containers successfully built and started." -ForegroundColor Green

# 3. Health Polling: Wait for native GPU Ollama readiness at http://localhost:11434/api/version
Write-Host "`n[Health Polling] Verifying native AMD GPU Ollama readiness at http://localhost:11434/api/version..." -ForegroundColor Yellow
$ollamaUrl = "http://localhost:11434/api/version"
$maxAttempts = 15
$intervalSeconds = 2
$isHealthy = $false

for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    try {
        $request = [System.Net.WebRequest]::Create($ollamaUrl)
        $request.Timeout = 3000
        $response = $request.GetResponse()
        if ($response.StatusCode -eq [System.Net.HttpStatusCode]::OK) {
            $response.Close()
            $isHealthy = $true
            Write-Host "  + Native AMD GPU Ollama service is healthy and responding! (Attempt $attempt/$maxAttempts)" -ForegroundColor Green
            break
        }
        $response.Close()
    } catch {
        # Try to launch native Ollama app if not running
        Write-Host "  - Attempting to launch native Ollama app..." -ForegroundColor Gray
        Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" -ArgumentList "app" -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds $intervalSeconds
}

if (-not $isHealthy) {
    Write-Host "[ERROR] Native GPU Ollama failed to become ready at http://localhost:11434." -ForegroundColor Red
    exit 1
}

# 4. Pre-fetch Models: Execute native ollama pull for LLM and Embedding models
Write-Host "`n[Model Pre-fetch] Ensuring models qwen2.5:7b and nomic-embed-text are ready in native GPU Ollama..." -ForegroundColor Yellow
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Model pre-fetch (qwen2.5:7b) failed with exit code $LASTEXITCODE." -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "  + Model qwen2.5:7b successfully ready on AMD GPU." -ForegroundColor Green

# 5. E2E Verification: Execute test runner container (docker-compose -f docker-compose.test.yml up --abort-on-container-exit --build)
Write-Host "`n[E2E Verification] Executing E2E test runner via docker-compose.test.yml..." -ForegroundColor Yellow
if ($composeCmd -eq "docker-compose") {
    docker-compose -f docker-compose.test.yml up --abort-on-container-exit --build
} else {
    docker compose -f docker-compose.test.yml up --abort-on-container-exit --build
}

$testExitCode = $LASTEXITCODE

# 6. Exit Code Propagation
if ($testExitCode -eq 0) {
    Write-Host "`n=========================================================" -ForegroundColor Green
    Write-Host " SUCCESS: Setup and E2E Verification Completed Successfully!" -ForegroundColor Green
    Write-Host "=========================================================" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n=========================================================" -ForegroundColor Red
    Write-Host " FAILURE: E2E Verification Failed with exit code $testExitCode." -ForegroundColor Red
    Write-Host "=========================================================" -ForegroundColor Red
    exit $testExitCode
}
