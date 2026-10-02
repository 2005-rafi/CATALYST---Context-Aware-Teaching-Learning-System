@echo off
echo Building Frontend...
cd frontend
call npm run build
cd ..
echo Build complete.
pause
