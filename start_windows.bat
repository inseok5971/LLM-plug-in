@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
cd /d "%~dp0"

echo ==========================================================
echo  ⚡ AI 플러그인 스위치보드 미니 위젯을 실행합니다...
echo ==========================================================

REM 1. 이전 프로세스가 남아있다면 포트 8765 정리
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765 ^| findstr LISTENING') do (
    if not "%%a"=="0" taskkill /f /pid %%a >nul 2>&1
)

REM 2. 실제로 실행 가능한 Python인지 테스트
set PY_CMD=

python -c "exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=python
    goto RUN
)

py -c "exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=py
    goto RUN
)

python3 -c "exit(0)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=python3
    goto RUN
)

:NO_PYTHON
echo.
echo ==========================================================
echo  [안내] 컴퓨터에 Python(파이썬)이 설치되어 있지 않습니다!
echo ==========================================================
echo.
echo  이 위젯 프로그램을 구동하려면 Python 3가 필요합니다.
echo.
echo  1. 마이크로소프트 스토어(Microsoft Store)에서 "Python 3.12" 검색 후 설치
echo     또는 공식 사이트: https://www.python.org/downloads/
echo.
echo  2. 공식 사이트 설치 시 꼭 [Add python.exe to PATH] 체크박스를 켜주세요!
echo.
echo ==========================================================
echo.
pause
exit /b 1

:RUN
echo Python 실행기 감지 완료 (%PY_CMD%)
echo 스위치보드 위젯 서버를 시작합니다...
%PY_CMD% main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==========================================================
    echo  [안내] 프로그램 실행이 중단되었습니다. (오류 코드: %ERRORLEVEL%)
    echo ==========================================================
    echo.
    pause
)
