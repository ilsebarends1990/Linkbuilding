@echo off
echo Starting WordPress Link Manager...
echo.

REM Start backend in new window
echo Starting FastAPI backend...
start "Backend - FastAPI" cmd /k "cd /d backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo Starting React frontend...
start "Frontend - React" cmd /k "cd /d drijfveer-dashboard && npm run dev"

echo.
echo Both services are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:5173
echo.
echo Press any key to close this window (services will keep running)
pause >nul
