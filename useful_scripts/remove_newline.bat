@echo off
setlocal enabledelayedexpansion

:: Check if a filename was passed as an argument
if "%~1"=="" (
    echo Usage: %~nx0 inputFile
    exit /b 1
)

:: Input file
set "inputFile=%~1"

:: Check if the input file exists
if not exist "%inputFile%" (
    echo Error: Input file "%inputFile%" does not exist.
    exit /b 1
)

:: Temporary file to store modified content
set "tempFile=%temp%\tempfile.txt"

:: Remove the temporary file if it already exists
if exist "%tempFile%" del /f /q "%tempFile%"

:: Count total lines in the file
for /f %%A in ('type "%inputFile%" ^| find /c /v ""') do set "totalLines=%%A"

:: Read the file and exclude the last newline
set "lineNumber=0"
(for /f "delims=" %%B in (%inputFile%) do (
    set /a lineNumber+=1
    if !lineNumber! lss !totalLines! (
        echo %%B
    ) else (
        <nul set /p=%%B
    )
)) > "%tempFile%"

:: Replace the original file with the modified content
move /y "%tempFile%" "%inputFile%" >nul

echo The last newline character has been removed from "%inputFile%".
exit /b 0
