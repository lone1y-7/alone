#!/bin/bash
# 取证工具启动脚本

# 获取脚本所在目录
cd "$(dirname "$0")"

# 检查并清理旧进程
echo "检查并清理旧进程..."
pkill -f "python3 main.py" 2>/dev/null
pkill -f "python3 ui.py" 2>/dev/null
sleep 1

# 启动 API 服务（后台运行）
echo "正在启动 API 服务..."
nohup python3 main.py > /tmp/api.log 2>&1 &
API_PID=$!

# 等待 API 启动
sleep 2

# 检查 API 是否启动成功
if ps -p $API_PID > /dev/null; then
    echo "✓ API 服务启动成功 (PID: $API_PID)"
    echo "  API 地址: http://localhost:8000"
    echo "  API 文档: http://localhost:8000/docs"
else
    echo "✗ API 服务启动失败"
    echo "查看日志: tail -f /tmp/api.log"
    exit 1
fi

echo

# 启动 UI 界面（前台运行）
echo "正在启动 UI 界面..."
python3 ui.py

# UI 关闭后，清理 API 进程
echo
echo "UI 界面已关闭，正在清理 API 服务..."
kill $API_PID 2>/dev/null
wait $API_PID 2>/dev/null
echo "✓ 程序已完全关闭"
