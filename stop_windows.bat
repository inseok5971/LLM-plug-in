@echo off
chcp 65001 > nul
echo ==========================================================
echo  🛑 AI 플러그인 스위치보드 위젯을 종료합니다...
echo ==========================================================

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8765') do taskkill /f /pid %%a >nul 2>&1

echo ✅ 스위치보드가 안전하게 종료되었습니다.
timeout /t 2 >nul
