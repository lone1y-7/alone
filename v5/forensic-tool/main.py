import ctypes
import os
import sqlite3
import time
from typing import List
import redis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_pool import DatabasePool

# 初始化Redis（模拟）
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
    r.ping()
    print("✓ Redis 连接成功")
except Exception as e:
    print(f"✗ Redis 连接失败: {e}")

# 加载C模块（兼容Windows/Linux）
if os.name == "posix":
    lib = ctypes.CDLL("./build/libscanner.so")
elif os.name == "nt":
    lib = ctypes.CDLL("./build/scanner.dll")
else:
    raise Exception("不支持的系统")

# 设置C函数参数/返回值类型
lib.scan_files.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)),
                           ctypes.POINTER(ctypes.c_int)]
lib.scan_files.restype = None
lib.extract_content.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
lib.extract_content.restype = ctypes.c_char_p
lib.free_files.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]
lib.free_files.restype = None

# 初始化SQLite数据库
print("正在初始化数据库连接池...")
db_pool = DatabasePool('forensic.db', pool_size=10)

with db_pool.get_connection() as conn:
    cursor = conn.cursor()
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

    # 添加索引
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_package_name ON file_data(package_name)',
        'CREATE INDEX IF NOT EXISTS idx_file_path ON file_data(file_path)',
        'CREATE INDEX IF NOT EXISTS idx_category ON file_data(category)',
        'CREATE INDEX IF NOT EXISTS idx_create_time ON file_data(create_time)'
    ]
    for idx_sql in indexes:
        cursor.execute(idx_sql)

    conn.commit()

print("✓ 数据库初始化完成")

# 存储最新扫描的包名列表
latest_packages = set()

# 存储包名到文件路径的映射（每个包名对应多个文件路径）
package_to_paths = {}

# 初始化FastAPI
app = FastAPI(title="取证比赛高速查询工具")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== 核心修改：无差别包名识别 =====================
def is_valid_package_name(name: str) -> bool:
    """简化包名验证：只要符合「反向域名格式」就认定为有效包名"""
    if "." not in name:
        return False  # 必须包含.（如 com.apple.freeform）
    segments = name.split(".")
    for seg in segments:
        if not seg or not seg[0].isalnum():
            return False  # 每段非空，且以字母/数字开头
        for char in seg:
            if not (char.isalnum() or char == "_"):
                return False  # 只允许字母/数字/下划线
    return True


def extract_package_name(file_path: str) -> str:
    """从任意路径中提取所有可能的有效包名（无平台限制）"""
    # 标准化路径分隔符
    normalized_path = file_path.replace("\\", "/")
    # 分割路径为片段
    path_segments = [seg for seg in normalized_path.split("/") if seg]

    # 目录黑名单（排除明显非包名的目录）
    dir_blacklist = ['library', 'documents', 'preferences', 'cache', 'tmp', 'system', 'var', 'usr', 'home', 'root']

    # 遍历所有路径片段，查找有效包名
    for seg in path_segments:
        seg_lower = seg.lower()
        if seg_lower in dir_blacklist:
            continue
        # 移除可能的文件扩展名（如 .app .plist .db）
        for ext in ['.app', '.plist', '.db', '.txt', '.xml', '.json', '.log']:
            if seg.lower().endswith(ext):
                seg = seg[:-len(ext)]
                break
        # 验证是否为有效包名
        if is_valid_package_name(seg):
            return seg
    return "未知包名"


# =================================================================

def classify_content(content: str) -> str:
    """原有内容分类逻辑，保持不变"""
    keywords_map = {
        "账号密码": ["password", "passwd", "账号", "密码", "token", "auth"],
        "位置信息": ["GPS", "latitude", "longitude", "纬度", "经度", "位置"],
        "通信记录": ["通话", "短信", "聊天", "phone", "sms", "chat"],
        "应用日志": ["log", "日志", "crash", "error"],
        "配置文件": ["config", "设置", "xml", "json", "yml"]
    }
    for category, keywords in keywords_map.items():
        if any(keyword in content for keyword in keywords):
            return category
    return "未分类"


def scan_and_extract(root_dir: str) -> List[dict]:
    """扫描并提取文件内容，修复了批量写入和内存管理问题"""
    global latest_packages, package_to_paths
    latest_packages.clear()  # 清空之前的包名列表
    package_to_paths.clear()  # 清空之前的包名到路径映射

    print(f"开始扫描目录: {root_dir}")
    file_paths = ctypes.POINTER(ctypes.c_char_p)()
    file_count = ctypes.c_int(0)
    lib.scan_files(ctypes.c_char_p(root_dir.encode()), ctypes.byref(file_paths), ctypes.byref(file_count))
    print(f"扫描到 {file_count.value} 个文件")

    results = []
    batch_data = []
    batch_size = 500  # 批量写入大小
    processed_count = 0

    for i in range(file_count.value):
        try:
            file_path = file_paths[i].decode()
            content_len = ctypes.c_int(0)
            content_ptr = lib.extract_content(ctypes.c_char_p(file_path.encode()), ctypes.byref(content_len))

            if content_ptr:
                content = ctypes.string_at(content_ptr, content_len.value).decode(errors="ignore")
                package_name = extract_package_name(file_path)
                category = classify_content(content)

                # 添加到最新包名列表
                if package_name != "未知包名":
                    latest_packages.add(package_name)
                    # 添加包名到文件路径的映射
                    if package_name not in package_to_paths:
                        package_to_paths[package_name] = []
                    package_to_paths[package_name].append(file_path)

                results.append({
                    "file_path": file_path,
                    "package_name": package_name,
                    "content": content,
                    "category": category
                })

                # 尝试写入 Redis（如果连接成功）
                try:
                    r.setex(f"file:{file_path}", 1800, content)
                except:
                    pass  # Redis 失败不影响主流程

                # 添加到批量写入
                batch_data.append((file_path, package_name, content, category))

                # 批量写入数据库
                if len(batch_data) >= batch_size:
                    try:
                        with db_pool.get_connection() as conn:
                            conn.execute('BEGIN TRANSACTION')
                            conn.executemany('''
                            INSERT OR REPLACE INTO file_data (file_path, package_name, content, category)
                            VALUES (?, ?, ?, ?)
                            ''', batch_data)
                            conn.commit()
                            batch_data = []
                            processed_count += len(batch_data)
                            if processed_count % 1000 == 0:
                                print(f"已处理 {processed_count} 个文件...")
                    except Exception as e:
                        print(f"批量写入SQLite失败：{e}")

        except Exception as e:
            print(f"处理文件时出错 {i}: {e}")
            continue

    # 写入剩余的批量数据
    if batch_data:
        try:
            with db_pool.get_connection() as conn:
                conn.execute('BEGIN TRANSACTION')
                conn.executemany('''
                INSERT OR REPLACE INTO file_data (file_path, package_name, content, category)
                VALUES (?, ?, ?, ?)
                ''', batch_data)
                conn.commit()
                print(f"最后批次：写入 {len(batch_data)} 个文件")
        except Exception as e:
            print(f"批量写入SQLite失败：{e}")

    lib.free_files(file_paths, file_count.value)
    print(f"扫描完成！总计处理 {len(results)} 个文件，发现 {len(latest_packages)} 个包名")
    return results


# 请求模型（保持不变）
class ScanRequest(BaseModel):
    root_dir: str


class QueryRequest(BaseModel):
    keyword: str
    source: str = "redis"


# API接口（保持不变）
@app.get("/")
async def root():
    return {"message": "取证比赛高速查询工具 API", "version": "1.0.0"}


@app.get("/packages")
async def get_packages():
    """获取包名列表"""
    global latest_packages
    packages = sorted(list(latest_packages))
    return {"data": packages}


@app.get("/package_paths")
async def get_package_paths(package_name: str):
    """获取指定包名对应的所有文件路径"""
    global package_to_paths

    if package_name not in package_to_paths:
        return {"status": "error", "message": f"未找到包名 '{package_name}' 对应的文件路径"}

    paths = package_to_paths[package_name]
    return {"status": "success", "package_name": package_name, "paths": paths}


@app.post("/scan")
async def api_scan(request: ScanRequest):
    """扫描目录"""
    if not os.path.exists(request.root_dir):
        raise HTTPException(status_code=400, detail="目录不存在")

    print(f"\n{'='*60}")
    print(f"开始扫描: {request.root_dir}")
    print(f"{'='*60}\n")

    try:
        results = scan_and_extract(request.root_dir)
        return {
            "status": "success",
            "count": len(results),
            "package_count": len(latest_packages),
            "message": f"扫描到{len(results)}个文件，发现{len(latest_packages)}个包名"
        }
    except Exception as e:
        print(f"扫描失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"扫描失败: {str(e)}")


@app.post("/query")
async def api_query(request: QueryRequest):
    """关键词查询"""
    start_time = time.time()
    matches = []

    if request.source == "redis":
        try:
            redis_cursor = r.scan_iter(match="file:*", count=1000)
            for key in redis_cursor:
                try:
                    value = r.get(key)
                    if value is None:
                        continue
                    content = value.decode(errors="ignore") if isinstance(value, bytes) else str(value)
                    if request.keyword in content:
                        file_path = key.decode(errors="ignore").replace("file:", "") if isinstance(key, bytes) else str(key).replace("file:", "")
                        matches.append({
                            "file_path": file_path,
                            "content": content[:500],
                            "source": "redis"
                        })
                except Exception as e:
                    print(f"Redis 查询出错: {e}")
                    continue
        except Exception as e:
            print(f"Redis 查询失败: {e}")
    else:
        try:
            with db_pool.get_connection() as conn:
                db_cursor = conn.cursor()
                db_cursor.execute('''
                    SELECT file_path, content, package_name FROM file_data
                    WHERE content LIKE ? LIMIT 100
                    ''', (f"%{request.keyword}%",))
                rows = db_cursor.fetchall()
                for row in rows:
                    matches.append({
                        "file_path": row[0],
                        "content": row[1][:500] if row[1] else "",
                        "package_name": row[2],
                        "source": "sqlite"
                    })
        except Exception as e:
            print(f"SQLite 查询失败: {e}")

    cost = round((time.time() - start_time) * 1000, 2)
    return {"status": "success", "cost_ms": cost, "count": len(matches), "data": matches}


@app.post("/release_memory")
async def api_release_memory():
    """释放 Redis 内存"""
    try:
        keys = r.keys("file:*")
        if keys:
            keys_list = list(keys)
            if keys_list:
                r.delete(*keys_list)
                return {"status": "success", "message": f"已释放 {len(keys_list)} 个缓存"}
    except Exception as e:
        return {"status": "error", "message": f"释放内存失败: {str(e)}"}
    return {"status": "success", "message": "内存已释放"}


@app.post("/clear_data")
async def api_clear_data():
    """清空所有数据"""
    try:
        with db_pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM file_data')
            conn.commit()

        # 清空 Redis
        try:
            keys = r.keys("file:*")
            if keys:
                keys_list = list(keys)
                if keys_list:
                    r.delete(*keys_list)
        except:
            pass

        # 清空内存中的包名列表
        global latest_packages, package_to_paths
        latest_packages.clear()
        package_to_paths.clear()

        return {"status": "success", "message": "数据已清空"}
    except Exception as e:
        return {"status": "error", "message": f"清空数据失败: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
