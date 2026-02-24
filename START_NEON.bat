@echo off
title NeonAI Controller
color 0A

echo [INFO] System Startup Initiated...

:: Check Ollama Status
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [INFO] Ollama Service: ACTIVE
) else (
    echo [WARN] Ollama Service: STOPPED. Starting now...
    start "Ollama Service" cmd /c ollama serve
    timeout /t 4 >nul
)

:: Start Server
echo [INFO] Launching Brain Engine...
start "NeonAI Server" cmd /k python server.py

:: Launch UI
echo [INFO] Opening Dashboard...
timeout /t 3 >nul
start http://localhost:5000

echo [SUCCESS] NeonAI is Live.
pause