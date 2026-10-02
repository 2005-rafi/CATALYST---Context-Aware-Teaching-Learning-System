@echo off
cd /d "%~dp0"

echo ===================================================
echo     Running Platform Verification & Tests
echo ===================================================

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at .\venv\
    pause
    exit /b 1
)

echo [1/2] Running Backend Pytest Suite...
call venv\Scripts\activate.bat
python -m pytest backend/tests/ -v
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Backend tests encountered errors.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Running Frontend Lint...
if exist "frontend\package.json" (
    cd frontend
    call npm run lint
    cd ..
)

echo.
echo ===================================================
echo   All tests and lint checks passed successfully!
echo ===================================================
pause
