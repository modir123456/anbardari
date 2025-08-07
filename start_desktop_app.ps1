# Persian File Copier Pro - Desktop App Launcher
# Runs the application in desktop mode using browser app mode

param(
    [switch]$NoWait
)

$Host.UI.RawUI.WindowTitle = "Persian File Copier Pro - Desktop Mode"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Persian File Copier Pro - Desktop Mode" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    if (-not $NoWait) { Read-Host "Press Enter to exit" }
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
Write-Host "Starting Persian File Copier Pro in Desktop Mode..." -ForegroundColor Green
Write-Host ""

# Start server in background
$serverJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & "venv\Scripts\python.exe" main.py
}

# Wait for server to start
Start-Sleep -Seconds 3

Write-Host "Server started. Opening application..." -ForegroundColor Green

# Browser paths to check
$browsers = @(
    @{
        Name = "Google Chrome"
        Path = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        Args = "--app=http://localhost:8548 --new-window --disable-web-security --disable-features=VizDisplayCompositor --window-size=1400,900 --window-position=100,50"
    },
    @{
        Name = "Google Chrome (x86)"
        Path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        Args = "--app=http://localhost:8548 --new-window --disable-web-security --disable-features=VizDisplayCompositor --window-size=1400,900 --window-position=100,50"
    },
    @{
        Name = "Microsoft Edge"
        Path = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        Args = "--app=http://localhost:8548 --new-window --window-size=1400,900 --window-position=100,50"
    },
    @{
        Name = "Microsoft Edge (Program Files)"
        Path = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        Args = "--app=http://localhost:8548 --new-window --window-size=1400,900 --window-position=100,50"
    }
)

$launched = $false
foreach ($browser in $browsers) {
    if (Test-Path $browser.Path) {
        Write-Host "Opening with $($browser.Name)..." -ForegroundColor Green
        Start-Process -FilePath $browser.Path -ArgumentList $browser.Args -WindowStyle Normal
        $launched = $true
        break
    }
}

if (-not $launched) {
    Write-Host "Opening with default browser..." -ForegroundColor Yellow
    Start-Process "http://localhost:8548"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Persian File Copier Pro is now running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application is running in desktop mode" -ForegroundColor Green
Write-Host "Application URL: http://localhost:8548" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop the application:" -ForegroundColor Yellow
Write-Host "1. Close the application window" -ForegroundColor White
Write-Host "2. Press Ctrl+C in this console" -ForegroundColor White
Write-Host ""

# Monitor server job and keep console open
try {
    while ($serverJob.State -eq "Running") {
        Start-Sleep -Seconds 1
        if ([Console]::KeyAvailable) {
            $key = [Console]::ReadKey($true)
            if ($key.Key -eq "Escape" -or ($key.Modifiers -eq "Control" -and $key.Key -eq "C")) {
                break
            }
        }
    }
} finally {
    Write-Host ""
    Write-Host "Stopping server..." -ForegroundColor Yellow
    Stop-Job -Job $serverJob -Force
    Remove-Job -Job $serverJob -Force
    Write-Host "Server stopped." -ForegroundColor Green
}

if (-not $NoWait) {
    Read-Host "Press Enter to exit"
}