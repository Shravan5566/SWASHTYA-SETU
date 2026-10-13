# Swasthya Setu Platform PowerShell Startup Script
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Starting Swasthya Setu Health Platform           " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

$pythonExe = ""
if (Test-Path ".\.venv\Scripts\python.exe") {
    $pythonExe = ".\.venv\Scripts\python.exe"
} elseif (Test-Path ".\health-01\.venv\Scripts\python.exe") {
    $pythonExe = ".\health-01\.venv\Scripts\python.exe"
} else {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
    .\.venv\Scripts\pip install -r requirements.txt
    $pythonExe = ".\.venv\Scripts\python.exe"
}

Write-Host "[*] Seeding database & verifying tables..." -ForegroundColor Green
& $pythonExe seed.py

if (-not (Test-Path "dist\index.html")) {
    Write-Host "[*] Building frontend assets..." -ForegroundColor Yellow
    npm run build
}

Write-Host "`n[*] Starting Swasthya Setu server on http://127.0.0.1:5000 ..." -ForegroundColor Cyan
Write-Host "[*] Open http://127.0.0.1:5000 in your web browser.`n" -ForegroundColor Green

& $pythonExe run.py
