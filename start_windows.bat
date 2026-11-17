@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ==========================================================
echo  ⚡ AI 플러그인 스위치보드 미니 위젯을 실행합니다...
echo ==========================================================

REM 이전 프로세스가 남아있다면 포트 8765 깔끔하게 정리
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765') do taskkill /f /pid %%a >nul 2>&1

REM 파이썬 실행기 자동 탐색 (python, py, python3 순서로 확인)
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python main.py
    goto end
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py main.py
    goto end
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python3 main.py
    goto end
)

echo.
echo [안내] Python이 컴퓨터에 설치되어 있지 않습니다.
echo https://www.python.org 또는 Microsoft Store에서 Python을 설치해 주세요.
echo.
pause

:end
