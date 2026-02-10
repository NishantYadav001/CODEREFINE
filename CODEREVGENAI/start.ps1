# Quick Start Script for Code Refine (PowerShell)

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Code Refine - Quick Start" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\backend"

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
$venvPath = Join-Path (Get-Location) "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
}

# Install/upgrade dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt -q

# Show server info
Write-Host ""
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "Starting Server..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "URL: http://127.0.0.1:8000/login" -ForegroundColor Cyan
Write-Host ""
Write-Host "Demo Credentials:" -ForegroundColor White
Write-Host "  Username: admin" -ForegroundColor Green
Write-Host "  Password: password" -ForegroundColor Green
Write-Host ""
Write-Host "Or try: student1 / teacher with same password" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host ""

# Run the server
python main.py
