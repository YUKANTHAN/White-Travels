@echo off
setlocal
title White Travels - AI Concierge Launch Engine

echo.
echo  #########################################
echo  #                                       #
echo  #       WHITE TRAVELS ENGINE            #
echo  #       Autonomous AI Concierge         #
echo  #                                       #
echo  #########################################
echo.

:: Detect Python Command
echo [1/3] Detecting Python environment...
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PY=python
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set PY=py
    ) else (
        echo [CRITICAL ERROR] Python not found on this system.
        echo Please install Python and add it to your PATH.
        pause
        exit /b 1
    )
)
echo [OK] Using: %PY%

:: Install Dependencies (Silent)
echo [2/3] Verifying core modules (Flask, Duffel, DeepSeek)...
%PY% -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Dependency sync encountered issues. 
    echo Checking if server can run regardless...
) else (
    echo [OK] Dependencies confirmed.
)

:: Launch Background Watcher & Server
echo [3/3] Powering up AI Watchers and Web Shell...
echo.
echo >> APP LOGS:
echo Access URL: http://127.0.0.1:5000
echo.

:: Start the background watcher (Skill: travel-expert)
start /b "" %PY% .agent\skills\travel-expert\scripts\watcher.py > watcher.log 2>&1

:: Run main server
%PY% server.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server crashed or failed to start.
    echo Common issues: Port 5000 in use or missing environment vars.
)

pause
