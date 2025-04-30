@echo off
setlocal enabledelayedexpansion

:: Check if a filename is provided
if "%~1"=="" (
    echo Usage: %~nx0 inputfile.txt
    exit /b 1
)

:: Get the input filename from the first parameter
set "inputFile=%~1"

:: Check if the input file exists
if not exist "%inputFile%" (
    echo Error: File "%inputFile%" not found!
    exit /b 1
)

:: Read the first line from the file
set "line="
for /f "delims=" %%A in (%inputFile%) do set "line=%%A"

:: Remove the trailing comma (if it exists)
if "!line:~-1!"=="," set "line=!line:~0,-1!"

:: Write the cleaned string to the file (overwrite the original file)
> "%inputFile%" < nul set /p=!line!

echo Process completed. The file "%inputFile%" has been updated.

