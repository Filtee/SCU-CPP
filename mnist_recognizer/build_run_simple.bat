@echo off
REM Simple build and run script for handwritten digit recognizer

REM Check if Visual Studio compiler is available
cl > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Visual C++ compiler not found
    echo Please install Visual Studio Build Tools
    pause
    exit /b 1
)

REM Compile the program
echo Compiling console_recognizer.cpp...
cl console_recognizer.cpp /EHsc /link gdiplus.lib

if %errorlevel% neq 0 (
    echo Compilation failed!
    pause
    exit /b 1
)

echo Compilation successful!

REM Run the program with the drawn_digit.png file
echo Running recognizer...
console_recognizer.exe "..\drawn_digit.png"

pause