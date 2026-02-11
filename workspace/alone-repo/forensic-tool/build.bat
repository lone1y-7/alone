@echo off
chcp 65001 >nul
echo 编译 C 语言核心模块...

:: 确保目录存在
if not exist build mkdir build
if not exist src mkdir src

:: 检查是否为 VS x64 工具环境
if not defined VSCMD_VER (
    echo 错误：请在 "x64 Native Tools Command Prompt for VS" 中运行此脚本！
    pause
    exit /b 1
)

:: MSVC 编译目标文件（x64，导出函数）
echo 检测到 VS x64 环境，编译 DLL...
cl.exe /c /D BUILD_DLL /Fo:src\file_scanner.obj src\file_scanner.c /W3 /nologo
if errorlevel 1 (
    echo 编译目标文件失败！请检查 C 代码语法/依赖
    pause
    exit /b 1
)

:: 链接为 64 位 DLL（依赖 Windows 系统库）
link.exe /DLL /OUT:build\scanner.dll src\file_scanner.obj user32.lib kernel32.lib advapi32.lib /MACHINE:x64 /nologo
if errorlevel 1 (
    echo 链接 DLL 失败！
    pause
    exit /b 1
)

:: 检查输出文件
if exist build\scanner.dll (
    echo 编译成功！
    echo 动态链接库已生成：build\scanner.dll
) else (
    echo 编译失败：未生成 DLL 文件！
    pause
    exit /b 1
)

pause
exit /b 0