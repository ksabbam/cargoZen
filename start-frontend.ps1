# Start CargoZen Frontend
Write-Host "Starting CargoZen Frontend..." -ForegroundColor Cyan

Set-Location $PSScriptRoot\frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install
}

Write-Host "Starting Vite dev server on http://localhost:5173" -ForegroundColor Green
npm run dev
