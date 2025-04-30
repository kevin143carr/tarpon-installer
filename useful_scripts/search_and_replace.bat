@echo off
if "%~4"=="" (
    echo Usage: replace.bat search_word replace_word input_file output_file
    exit /b
)

setlocal enabledelayedexpansion

set "search=%~1"
set "replace=%~2"
set "input=%~3"
set "output=%~4"

if exist "%output%" del "%output%"

for /f "usebackq delims=" %%A in ("%input%") do (
    set "line=%%A"
    set "line=!line:%search%=%replace%!"
    >>"%output%" echo(!line!
)

echo Done. Output saved to "%output%"
endlocal


