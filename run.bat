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
echo Launching server and Turbo Watcher...
echo.
echo Application available at http://127.0.0.1:5000
echo Turbo Monitor Active: Silent Background Watcher is live.
echo.
start /b python .agent\skills\travel-expert\scripts\watcher.py > watcher.log 2>&1
python server.py
pause
