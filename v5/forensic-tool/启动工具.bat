@echo off
REM 取证工具启动脚本 (Windows - 双击运行版本)

cd /d "%~dp0"

echo ========================================
echo   取证比赛高速查询工具
echo ========================================
echo.

REM 检查 Python 是否已安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.7 或更高版本
    echo.
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo 检查并清理旧进程...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo 正在启动 API 服务...
start /B python main.py > api.log 2>&1
timeout /t 3 /nobreak >nul

echo.
echo 正在启动 UI 界面...
python ui.py

echo.
echo UI 界面已关闭
echo 正在清理 API 服务...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo ========================================
echo   程序已完全关闭
echo ========================================
echo.
pause
