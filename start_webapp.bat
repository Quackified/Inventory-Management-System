@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_webapp.ps1"

if %ERRORLEVEL% neq 0 (
	echo.
	echo Launch failed.
	exit /b %ERRORLEVEL%
)

echo.
echo Launch finished.