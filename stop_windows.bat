@echo off
cd /d "%~dp0"

echo ==========================================================
echo  Stopping AI Plugin Switchboard Widget...
echo ==========================================================

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765 ^| findstr LISTENING') do (
    if not "%%a"=="0" taskkill /f /pid %%a >nul 2>&1
)

echo [OK] Switchboard stopped safely.
timeout /t 2 >nul
