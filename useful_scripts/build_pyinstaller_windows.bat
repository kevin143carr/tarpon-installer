@echo off
setlocal

cd /d "%~dp0.."

if exist build\windows rmdir /s /q build\windows
if exist dist\windows rmdir /s /q dist\windows

py -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --name tarpon_installer ^
  --distpath dist\windows ^
  --workpath build\windows ^
  --specpath build\windows ^
  --hidden-import PIL._tkinter_finder ^
  --add-data "assets\icons\tarpon_installer_image.png;assets/icons" ^
  --add-data "assets\icons\tarpon_installer.ico;assets/icons" ^
  --icon "assets\icons\tarpon_installer.ico" ^
  tarpon_installer.py

if errorlevel 1 exit /b %errorlevel%

echo Built dist\windows\tarpon_installer.exe
