#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=========================================================="
echo "🎯 ResumeIQ: ATS Resume Analyzer Web Application"
echo "=========================================================="

MODE="${1:-prod}"

if [ "$MODE" = "dev" ]; then
    echo "Starting in DEVELOPMENT mode..."
    echo "1. Starting FastAPI backend on http://127.0.0.1:8000..."
    PYTHONPATH=backend .venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload &
    BACKEND_PID=$!

    echo "2. Starting Vite frontend on http://localhost:5173..."
    cd frontend && npm run dev &
    FRONTEND_PID=$!

    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true" EXIT
    wait
else
    echo "Starting in UNIFIED SINGLE-SERVICE mode (Recommended)..."
    echo "Checking if frontend is built..."
    if [ ! -f "frontend/dist/index.html" ]; then
        echo "Building frontend static assets..."
        (cd frontend && npm run build)
    fi

    echo "Starting FastAPI on http://127.0.0.1:8000..."
    echo "Opening your browser to http://127.0.0.1:8000..."
    PYTHONPATH=backend .venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
fi
