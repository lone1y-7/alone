# 快速开始

## 一键启动

### Linux / macOS
```bash
./start.sh
```

### Windows
双击 `start.bat` 文件

## 或使用 Python 脚本（跨平台）
```bash
python3 start.py
```

## 使用步骤

1. **启动程序**
   - 运行启动脚本
   - 等待 API 服务和 UI 界面启动完成

2. **扫描目录**
   - 在 UI 界面中点击"浏览"按钮选择要扫描的目录
   - 点击"扫描"按钮开始扫描
   - 等待扫描完成

3. **查看包名**
   - 左侧列表会显示扫描到的包名
   - 点击"刷新包名"按钮更新列表

4. **查看文件路径**
   - 双击包名列表中的任意包名
   - 会弹出该包名对应的所有文件路径
   - 选择一个路径并点击"打开选中路径"

5. **关键词查询**
   - 在"查询关键词"输入框中输入关键词
   - 选择数据源：Redis（高速）或 SQLite（本地）
   - 点击"查询"按钮
   - 右侧文本框会显示查询结果

6. **关闭程序**
   - 直接关闭 UI 窗口
   - API 服务会自动停止

## 功能说明

### API 端点

- `GET /` - 服务状态
- `GET /packages` - 获取包名列表
- `GET /package_paths?package_name=xxx` - 获取包名对应的文件路径
- `POST /scan` - 扫描目录
- `POST /query` - 关键词查询
- `POST /release_memory` - 释放 Redis 内存
- `POST /clear_data` - 清空所有数据

### API 文档
启动后访问: http://localhost:8000/docs

## 常用命令

### 手动启动
```bash
# 终端 1
python3 main.py

# 终端 2
python3 ui.py
```

### 停止服务
```bash
pkill -f "python3 main.py"
pkill -f "python3 ui.py"
```

### 查看日志
```bash
tail -f /tmp/api.log
```

### 测试 API
```bash
# 测试服务状态
curl http://localhost:8000/

# 获取包名列表
curl http://localhost:8000/packages

# 查询包名路径
curl "http://localhost:8000/package_paths?package_name=com.example"

# 扫描目录
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"root_dir": "/path/to/scan"}'

# 关键词查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"keyword": "password", "source": "sqlite"}'
```

## 注意事项

1. 确保端口 8000 未被占用
2. 首次运行前需要安装依赖：`pip install -r requirements.txt`
3. 需要编译 C 模块（如果未预编译）
4. Linux/Mac 需要 tkinter 库：`sudo apt-get install python3-tk`

## 故障排查

如果遇到问题，请查看 `START_GUIDE.md` 中的"常见问题"部分。
