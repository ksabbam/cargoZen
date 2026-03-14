@echo off
title CargoZen
color 0B
cls

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║       CargoZen - Starting...             ║
echo  ╚══════════════════════════════════════════╝
echo.

:: ── Kill any previous instances ───────────────────────────
taskkill /FI "WINDOWTITLE eq CargoZen API*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq CargoZen UI*" /F >nul 2>&1

:: ── Start Backend ─────────────────────────────────────────
echo  [1/2] Starting API server...
cd /d "%~dp0backend"
start "CargoZen API" /min cmd /k "title CargoZen API && cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn app.main:app --host 127.0.0.1 --port 8000"

:: ── Start Frontend ────────────────────────────────────────
echo  [2/2] Starting UI server...
cd /d "%~dp0frontend"
start "CargoZen UI" /min cmd /k "title CargoZen UI && cd /d %~dp0frontend && node node_modules\vite\bin\vite.js --host"

:: ── Wait and open browser ─────────────────────────────────
echo.
echo  Waiting for servers to start...
timeout /t 4 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║      CargoZen is RUNNING!                ║
echo  ╠══════════════════════════════════════════╣
echo  ║                                          ║
echo  ║  UI    :  http://localhost:5173          ║
echo  ║  API   :  http://localhost:8000          ║
echo  ║  Docs  :  http://localhost:8000/api/docs ║
echo  ║                                          ║
echo  ║  Login :  admin / Admin@123              ║
echo  ║                                          ║
echo  ║  Close terminal windows to stop.         ║
echo  ╚══════════════════════════════════════════╝
echo.
pause