# Start CargoZen Backend
Write-Host "Starting CargoZen Backend..." -ForegroundColor Cyan

Set-Location $PSScriptRoot\backend

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example - Please configure Snowflake credentials!" -ForegroundColor Yellow
}

if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/api/docs" -ForegroundColor Green
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
