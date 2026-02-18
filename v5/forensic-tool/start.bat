@echo off
REM 取证工具启动脚本 (Windows)

cd /d "%~dp0"

echo 检查并清理旧进程...
taskkill /F /IM python.exe 2>nul
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
taskkill /F /IM python.exe 2>nul
echo 程序已完全关闭
pause
