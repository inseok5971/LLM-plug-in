@echo off
cd /d "%~dp0"

echo ==========================================================
echo  Starting AI Plugin Switchboard Widget...
echo ==========================================================

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765 ^| findstr LISTENING') do (
    if not "%%a"=="0" taskkill /f /pid %%a >nul 2>&1
)

python -c "exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python found. Launching widget...
    python main.py
    goto END
)

py -c "exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python found (py). Launching widget...
    py main.py
    goto END
)

python3 -c "exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python found (python3). Launching widget...
    python3 main.py
    goto END
)

echo.
echo ==========================================================
echo  [ERROR] Python is not installed on this PC!
echo ==========================================================
echo.
echo  Please install Python 3 to run this application:
echo  1. Open Microsoft Store and install "Python 3.12"
echo     or download from: https://www.python.org/downloads/
echo.
echo  2. If using python.org installer, make sure to check:
echo     [x] "Add python.exe to PATH"
echo.
echo ==========================================================
echo.
pause
exit /b 1

:END
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==========================================================
    echo  Execution finished with error code %ERRORLEVEL%
    echo ==========================================================
    echo.
    pause
)
