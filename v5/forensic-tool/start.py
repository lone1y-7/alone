#!/usr/bin/env python3
"""
取证工具启动脚本
自动启动 API 服务和 UI 界面
"""

import subprocess
import sys
import os
import time
import signal

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

def check_process_running(process_name):
    """检查进程是否正在运行"""
    try:
        result = subprocess.run(['pgrep', '-f', process_name], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def start_api():
    """启动 API 服务"""
    print("正在启动 API 服务...")
    api_process = subprocess.Popen(
        [sys.executable, 'main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=SCRIPT_DIR
    )

    # 等待 API 启动
    time.sleep(2)

    # 检查进程是否还在运行
    if api_process.poll() is None:
        print("✓ API 服务启动成功 (PID: {})".format(api_process.pid))
        print("  API 地址: http://localhost:8000")
        print("  API 文档: http://localhost:8000/docs")
        print()
        return api_process
    else:
        print("✗ API 服务启动失败")
        stdout, stderr = api_process.communicate()
        if stderr:
            print("错误信息:", stderr.decode())
        return None

def start_ui():
    """启动 UI 界面"""
    print("正在启动 UI 界面...")
    ui_process = subprocess.Popen(
        [sys.executable, 'ui.py'],
        cwd=SCRIPT_DIR
    )

    time.sleep(1)

    if ui_process.poll() is None:
        print("✓ UI 界面启动成功 (PID: {})".format(ui_process.pid))
        print()
        return ui_process
    else:
        print("✗ UI 界面启动失败")
        return None

def cleanup(api_process, ui_process):
    """清理进程"""
    print("\n正在关闭程序...")

    if ui_process and ui_process.poll() is None:
        print("正在关闭 UI 界面...")
        ui_process.terminate()
        try:
            ui_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ui_process.kill()

    if api_process and api_process.poll() is None:
        print("正在关闭 API 服务...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()

    print("✓ 程序已关闭")

def main():
    print("=" * 50)
    print("取证比赛高速查询工具 - 启动程序")
    print("=" * 50)
    print()

    # 检查是否已经有进程在运行
    if check_process_running('main.py'):
        print("警告: API 服务已经在运行中")
        print("如果需要重新启动，请先手动关闭已有进程")
        print()

    # 启动 API 服务
    api_process = start_api()
    if not api_process:
        print("无法启动 API 服务，程序退出")
        return

    # 启动 UI 界面
    ui_process = start_ui()
    if not ui_process:
        print("无法启动 UI 界面，正在关闭 API 服务...")
        api_process.terminate()
        api_process.wait()
        return

    print("=" * 50)
    print("程序已启动，请使用 UI 界面进行操作")
    print("按 Ctrl+C 关闭程序")
    print("=" * 50)
    print()

    # 注册信号处理函数
    def signal_handler(signum, frame):
        cleanup(api_process, ui_process)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # 等待 UI 进程结束
        ui_process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(api_process, ui_process)

if __name__ == "__main__":
    main()
