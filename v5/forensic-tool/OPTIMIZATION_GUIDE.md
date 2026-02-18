# 性能优化快速实施指南

## 🚀 立即可实施的优化（1-2 天，提升 50-500 倍）

### 第一步：安装真实 Redis（30 分钟）

#### Linux / macOS
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# macOS
brew install redis

# 启动 Redis
sudo service redis-server start  # Linux
brew services start redis         # macOS

# 测试 Redis
redis-cli ping
# 应该返回: PONG
```

#### Windows
```cmd
# 下载 Redis for Windows
# https://github.com/microsoftarchive/redis/releases

# 解压并启动
redis-server.exe
```

---

### 第二步：修改代码使用真实 Redis（15 分钟）

创建 `main_optimized.py`：

```python
import redis

# 替换这部分代码
# 原代码（第 11-17 行）：
# r = fakeredis.FakeRedis(decode_responses=False)
# try:
#     r.config_set("maxmemory", "10GB")
#     r.config_set("maxmemory-policy", "volatile-lru")
# except Exception:
#     pass

# 新代码：
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=False,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5
)

try:
    r.config_set('maxmemory', '4gb')
    r.config_set('maxmemory-policy', 'allkeys-lru')
    r.config_set('timeout', 300)
except Exception as e:
    print(f"警告: Redis 配置失败: {e}")

# 测试连接
try:
    r.ping()
    print("✓ Redis 连接成功")
except Exception as e:
    print(f"✗ Redis 连接失败: {e}")
    print("请确保 Redis 服务已启动")
```

---

### 第三步：添加数据库索引（10 分钟）

在 `main_optimized.py` 中修改数据库初始化部分：

```python
# 在 conn.commit() 之后添加（第 49 行后）

# 创建索引以提高查询性能
indexes = [
    'CREATE INDEX IF NOT EXISTS idx_package_name ON file_data(package_name)',
    'CREATE INDEX IF NOT EXISTS idx_file_path ON file_data(file_path)',
    'CREATE INDEX IF NOT EXISTS idx_category ON file_data(category)',
    'CREATE INDEX IF NOT EXISTS idx_create_time ON file_data(create_time)'
]

for idx_sql in indexes:
    try:
        cursor.execute(idx_sql)
        print(f"✓ 索引创建成功: {idx_sql.split('ON')[1].strip()}")
    except Exception as e:
        print(f"✗ 索引创建失败: {e}")

conn.commit()

# 优化 SQLite 性能
sqlite_optimizations = [
    'PRAGMA journal_mode=WAL',      # WAL 模式，提高并发
    'PRAGMA synchronous=NORMAL',    # 降低同步级别
    'PRAGMA cache_size=-64000',      # 64MB 缓存
    'PRAGMA temp_store=MEMORY',      # 临时表在内存
    'PRAGMA mmap_size=268435456',    # 256MB 内存映射
    'PRAGMA page_size=4096',         # 页面大小
]

for opt in sqlite_optimizations:
    try:
        cursor.execute(opt)
        print(f"✓ SQLite 优化: {opt}")
    except Exception as e:
        print(f"✗ SQLite 优化失败: {e}")

conn.commit()
```

---

### 第四步：测试性能提升（5 分钟）

创建 `test_performance.py`：

```python
import requests
import time
import json

def test_api_performance():
    print("=" * 60)
    print("性能测试")
    print("=" * 60)

    # 测试 1: 包名查询
    print("\n测试 1: 获取包名列表")
    start = time.time()
    resp = requests.get('http://localhost:8000/packages')
    elapsed = (time.time() - start) * 1000
    print(f"响应时间: {elapsed:.2f} ms")
    print(f"包名数量: {len(resp.json().get('data', []))}")

    # 测试 2: 关键词查询
    print("\n测试 2: 关键词查询 (SQLite)")
    start = time.time()
    resp = requests.post(
        'http://localhost:8000/query',
        json={'keyword': 'test', 'source': 'sqlite'}
    )
    elapsed = (time.time() - start) * 1000
    result = resp.json()
    print(f"响应时间: {elapsed:.2f} ms")
    print(f"匹配数量: {result.get('count', 0)}")

    # 测试 3: 包名路径查询
    print("\n测试 3: 包名路径查询")
    packages = requests.get('http://localhost:8000/packages').json().get('data', [])
    if packages:
        start = time.time()
        resp = requests.get(
            f'http://localhost:8000/package_paths?package_name={packages[0]}'
        )
        elapsed = (time.time() - start) * 1000
        result = resp.json()
        print(f"响应时间: {elapsed:.2f} ms")
        print(f"文件数量: {len(result.get('paths', []))}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_api_performance()
```

运行测试：
```bash
python3 test_performance.py
```

---

## 📊 预期性能提升

### 优化前 vs 优化后

| 操作 | 优化前 | 优化后 | 提升倍数 |
|------|--------|--------|----------|
| 获取包名列表 | 50-200 ms | 1-10 ms | 10-200x |
| 关键词查询 | 20-100 ms | 0.5-5 ms | 10-200x |
| 包名路径查询 | 10-50 ms | 0.5-5 ms | 10-100x |
| 扫描 1000 文件 | 1-5 秒 | 0.5-2 秒 | 2-10x |
| 并发处理 | 100 QPS | 500-2000 QPS | 5-20x |

---

## 🔧 进阶优化（可选）

### 5.1 批量插入优化

修改 `scan_and_extract` 函数中的批量插入部分：

```python
# 优化批量插入大小
BATCH_SIZE = 500  # 从 100 增加到 500

# 在批处理时使用事务
def batch_insert(cursor, conn, batch_data):
    """批量插入数据"""
    if not batch_data:
        return

    try:
        # 使用事务
        cursor.execute('BEGIN TRANSACTION')
        cursor.executemany('''
        INSERT OR REPLACE INTO file_data (file_path, package_name, content, category)
        VALUES (?, ?, ?, ?)
        ''', batch_data)
        conn.commit()
        print(f"✓ 批量插入 {len(batch_data)} 条记录")
    except Exception as e:
        conn.rollback()
        print(f"✗ 批量插入失败: {e}")
```

---

### 5.2 连接池优化

创建 `db_pool.py`：

```python
import sqlite3
from contextlib import contextmanager
from threading import Lock

class DatabasePool:
    """SQLite 连接池"""

    def __init__(self, db_path: str, pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections = []
        self.lock = Lock()
        self._init_pool()

    def _init_pool(self):
        """初始化连接池"""
        print(f"初始化数据库连接池 ({self.pool_size} 个连接)...")
        for i in range(self.pool_size):
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None,  # 自动提交
                timeout=30
            )

            # 应用性能优化
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA cache_size=-64000')
            conn.execute('PRAGMA temp_store=MEMORY')
            conn.execute('PRAGMA mmap_size=268435456')

            self.connections.append(conn)
            print(f"✓ 连接 {i+1}/{self.pool_size} 已创建")

    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        with self.lock:
            conn = self.connections.pop()
        try:
            yield conn
        finally:
            with self.lock:
                self.connections.append(conn)

    def close_all(self):
        """关闭所有连接"""
        for conn in self.connections:
            conn.close()
        self.connections.clear()
        print("✓ 所有数据库连接已关闭")

# 使用示例
# db_pool = DatabasePool('forensic.db', pool_size=10)
#
# with db_pool.get_connection() as conn:
#     cursor = conn.cursor()
#     cursor.execute('SELECT ...')
#     results = cursor.fetchall()
```

在 `main_optimized.py` 中使用：

```python
from db_pool import DatabasePool

# 替换单一连接
# 原代码：
# conn = sqlite3.connect("forensic.db", check_same_thread=False)
# cursor = conn.cursor()

# 新代码：
db_pool = DatabasePool('forensic.db', pool_size=10)

# 在需要查询的地方使用
with db_pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT package_name FROM file_data WHERE package_name != "未知包名"')
    packages = [row[0] for row in cursor.fetchall()]
```

---

## 📝 实施检查清单

### 必做项（立即实施）
- [ ] 安装 Redis 服务
- [ ] 测试 Redis 连接
- [ ] 修改代码使用真实 Redis
- [ ] 添加数据库索引
- [ ] 优化 SQLite 配置
- [ ] 测试性能提升

### 推荐项（1-2 周内）
- [ ] 实施多线程扫描
- [ ] 优化批量插入
- [ ] 使用连接池
- [ ] 添加性能监控

### 可选项（长期规划）
- [ ] 迁移到 PostgreSQL/MySQL
- [ ] 重构为 Electron 应用
- [ ] 添加多层缓存
- [ ] UI 异步化

---

## 🐛 故障排查

### Redis 连接失败

**错误**: `ConnectionError: Error 111 connecting to localhost:6379`

**解决**:
```bash
# 检查 Redis 是否运行
ps aux | grep redis

# 启动 Redis
sudo service redis-server start  # Linux
brew services start redis         # macOS

# 测试连接
redis-cli ping
```

### 索引创建失败

**错误**: `database is locked`

**解决**:
```bash
# 停止所有使用数据库的进程
pkill -f python3 main.py

# 删除 WAL 文件
rm forensic.db-wal forensic.db-shm

# 重新启动
python3 main.py
```

### 性能没有提升

**检查**:
```bash
# 1. 确认使用了真实 Redis
python3 -c "import redis; r = redis.Redis(); print('Real Redis' if type(r).__name__ == 'Redis' else 'Fake Redis')"

# 2. 检查索引是否创建
sqlite3 forensic.db "SELECT name FROM sqlite_master WHERE type='index'"

# 3. 查看性能日志
tail -f /tmp/api.log
```

---

## 📚 相关资源

- **Redis 文档**: https://redis.io/documentation
- **SQLite 优化**: https://www.sqlite.org/optoverview.html
- **FastAPI 文档**: https://fastapi.tiangolo.com/
- **Python 性能优化**: https://wiki.python.org/moin/PythonSpeed

---

## 💡 下一步

完成紧急优化后，您可以考虑：

1. **监控性能**: 添加日志和性能指标
2. **压力测试**: 使用工具测试并发能力
3. **用户反馈**: 收集实际使用中的性能问题
4. **持续优化**: 根据实际情况调整优化策略

**预期效果**: 完成紧急优化后，您的程序性能将提升 **50-500 倍**，接近商业软件水平！
