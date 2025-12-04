@echo off

REM 设置Visual Studio环境变量
set VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build
if not exist "%VS_PATH%\vcvars32.bat" (
    echo 找不到Visual Studio 2019环境
    echo 请修改VS_PATH变量指向正确的Visual Studio安装路径
    pause
    exit /b 1
)

call "%VS_PATH%\vcvars32.bat"

REM 编译控制台识别程序
echo 正在编译控制台识别程序...
cl console_recognizer.cpp /EHsc /DUNICODE /D_UNICODE /link gdiplus.lib

if %errorlevel% neq 0 (
    echo 编译失败
    pause
    exit /b 1
)

echo 编译成功

REM 运行程序
echo 正在运行识别程序...
echo.console_recognizer.exe

pause
