#!/bin/bash
echo "编译 C 语言核心模块..."

# 确保目录存在
mkdir -p build
mkdir -p src

# 仅处理 Linux 环境
if [[ "$(uname -s)" == "Linux" ]]; then
    echo "检测到 Linux 环境，生成 SO..."
    gcc -shared -fPIC -o build/libscanner.so src/file_scanner.c -Wall
    if [ $? -eq 0 ] && [ -f "build/libscanner.so" ]; then
        echo "编译成功！"
        echo "动态链接库已生成：build/libscanner.so"
    else
        echo "编译失败！"
        exit 1
    fi
else
    echo "错误：Linux 以外的环境请使用 build.bat（VS x64 工具）！"
    exit 1
fi