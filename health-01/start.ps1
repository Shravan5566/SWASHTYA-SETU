# Swasthya Setu PowerShell Startup Script
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Starting Swasthya Setu Health Platform           " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
    .\.venv\Scripts\pip install -r requirements.txt
}

Write-Host "[*] Seeding database & verifying tables..." -ForegroundColor Green
.\.venv\Scripts\python.exe seed.py

Write-Host "`n[*] Starting Swasthya Setu server on http://127.0.0.1:5000 ..." -ForegroundColor Cyan
Write-Host "[*] Open http://127.0.0.1:5000 in your browser.`n" -ForegroundColor Green

.\.venv\Scripts\python.exe run.py
