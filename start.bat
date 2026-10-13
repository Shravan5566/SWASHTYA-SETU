@echo off
setlocal enabledelayedexpansion
title Swasthya Setu Platform
echo ========================================================
echo        Starting Swasthya Setu Health Platform
echo ========================================================

cd /d "%~dp0"

:: Auto-detect project folder whether launched from Desktop, SS pccoe, or health-01
if exist "health-01\run.py" (
    cd "health-01"
    goto :FOUND
)
if exist "SS pccoe\health-01\run.py" (
    cd "SS pccoe\health-01"
    goto :FOUND
)
if exist "run.py" (
    goto :FOUND
)

:FOUND
echo [*] Project directory detected: %CD%

if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not found in %CD%. Creating .venv...
    python -m venv .venv
    echo [*] Installing dependencies...
    .\.venv\Scripts\pip install -r requirements.txt
)

echo [*] Seeding / checking database tables...
.\.venv\Scripts\python.exe seed.py

:: Check and build modern frontend if dist is missing
if not exist "..\dist\index.html" (
    if not exist "dist\index.html" (
        if not exist "app\dist\index.html" (
            echo [*] Building modern digital health frontend...
            pushd "%~dp0"
            call npm run build
            popd
        )
    )
)

echo [*] Launching unified application server on http://127.0.0.1:5000 ...
echo [*] Unified platform running! Open http://127.0.0.1:5000 in your browser.
.\.venv\Scripts\python.exe run.py
pause
