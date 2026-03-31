# Linux 运行步骤

## 环境要求

- 操作系统: Linux (推荐 Ubuntu/Debian)
- Python 版本: 3.11+
- 编译器: GCC 12.0+

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd forensic-tool
pip3 install -r requirements.txt
pip3 install fakeredis
```

### 2. 编译 C 语言模块

```bash
# 编译 Linux 版本的动态链接库
gcc -shared -fPIC -o build/libscanner.so src/file_scanner.c -Wall

# 验证编译结果
ls -lh build/libscanner.so
```

### 3. 创建测试数据（可选）

```bash
# 创建测试目录
mkdir -p test_data/data/data/com.tencent.mm
mkdir -p test_data/data/data/com.alipay.android
mkdir -p test_data/var/mobile/Containers/Bundle/Application/ABC123/com.apple.Safari

# 创建微信测试数据
cat > test_data/data/data/com.tencent.mm/MicroMsg.db << 'EOF'
-- SQLite database for WeChat messages
CREATE TABLE messages (id INTEGER PRIMARY KEY, content TEXT, timestamp INTEGER);
INSERT INTO messages VALUES (1, 'password: wx123456', 1640000000);
INSERT INTO messages VALUES (2, 'latitude: 39.9042, longitude: 116.4074', 1640000001);
INSERT INTO messages VALUES (3, 'token: abc123def456', 1640000002);
EOF

# 创建支付宝测试数据
cat > test_data/data/data/com.alipay.android/alipay_config.json << 'EOF'
{
  "app_id": "2021001234567890",
  "auth_token": "alipay_token_xyz789",
  "user_id": "2088001234567890",
  "password": "alipay_pwd_123456"
}
EOF

# 创建 Safari 测试数据
cat > test_data/var/mobile/Containers/Bundle/Application/ABC123/com.apple.Safari/history.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
  <key>History</key>
  <array>
    <string>https://www.example.com/login?password=user123</string>
  </array>
  <key>Token</key>
  <string>safari_token_abc123</string>
</dict>
</plist>
EOF

# 创建系统日志
cat > test_data/system.log << 'EOF'
[2026-02-11 10:00:00] INFO: System started
[2026-02-11 10:05:00] ERROR: Failed to connect to database
[2026-02-11 10:10:00] WARNING: GPS signal weak
EOF
```

## 运行步骤

### 方法 1: 后台运行 API 服务

```bash
# 启动 API 服务（后台运行）
nohup python3 main.py > /tmp/api.log 2>&1 &

# 查看启动日志
tail -f /tmp/api.log
```

### 方法 2: 前台运行 API 服务

```bash
# 启动 API 服务（前台运行）
python3 main.py
```

服务将运行在: http://localhost:8000

### 方法 3: 启动图形界面

```bash
# 确保先启动 API 服务（方法 1 或 2）
# 然后启动 GUI
python3 ui.py
```

## API 使用示例

### 1. 健康检查

```bash
curl http://localhost:8000/
```

响应:
```json
{
  "message": "取证比赛高速查询工具 API",
  "version": "1.0.0"
}
```

### 2. 扫描目录

```bash
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"root_dir": "/path/to/scan"}'
```

响应:
```json
{
  "status": "success",
  "count": 4,
  "message": "扫描到4个文件"
}
```

### 3. 获取包名列表

```bash
curl http://localhost:8000/packages
```

响应:
```json
{
  "data": [
    "com.alipay.android",
    "com.tencent.mm"
  ]
}
```

### 4. 关键词查询

```bash
# 使用 SQLite 查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"keyword": "password", "source": "sqlite"}'

# 使用 Redis 查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"keyword": "password", "source": "redis"}'
```

响应:
```json
{
  "status": "success",
  "cost_ms": 0.38,
  "count": 2,
  "data": [
    {
      "file_path": "/path/to/file.db",
      "content": "...",
      "source": "sqlite"
    }
  ]
}
```

### 5. 释放内存

```bash
curl -X POST http://localhost:8000/release_memory
```

响应:
```json
{
  "status": "success",
  "message": "内存已释放"
}
```

## 停止服务

```bash
# 查找进程
ps aux | grep main.py

# 停止进程
pkill -f main.py
```

## API 文档

启动服务后，可以访问自动生成的 API 文档:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 常见问题

### 1. 编译错误: `windows.h: No such file or directory`

**原因**: 代码是 Windows 版本，需要使用 Linux 版本的 C 代码

**解决**: 确保使用 `src/file_scanner.c`（Linux 版本）

### 2. 运行错误: `cannot open shared object file`

**原因**: C 模块未编译或路径错误

**解决**:
```bash
# 重新编译
gcc -shared -fPIC -o build/libscanner.so src/file_scanner.c -Wall

# 验证文件存在
ls -lh build/libscanner.so
```

### 3. 扫描失败: `Connection aborted`

**原因**: 内存管理问题

**解决**: 确保使用修复后的 `main.py`（已移除手动内存释放）

### 4. 端口被占用

**原因**: 8000 端口已被其他进程使用

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 或者修改 main.py 中的端口号
uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 性能优化建议

1. **定期释放内存**: 扫描大量文件后，调用 `/release_memory` 接口
2. **使用 Redis 缓存**: 对于重复查询，使用 `source: "redis"` 获得更好性能
3. **限制文件大小**: 代码已限制最大 100MB，避免处理超大文件
4. **批量查询**: 可以一次发送多个关键词，减少网络请求

## 支持的文件类型

| 扩展名 | 说明 |
|--------|------|
| .db | 数据库文件 |
| .sqlite | SQLite 数据库 |
| .txt | 文本文件 |
| .rdb | Redis 数据库 |
| .aof | Redis AOF 文件 |
| .xml | XML 配置文件 |
| .json | JSON 配置文件 |
| .log | 日志文件 |
| .plist | iOS 属性列表 |

## 下一步

- 查看 README.md 了解更多功能
- 访问 http://localhost:8000/docs 查看 API 文档
- 运行 `python3 ui.py` 启动图形界面
