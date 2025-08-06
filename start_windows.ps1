# Persian File Copier Pro - PowerShell Setup Script
# Run this script as Administrator for best results

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Persian File Copier Pro - Windows Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists." -ForegroundColor Green
}

Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Starting Persian File Copier Pro Server..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at: http://localhost:8548" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python main.py

Read-Host "Press Enter to exit"