@echo off
echo Starting White Travels Project...
echo Checking dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Please ensure Python is installed and in your PATH.
    pause
    exit /b %errorlevel%
)
echo Dependencies confirmed.
echo Launching server...
echo.
echo Application will be available at http://127.0.0.1:5000
echo.
python server.py
pause
