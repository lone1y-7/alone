@echo off
echo ====================================
echo   SQLite 数据库 AI 分析工具
echo ====================================
echo.

python sqlite_analyzer.py --provider doubao --config config.ini.example

echo.
echo 程序已退出，按任意键关闭...
pause >nul
