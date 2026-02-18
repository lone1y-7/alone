# 取证工具启动脚本使用说明

## 概述

为了方便启动取证工具，提供了以下启动脚本，可以自动启动 API 服务和 UI 界面。

## 启动脚本

### 1. start.py (Python 脚本)
- **适用平台**: Linux / macOS / Windows
- **使用方式**: `python3 start.py`
- **功能**:
  - 自动检查是否有旧进程在运行
  - 依次启动 main.py (API 服务) 和 ui.py (UI 界面)
  - 处理 Ctrl+C 信号，确保进程正确关闭
  - 提供详细的启动状态信息

### 2. start.sh (Shell 脚本)
- **适用平台**: Linux / macOS
- **使用方式**: `./start.sh` 或 `bash start.sh`
- **功能**:
  - 清理旧进程
  - 后台启动 API 服务
  - 前台启动 UI 界面
  - UI 关闭后自动清理 API 进程

### 3. start.bat (批处理脚本)
- **适用平台**: Windows
- **使用方式**: 双击运行或在命令行执行 `start.bat`
- **功能**:
  - 清理旧进程
  - 后台启动 API 服务
  - 启动 UI 界面
  - UI 关闭后自动清理

## 使用方法

### Linux / macOS 系统

推荐使用 start.sh 脚本：

```bash
cd /path/to/forensic-tool
./start.sh
```

或者使用 Python 脚本：

```bash
python3 start.py
```

### Windows 系统

直接双击 `start.bat` 文件，或在命令行中执行：

```cmd
cd C:\path\to\forensic-tool
start.bat
```

## 启动流程

1. **检查旧进程**: 如果有旧的 main.py 或 ui.py 进程在运行，会先清理
2. **启动 API 服务**: 启动 main.py，等待 2-3 秒确保服务就绪
3. **启动 UI 界面**: 启动 ui.py，显示图形界面
4. **使用工具**: 在 UI 中进行扫描、查询等操作
5. **关闭程序**: 关闭 UI 窗口后，脚本会自动清理 API 进程

## 验证服务

启动后，可以通过以下方式验证 API 服务是否正常运行：

1. 访问 API 文档: http://localhost:8000/docs
2. 测试 API 端点:
   ```bash
   curl http://localhost:8000/
   ```
3. 查看日志:
   ```bash
   tail -f /tmp/api.log
   ```

## 手动启动（备选方案）

如果启动脚本遇到问题，也可以手动启动：

```bash
# 终端 1: 启动 API 服务
python3 main.py

# 终端 2: 启动 UI 界面
python3 ui.py
```

## 常见问题

### 问题 1: 端口 8000 被占用

**错误信息**: `Address already in use`

**解决方法**:
1. 找到占用端口的进程: `lsof -i :8000` (Linux/Mac) 或 `netstat -ano | findstr :8000` (Windows)
2. 杀死该进程或修改 main.py 中的端口号

### 问题 2: Python 依赖缺失

**错误信息**: `ModuleNotFoundError`

**解决方法**:
```bash
pip install -r requirements.txt
pip install fakeredis
```

### 问题 3: C 模块未编译

**错误信息**: `file not found` 或动态链接库加载失败

**解决方法**:
```bash
# Linux
gcc -shared -fPIC -o build/libscanner.so src/file_scanner.c -Wall

# Windows (使用 MSVC)
cl /LD src/file_scanner.c /Fe:build\scanner.dll
```

### 问题 4: UI 无法启动

**可能原因**: tkinter 未安装

**解决方法**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# macOS (通常已包含，如遇问题重新安装 Python)
brew reinstall python-tk
```

## 停止程序

### 使用脚本停止

如果在 Linux/Mac 上使用 start.sh 启动，只需关闭 UI 窗口即可，API 会自动停止。

### 手动停止

```bash
# 停止所有相关进程
pkill -f "python3 main.py"
pkill -f "python3 ui.py"

# Windows
taskkill /F /IM python.exe
```

## 文件说明

- `main.py`: FastAPI 主程序，提供 RESTful API 服务
- `ui.py`: tkinter 图形界面程序
- `start.py`: Python 启动脚本（跨平台）
- `start.sh`: Shell 启动脚本（Linux/Mac）
- `start.bat`: 批处理启动脚本（Windows）
- `requirements.txt`: Python 依赖包列表

## 技术支持

如遇到问题，请检查：
1. Python 版本是否为 3.7 或更高
2. 所有依赖是否已安装
3. C 模块是否已编译
4. 端口 8000 是否被占用
5. 日志文件 `/tmp/api.log` 中的错误信息
