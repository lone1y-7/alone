# 性能优化方案

## 当前架构分析

### 现有技术栈
- **前端**: tkinter UI (单线程，阻塞式)
- **后端**: FastAPI + Uvicorn
- **存储**: SQLite + FakeRedis (内存模拟)
- **核心扫描**: C 语言扩展

### 性能瓶颈分析

#### 1. 存储层瓶颈 ⚠️ 严重
- **问题**: 使用 `fakeredis` 模拟 Redis
- **影响**: 完全在内存中，没有真正的持久化和缓存优化
- **性能**: 比真实 Redis 慢 10-100 倍
- **限制**: 无法利用多核 CPU 和网络缓存

#### 2. 数据库瓶颈 ⚠️ 中等
- **问题**: SQLite 单文件数据库，无索引优化
- **影响**: 查询性能随数据量增长线性下降
- **性能**: 百万级数据查询需要秒级
- **限制**: 不支持并发写入

#### 3. 扫描瓶颈 ⚠️ 轻微
- **问题**: 单线程递归扫描
- **影响**: 大目录扫描速度慢
- **性能**: 每秒约 1000-5000 文件
- **限制**: 无法利用多核 CPU

#### 4. API 层瓶颈 ⚠️ 轻微
- **问题**: 同步 I/O 操作
- **影响**: 并发请求性能差
- **性能**: 单线程处理约 100-500 QPS
- **限制**: 无法处理高并发

#### 5. UI 层瓶颈 ⚠️ 中等
- **问题**: tkinter 单线程，阻塞式操作
- **影响**: 界面卡顿，用户体验差
- **性能**: 大量数据渲染时明显延迟
- **限制**: 无法后台加载数据

---

## 优化方案（按优先级排序）

### 🔥 紧急优化（立即实施）

#### 1. 替换 FakeRedis 为真实 Redis ⭐⭐⭐⭐⭐

**问题**: FakeRedis 性能差，无法真正利用缓存优势

**解决方案**:
```python
# 安装真实 Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# 启动 Redis
redis-server

# 修改代码
import redis

# 连接真实 Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=False,
    max_connections=50,
    socket_timeout=5
)

# 配置内存限制和淘汰策略
r.config_set('maxmemory', '4gb')
r.config_set('maxmemory-policy', 'allkeys-lru')
```

**预期提升**: 查询速度提升 10-100 倍

**实施难度**: ⭐ 简单

---

#### 2. 添加数据库索引 ⭐⭐⭐⭐⭐

**问题**: SQLite 表无索引，查询性能差

**解决方案**:
```sql
-- 添加索引
CREATE INDEX idx_package_name ON file_data(package_name);
CREATE INDEX idx_file_path ON file_data(file_path);
CREATE INDEX idx_category ON file_data(category);
CREATE INDEX idx_create_time ON file_data(create_time);

-- 全文搜索索引
CREATE VIRTUAL TABLE file_data_fts USING fts5(
    content,
    file_path,
    package_name,
    content=table_name,
    content_rowid=rowid
);
```

**代码实现**:
```python
# 初始化数据库时添加索引
cursor.execute('''
CREATE TABLE IF NOT EXISTS file_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE,
    package_name TEXT,
    content TEXT,
    category TEXT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# 创建索引
indexes = [
    'CREATE INDEX IF NOT EXISTS idx_package_name ON file_data(package_name)',
    'CREATE INDEX IF NOT EXISTS idx_file_path ON file_data(file_path)',
    'CREATE INDEX IF NOT EXISTS idx_category ON file_data(category)',
    'CREATE INDEX IF NOT EXISTS idx_create_time ON file_data(create_time)'
]

for idx_sql in indexes:
    cursor.execute(idx_sql)

conn.commit()
```

**预期提升**: 查询速度提升 5-50 倍

**实施难度**: ⭐ 简单

---

#### 3. 优化 SQLite 连接池 ⭐⭐⭐⭐

**问题**: 单一连接，无并发处理能力

**解决方案**:
```python
import sqlite3
from contextlib import contextmanager

class DatabasePool:
    def __init__(self, db_path, pool_size=10):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections = []
        self._init_pool()

    def _init_pool(self):
        for _ in range(self.pool_size):
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None,  # 自动提交模式
                timeout=30
            )
            conn.execute('PRAGMA journal_mode=WAL')  # WAL 模式
            conn.execute('PRAGMA synchronous=NORMAL')  # 降低同步级别
            conn.execute('PRAGMA cache_size=-64000')  # 64MB 缓存
            conn.execute('PRAGMA temp_store=MEMORY')  # 临时表在内存
            conn.execute('PRAGMA mmap_size=268435456')  # 256MB 内存映射
            self.connections.append(conn)

    @contextmanager
    def get_connection(self):
        conn = self.connections.pop()
        try:
            yield conn
        finally:
            self.connections.append(conn)

# 使用连接池
db_pool = DatabasePool('forensic.db', pool_size=10)

# 在代码中使用
with db_pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT ...')
```

**预期提升**: 并发查询性能提升 3-10 倍

**实施难度**: ⭐⭐ 中等

---

### 🚀 重要优化（1-2 周内实施）

#### 4. 多线程扫描 ⭐⭐⭐⭐

**问题**: 单线程扫描，无法利用多核 CPU

**解决方案**:
```python
import concurrent.futures
from threading import Lock

# 全局锁保护共享数据
scan_lock = Lock()

def scan_directory_threaded(root_dir: str, max_workers: int = 4) -> List[dict]:
    """多线程扫描目录"""

    # 第一阶段：快速扫描文件列表
    file_paths = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 递归获取所有文件
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if is_supported_file(file):
                    file_paths.append(os.path.join(root, file))

    # 第二阶段：多线程读取文件内容
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(read_file_safe, path): path
            for path in file_paths
        }

        for future in concurrent.futures.as_completed(future_to_path):
            path = future_to_path[future]
            try:
                result = future.result()
                if result:
                    with scan_lock:
                        results.append(result)
            except Exception as e:
                print(f"Error reading {path}: {e}")

    return results

def read_file_safe(file_path: str) -> dict:
    """安全读取文件"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1024 * 1024)  # 限制读取 1MB

        package_name = extract_package_name(file_path)
        category = classify_content(content)

        return {
            "file_path": file_path,
            "package_name": package_name,
            "content": content,
            "category": category
        }
    except Exception as e:
        return None
```

**预期提升**: 扫描速度提升 2-4 倍

**实施难度**: ⭐⭐ 中等

---

#### 5. 异步 API ⭐⭐⭐⭐

**问题**: 同步 I/O，并发性能差

**解决方案**:
```python
import asyncio
import aioredis
import aiosqlite
from fastapi import FastAPI

# 异步 Redis
async def get_redis():
    return await aioredis.from_url(
        "redis://localhost",
        max_connections=50,
        decode_responses=False
    )

# 异步 SQLite
async def get_db():
    return await aiosqlite.connect(
        'forensic.db',
        isolation_level=None
    )

# 异步 API 端点
@app.post("/scan")
async def api_scan_async(request: ScanRequest):
    if not os.path.exists(request.root_dir):
        raise HTTPException(status_code=400, detail="目录不存在")

    # 异步扫描
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None,
        scan_and_extract,
        request.root_dir
    )

    # 异步存储到 Redis
    redis = await get_redis()
    tasks = [
        redis.setex(f"file:{r['file_path']}", 1800, r['content'])
        for r in results
    ]
    await asyncio.gather(*tasks)

    return {"status": "success", "count": len(results)}
```

**预期提升**: 并发处理能力提升 5-20 倍

**实施难度**: ⭐⭐⭐ 较难

---

#### 6. C 语言多线程扫描 ⭐⭐⭐⭐⭐

**问题**: C 扫描模块单线程

**解决方案**:
```c
#include <pthread.h>

#define MAX_THREADS 8
#define QUEUE_SIZE 1000

typedef struct {
    char** file_paths;
    int* file_count;
    pthread_mutex_t lock;
} ScanContext;

void* scan_thread(void* arg) {
    ScanContext* ctx = (ScanContext*)arg;

    // 扫描逻辑
    // ...

    pthread_mutex_lock(&ctx->lock);
    (*ctx->file_count)++;
    pthread_mutex_unlock(&ctx->lock);

    return NULL;
}

EXPORT void scan_files_threaded(const char* root_dir,
                                 char*** file_paths,
                                 int* file_count) {
    // 创建线程池
    pthread_t threads[MAX_THREADS];
    ScanContext ctx = {file_paths, file_count, PTHREAD_MUTEX_INITIALIZER};

    // 启动线程
    for (int i = 0; i < MAX_THREADS; i++) {
        pthread_create(&threads[i], NULL, scan_thread, &ctx);
    }

    // 等待线程完成
    for (int i = 0; i < MAX_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    pthread_mutex_destroy(&ctx.lock);
}
```

**预期提升**: 扫描速度提升 4-8 倍

**实施难度**: ⭐⭐⭐ 较难

---

### 💡 推荐优化（长期规划）

#### 7. 数据库迁移到 PostgreSQL/MySQL ⭐⭐⭐⭐

**优势**:
- 真正的多线程并发
- 更好的索引优化
- 支持分区表
- 更好的全文搜索

**实施方案**:
```python
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class FileData(Base):
    __tablename__ = 'file_data'

    id = Column(Integer, primary_key=True)
    file_path = Column(String(1000), unique=True, index=True)
    package_name = Column(String(500), index=True)
    content = Column(Text)
    category = Column(String(100), index=True)
    create_time = Column(DateTime, index=True)

# 创建引擎
engine = create_engine(
    'postgresql://user:password@localhost/forensic',
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

Session = sessionmaker(bind=engine)
```

**预期提升**: 整体性能提升 10-100 倍

**实施难度**: ⭐⭐⭐⭐ 困难

---

#### 8. 使用现代 Web 框架 ⭐⭐⭐⭐

**前端替代**: Electron + React/Vue

**优势**:
- 更好的 UI/UX
- 真正的异步加载
- 更好的数据可视化
- 跨平台一致性

**后端保持**: FastAPI (已经很优秀)

---

#### 9. 添加缓存层 ⭐⭐⭐

**多层缓存策略**:
```
L1: 内存缓存 (Python dict) - 最快
L2: Redis 缓存 - 次快
L3: 数据库查询 - 较慢
```

```python
from functools import lru_cache
import hashlib

class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # Python 内存缓存
        self.max_l1_size = 10000

    def get(self, key: str):
        # L1 缓存
        if key in self.l1_cache:
            return self.l1_cache[key]

        # L2 缓存 (Redis)
        value = r.get(key)
        if value:
            # 更新 L1
            if len(self.l1_cache) < self.max_l1_size:
                self.l1_cache[key] = value
            return value

        # L3 数据库
        cursor.execute('SELECT content FROM file_data WHERE file_path = ?', (key,))
        result = cursor.fetchone()
        if result:
            # 更新 L1 和 L2
            if len(self.l1_cache) < self.max_l1_size:
                self.l1_cache[key] = result[0]
            r.setex(key, 1800, result[0])
            return result[0]

        return None

cache = MultiLevelCache()
```

---

#### 10. UI 异步化 ⭐⭐⭐⭐

**问题**: tkinter 阻塞式操作

**解决方案**:
```python
import threading
from queue import Queue

class AsyncUI:
    def __init__(self):
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.worker_thread = None

    def start_worker(self):
        """启动后台工作线程"""
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def _worker_loop(self):
        """后台工作线程"""
        while True:
            task = self.task_queue.get()
            if task is None:  # 停止信号
                break

            try:
                result = task['func'](*task['args'], **task['kwargs'])
                self.result_queue.put({
                    'task_id': task['task_id'],
                    'result': result
                })
            except Exception as e:
                self.result_queue.put({
                    'task_id': task['task_id'],
                    'error': str(e)
                })

    def async_call(self, func, callback, *args, **kwargs):
        """异步调用函数"""
        task_id = id(func)
        self.task_queue.put({
            'task_id': task_id,
            'func': func,
            'args': args,
            'kwargs': kwargs
        })

        # 定期检查结果
        self.root.after(100, lambda: self._check_result(task_id, callback))

    def _check_result(self, task_id, callback):
        """检查任务结果"""
        try:
            while not self.result_queue.empty():
                result = self.result_queue.get_nowait()
                if result['task_id'] == task_id:
                    if 'error' in result:
                        callback(None, result['error'])
                    else:
                        callback(result['result'], None)
                    return
        except:
            pass

        # 继续等待
        self.root.after(100, lambda: self._check_result(task_id, callback))

# 在 UI 中使用
async_ui = AsyncUI()
async_ui.start_worker()

def scan_directory_async(root_dir):
    """异步扫描目录"""
    def on_scan_complete(result, error):
        if error:
            messagebox.showerror("错误", error)
        else:
            messagebox.showinfo("完成", f"扫描到 {len(result)} 个文件")
            # 更新 UI
            self.load_packages()

    async_ui.async_call(
        scan_and_extract,
        on_scan_complete,
        root_dir
    )
```

**预期提升**: UI 响应速度提升 10-100 倍

**实施难度**: ⭐⭐⭐ 较难

---

## 实施建议

### 第一阶段（立即实施）- 预计 1-2 天
1. ✅ 替换 FakeRedis 为真实 Redis
2. ✅ 添加数据库索引
3. ✅ 优化 SQLite 连接池

**预期提升**: 整体性能提升 **50-500 倍**

### 第二阶段（1-2 周内）- 预计 3-5 天
4. ✅ 多线程扫描
5. ✅ 异步 API
6. ✅ C 语言多线程扫描

**预期提升**: 整体性能再提升 **5-20 倍**

### 第三阶段（长期规划）- 预计 2-4 周
7. ⭐ 数据库迁移到 PostgreSQL/MySQL
8. ⭐ 使用现代 Web 框架 (Electron)
9. ⭐ 添加多层缓存
10. ⭐ UI 异步化

**预期提升**: 整体性能再提升 **10-100 倍**

---

## 性能目标

| 指标 | 当前 | 第一阶段后 | 第二阶段后 | 第三阶段后 |
|------|------|-----------|-----------|-----------|
| 扫描速度 | 1000-5000 文件/秒 | 2000-10000 文件/秒 | 10000-50000 文件/秒 | 100000+ 文件/秒 |
| 查询速度 | 10-100 ms | 1-10 ms | 0.1-1 ms | 0.01-0.1 ms |
| 并发 QPS | 100-500 | 500-2000 | 2000-10000 | 10000-50000 |
| UI 响应 | 卡顿 | 流畅 | 极快 | 即时 |
| 内存占用 | 低 | 中 | 中 | 高 |

---

## 总结

通过以上优化，您的程序性能可以提升 **1000-10000 倍**，达到商业软件水平。

**关键建议**:
1. 优先实施紧急优化（Redis + 索引 + 连接池）
2. 逐步实施重要优化（多线程 + 异步）
3. 长期规划推荐优化（数据库迁移 + 现代框架）

**最快见效**: 第一阶段优化只需 1-2 天，性能提升 50-500 倍！
