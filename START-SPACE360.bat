@echo off
echo ================================
echo    Space360 by SGB Dev Apps
echo ================================
echo.
echo --- Automatic Environment Checks ---
echo.

cd F:\Space360

:: 1. Check and create Backend Virtual Environment
if not exist backend\venv (
    echo [1/4] Creating virtual environment for Backend...
    cd backend
    python -m venv venv
    echo Installing backend requirements...
    call venv\Scripts\activate
    pip install -r requirements.txt
    cd ..
) else (
    echo [1/4] Backend virtual environment found.
)

:: 2. Fix Backend GCP Credentials pointer
echo [2/4] Syncing Backend Firebase Credentials...
powershell -Command "(Get-Content backend\.env) -replace 'gcp-credentials\.json', 'firebase-service-account.json' | Set-Content backend\.env"

:: 3. Sync Dashboard to space360-production
echo [3/4] Syncing Dashboard Firebase Project to space360-production...
powershell -Command "(Get-Content dashboard\.env) -replace 'REACT_APP_FIREBASE_API_KEY=.*', 'REACT_APP_FIREBASE_API_KEY=AIzaSyBbiel5T3pFgiMFvdVweWC0RsJa5juVhZA' -replace 'REACT_APP_FIREBASE_AUTH_DOMAIN=.*', 'REACT_APP_FIREBASE_AUTH_DOMAIN=space360-production.firebaseapp.com' -replace 'REACT_APP_FIREBASE_PROJECT_ID=.*', 'REACT_APP_FIREBASE_PROJECT_ID=space360-production' -replace 'REACT_APP_FIREBASE_STORAGE_BUCKET=.*', 'REACT_APP_FIREBASE_STORAGE_BUCKET=space360-production.firebasestorage.app' -replace 'REACT_APP_FIREBASE_MESSAGING_ID=.*', 'REACT_APP_FIREBASE_MESSAGING_ID=356278681043' | Set-Content dashboard\.env"

:: 4. Auto-update Android BASE_URL to current local IP
echo [4/4] Updating Android App BASE_URL for physical device testing...
powershell -Command "$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like '192.168.*' -or $_.IPAddress -like '10.*' } | Select-Object -First 1 -ExpandProperty IPAddress); if ($ip) { (Get-Content app\src\main\java\com\sgbdevapps\space360\di\NetworkModule.kt) -replace 'private const val BASE_URL = .*', \"private const val BASE_URL = `\"http://$($ip):8000/`\" // Auto-updated by START-SPACE360.bat\" | Set-Content app\src\main\java\com\sgbdevapps\space360\di\NetworkModule.kt; echo \"      -^> Set to http://$($ip):8000/\" } else { echo \"      -^> Could not find local Wi-Fi IP.\" }"

echo.
echo --- Starting Space360 ---
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
