#!/bin/bash

echo "启动 Ollama 服务..."
nohup ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
echo "Ollama 服务已启动 (PID: $OLLAMA_PID)"

sleep 3

echo "检查 llama2 模型..."
if ! ollama list | grep -q "llama2"; then
    echo "下载 llama2 模型..."
    ollama pull llama2
else
    echo "llama2 模型已存在"
fi

echo ""
echo "服务状态:"
echo "Ollama: 运行中 (PID: $OLLAMA_PID)"
echo "模型: llama2"
echo ""
echo "测试 Ollama..."
curl -s http://localhost:11434/api/generate -d '{"model":"llama2","prompt":"测试","stream":false}' | head -c 100

echo ""
echo ""
echo "现在可以运行 Python 分析程序:"
echo "  python3 sqlite_analyzer.py"
echo ""
echo "要停止服务，运行: kill $OLLAMA_PID"
