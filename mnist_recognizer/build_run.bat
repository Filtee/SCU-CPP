@echo off
setlocal

REM 设置编译器路径
set VS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64
set INCLUDE=C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\um;C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\shared
set LIB=C:\Program Files (x86)\Windows Kits\10\Lib\10.0.19041.0\um\x64

REM 检查编译器是否存在
if not exist "%VS_PATH%\cl.exe" (
    echo 无法找到Visual Studio编译器。请安装Visual Studio 2019或更新版本。
    echo 或者手动修改此批处理文件中的VS_PATH路径。
    pause
    exit /b 1
)

REM 切换到项目目录
cd /d %~dp0

REM 编译程序
echo 正在编译程序...
"%VS_PATH%\cl.exe" windows_recognizer.cpp /EHsc /DUNICODE /D_UNICODE /link gdiplus.lib

REM 检查编译是否成功
if %errorlevel% neq 0 (
    echo 编译失败！
    pause
    exit /b 1
)

echo 编译成功！

REM 运行程序
echo 正在运行程序...
echo.
windows_recognizer.exe

REM 清理临时文件
echo.
echo 清理临时文件...
del /f /q windows_recognizer.obj windows_recognizer.exe

echo 完成！
pause
