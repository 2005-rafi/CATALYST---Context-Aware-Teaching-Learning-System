@echo off
setlocal

echo ===================================================
echo     Stopping RAG Document Intelligence Platform
echo ===================================================

:: 1. Terminate Backend on Port 8000
echo [1/4] Terminating Backend on Port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    if not "%%a"=="0" (
        echo   - Stopping Backend PID %%a
        taskkill /F /T /PID %%a >nul 2>&1
    )
)

:: 2. Terminate Frontend on Port 3000
echo [2/4] Terminating Frontend on Port 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    if not "%%a"=="0" (
        echo   - Stopping Frontend PID %%a
        taskkill /F /T /PID %%a >nul 2>&1
    )
)

:: PowerShell fallback guarantee for ports 8000 and 3000
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000,3000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1

:: 3. Close titled server terminal windows
echo [3/4] Closing server terminal windows...
taskkill /F /FI "WINDOWTITLE eq RAG_Backend_Server*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq RAG_Frontend_Server*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq RAG_Ollama_Server*" >nul 2>&1

echo [4/4] Cleanup complete.
echo ===================================================
echo   All RAG platform servers (Ports 8000, 3000) stopped!
echo ===================================================
ping 127.0.0.1 -n 3 >nul
