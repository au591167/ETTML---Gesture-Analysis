@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo  ETTML Gesture Demo - Photon 2 one-click start
echo ============================================================

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Photon2-Demo.ps1" %*
set "DEMO_EXIT=%ERRORLEVEL%"

echo.
if not "%DEMO_EXIT%"=="0" (
    echo Demo-start fejlede. Se fejlteksten ovenfor.
) else (
    echo Demo-start fuldfoert.
)
echo.
pause
exit /b %DEMO_EXIT%

