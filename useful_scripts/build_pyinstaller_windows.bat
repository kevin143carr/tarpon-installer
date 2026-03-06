@echo off
setlocal

cd /d "%~dp0.."
set "PYTHON_CMD=python"

%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 set "PYTHON_CMD=python3"

%PYTHON_CMD% useful_scripts\build_pyinstaller_release.py --platform-id windows-x86_64 --build-mode onefile

if errorlevel 1 exit /b %errorlevel%

echo Built PyInstaller release package under dist\nuitka\
