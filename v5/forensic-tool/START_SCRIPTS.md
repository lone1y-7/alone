# 启动脚本说明

## 已创建的文件

### 1. start.py
- **类型**: Python 脚本
- **平台**: Linux / macOS / Windows
- **权限**: 可执行 (755)
- **大小**: 3.7 KB
- **使用方法**: `python3 start.py`

**功能特点**:
- 自动检查并清理旧进程
- 依次启动 API 服务和 UI 界面
- 处理 Ctrl+C 信号，优雅关闭
- 详细的启动状态信息
- 跨平台兼容

### 2. start.sh
- **类型**: Shell 脚本
- **平台**: Linux / macOS
- **权限**: 可执行 (755)
- **大小**: 989 字节
- **使用方法**: `./start.sh` 或 `bash start.sh`

**功能特点**:
- 快速启动
- 后台运行 API 服务
- 前台运行 UI 界面
- 自动清理进程
- 简洁高效

### 3. start.bat
- **类型**: Windows 批处理脚本
- **平台**: Windows
- **大小**: 411 字节
- **使用方法**: 双击运行或 `start.bat`

**功能特点**:
- Windows 原生支持
- 自动清理进程
- 启动 API 和 UI
- 自动关闭清理

### 4. START_GUIDE.md
- **类型**: 使用说明文档
- **大小**: 4.0 KB
- **内容**:
  - 详细的启动脚本使用说明
  - 各平台使用方法
  - 启动流程说明
  - 常见问题解答
  - 故障排查指南

### 5. QUICKSTART.md
- **类型**: 快速开始文档
- **大小**: 2.5 KB
- **内容**:
  - 一键启动命令
  - 基本使用步骤
  - 功能说明
  - 常用命令
  - 注意事项

## 使用示例

### Linux / macOS
```bash
# 方法 1: 使用 shell 脚本（推荐）
./start.sh

# 方法 2: 使用 Python 脚本
python3 start.py
```

### Windows
```cmd
# 方法 1: 双击 start.bat

# 方法 2: 命令行执行
start.bat

# 方法 3: 使用 Python 脚本
python start.py
```

## 启动流程

1. **检查旧进程**: 自动清理已运行的 main.py 和 ui.py 进程
2. **启动 API 服务**: 启动 main.py，等待 2-3 秒
3. **验证 API**: 确认 API 服务正常响应
4. **启动 UI 界面**: 启动 ui.py，显示图形界面
5. **等待使用**: 用户使用工具进行操作
6. **自动清理**: UI 关闭后自动停止 API 服务

## 验证启动成功

启动成功后，你会看到：

### API 服务
```
✓ API 服务启动成功 (PID: xxxx)
  API 地址: http://localhost:8000
  API 文档: http://localhost:8000/docs
```

### UI 界面
- 图形窗口打开
- 左侧显示包名列表
- 右侧显示操作按钮和结果区域

## 测试 API

```bash
# 测试服务状态
curl http://localhost:8000/

# 预期输出:
{"message":"取证比赛高速查询工具 API","version":"1.0.0"}
```

## 停止程序

### 使用启动脚本
- Linux/Mac: 关闭 UI 窗口即可
- Windows: 关闭 UI 窗口，按任意键退出

### 手动停止
```bash
# Linux / macOS
pkill -f "python3 main.py"
pkill -f "python3 ui.py"

# Windows
taskkill /F /IM python.exe
```

## 文件位置

所有文件位于: `/workspace/alone/v4/forensic-tool/`

```
forensic-tool/
├── start.py          # Python 启动脚本
├── start.sh          # Shell 启动脚本
├── start.bat         # Windows 批处理脚本
├── START_GUIDE.md    # 详细使用说明
├── QUICKSTART.md     # 快速开始指南
├── main.py           # API 主程序
└── ui.py             # UI 界面程序
```

## 优势

相比手动启动 `python main.py` 和 `python ui.py`，使用启动脚本的优势：

1. **一键启动**: 无需手动依次启动两个程序
2. **自动管理**: 自动处理进程清理和停止
3. **跨平台**: 提供多种平台支持
4. **错误处理**: 自动检测和报告启动错误
5. **日志记录**: API 日志输出到 `/tmp/api.log`
6. **用户体验**: 简化操作，提高效率

## 下一步

1. 选择适合你操作系统的启动脚本
2. 运行启动脚本
3. 使用 UI 界面进行扫描和查询
4. 查看 START_GUIDE.md 了解更多详情
5. 查看 QUICKSTART.md 快速上手

如有问题，请参考 START_GUIDE.md 中的"常见问题"部分。
