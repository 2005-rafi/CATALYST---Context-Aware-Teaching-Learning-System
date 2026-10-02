@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ===================================================
echo     Starting RAG Document Intelligence Platform
echo ===================================================

:: 1. Check & Start Ollama Local LLM Server (Port 11434)
echo [1/4] Checking Ollama Local LLM Server...
set OLLAMA_RUNNING=0
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":11434" ^| findstr "LISTENING"') do (
    set OLLAMA_RUNNING=1
)

if "!OLLAMA_RUNNING!"=="1" (
    echo   - Ollama is already active on http://localhost:11434
) else (
    where ollama >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo   - Launching Ollama Local LLM Server...
        start "RAG_Ollama_Server" cmd /k "echo Starting Ollama Server... && ollama serve"
        :: Wait 2 seconds for Ollama daemon to initialize
        ping 127.0.0.1 -n 3 >nul
    ) else (
        echo   - [INFO] Ollama executable not found on PATH.
        echo     (Cloud models like Groq will be used; install Ollama for offline inference)
    )
)

:: 2. Check for Python Virtual Environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at .\venv\
    echo Please create the virtual environment first using:
    echo   python -m venv venv
    echo   .\venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

:: 3. Start Backend (FastAPI on Port 8000)
echo [2/4] Launching FastAPI Backend on http://localhost:8000...
start "RAG_Backend_Server" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: 4. Start Frontend (Next.js on Port 3000)
echo [3/4] Launching Next.js Frontend on http://localhost:3000...
if exist "frontend\package.json" (
    start "RAG_Frontend_Server" cmd /k "cd frontend && npm run dev"
) else (
    echo [WARNING] frontend\package.json not found. Skipping frontend startup.
)

:: 5. Wait for services to initialize and open browser
echo [4/4] Waiting for servers to initialize...
ping 127.0.0.1 -n 6 >nul

echo Opening browser at http://localhost:3000...
start http://localhost:3000

echo ===================================================
echo   Platform is running!
echo   - Local LLM Engine : http://localhost:11434 (Ollama)
echo   - Backend API Docs : http://localhost:8000/docs
echo   - Frontend App     : http://localhost:3000
echo   To stop all servers, run: .\stop.bat
echo ===================================================
