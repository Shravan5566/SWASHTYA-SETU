#!/usr/bin/env bash
# Swasthya Setu Platform Startup Script (Bash / Git Bash / Linux / macOS)
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================================"
echo "       Starting Swasthya Setu Health Platform"
echo "========================================================"

# Auto-detect Python binary
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[!] Python is not found in PATH. Please install Python 3.10+."
    exit 1
fi

# Detect or create virtual environment
if [ -f ".venv/bin/python" ]; then
    VENV_PY=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    VENV_PY=".venv/Scripts/python.exe"
elif [ -f "health-01/.venv/bin/python" ]; then
    VENV_PY="health-01/.venv/bin/python"
elif [ -f "health-01/.venv/Scripts/python.exe" ]; then
    VENV_PY="health-01/.venv/Scripts/python.exe"
else
    echo "[*] Creating virtual environment (.venv)..."
    $PY_CMD -m venv .venv
    if [ -f ".venv/bin/pip" ]; then
        .venv/bin/pip install -r requirements.txt
        VENV_PY=".venv/bin/python"
    else
        .venv/Scripts/pip install -r requirements.txt
        VENV_PY=".venv/Scripts/python.exe"
    fi
fi

echo "[*] Seeding & verifying database tables..."
"$VENV_PY" seed.py

# Build frontend if dist/index.html is missing
if [ ! -f "dist/index.html" ]; then
    echo "[*] Building frontend asset bundle..."
    npm run build
fi

echo ""
echo "[*] Launching Swasthya Setu Platform server on http://127.0.0.1:5000 ..."
echo "[*] Open http://127.0.0.1:5000 in your web browser."
echo ""
"$VENV_PY" run.py
