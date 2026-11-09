@echo off
setlocal
cd /d "%~dp0" || exit /b 1
set "EMA_UV=uv"
if exist "%~dp0uv.exe" set "EMA_UV=%~dp0uv.exe"
"%EMA_UV%" --version >nul 2>&1
if errorlevel 1 (
    echo uv bulunamadi. GitHub Releases sayfasindan Windows paketini indir.
    if not "%~1"=="--no-browser" pause
    exit /b 1
)
"%EMA_UV%" run --locked python launch.py %*
set "EMA_EXIT=%ERRORLEVEL%"
if not "%EMA_EXIT%"=="0" if not "%~1"=="--no-browser" pause
exit /b %EMA_EXIT%
