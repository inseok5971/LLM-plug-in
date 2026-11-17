@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ==========================================================
echo  ⚡ 바탕화면에 'AI 플러그인 스위치보드' 바로가기를 생성합니다...
echo ==========================================================

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\AI 플러그인 스위치보드.lnk'); $s.TargetPath = '%~dp0start_windows.bat'; $s.WorkingDirectory = '%~dp0'; $s.IconLocation = 'shell32.dll,13'; $s.Save()"

echo.
echo ✅ 윈도우 바탕화면에 바로가기 생성이 완료되었습니다!
echo 앞으로는 바탕화면의 [AI 플러그인 스위치보드] 아이콘만 더블 클릭하시면 됩니다.
echo.
pause
