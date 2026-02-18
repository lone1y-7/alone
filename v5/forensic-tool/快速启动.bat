@echo off
REM 取证工具启动脚本 (Windows - 快速版本)

cd /d "%~dp0"

taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

start /B python main.py > api.log 2>&1
timeout /t 3 /nobreak >nul

python ui.py

taskkill /F /IM python.exe >nul 2>&1
