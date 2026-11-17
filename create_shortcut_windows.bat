@echo off
cd /d "%~dp0"

echo ==========================================================
echo  Creating Desktop Shortcut for AI Plugin Switchboard...
echo ==========================================================

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\AI Plugin Switchboard.lnk'); $s.TargetPath = '%~dp0start_windows.bat'; $s.WorkingDirectory = '%~dp0'; $s.Save()"

echo.
echo [OK] Shortcut created successfully on your Desktop!
echo You can now run the Switchboard anytime from your Desktop.
echo.
pause
