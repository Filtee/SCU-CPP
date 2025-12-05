@echo off
REM C++ 手写数字识别程序编译脚本

REM 设置 Visual Studio 编译器路径 (根据实际情况调整)
set VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build

REM 初始化 Visual Studio 环境
call "%VS_PATH%\vcvars32.bat" > nul

REM 检查编译器是否可用
where cl > nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 Visual C++ 编译器
    echo 请确保已安装 Visual Studio Build Tools 或 Visual Studio
    pause
    exit /b 1
)

echo 正在编译 console_recognizer.cpp...
cl console_recognizer.cpp /EHsc /link gdiplus.lib

if %errorlevel% neq 0 (
    echo 编译失败！
    pause
    exit /b 1
)

echo 编译成功！

REM 检查是否有 drawn_digit.png 文件
if exist "..\drawn_digit.png" (
    echo 找到 drawn_digit.png 文件
    echo 正在运行识别程序...
    console_recognizer.exe "..\drawn_digit.png"
) else (
    echo 未找到 drawn_digit.png 文件
    echo 请先使用 Python 程序绘制并保存数字
)

pause