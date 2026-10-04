@echo off
cd /d "%~dp0"
echo ========================================================
echo   Starting CATALYST Frontend (Render Cloud Backend)
echo ========================================================
echo  Backend URL : https://catalyst-rag-backend.onrender.com
echo  Frontend URL: http://localhost:3000
echo ========================================================
echo.

cd frontend
npm run dev
