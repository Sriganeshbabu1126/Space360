@echo off
echo ================================
echo    Space360 by SGB Dev Apps
echo ================================
echo.
echo Starting Backend API...
start cmd /k "cd F:\Space360\backend && call venv\Scripts\activate && uvicorn main:app --reload --port 8000"
echo.
echo Starting Dashboard...
start cmd /k "cd F:\Space360\dashboard && npm start"
echo.
echo ================================
echo Space360 is starting up...
echo.
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo Dashboard: http://localhost:3000
echo ================================
pause
