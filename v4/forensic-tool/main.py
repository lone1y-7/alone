import ctypes
import os
import sqlite3
import time
from typing import List
import fakeredis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 初始化Redis（模拟）
r = fakeredis.FakeRedis(decode_responses=False)
try:
    r.config_set("maxmemory", "10GB")
    r.config_set("maxmemory-policy", "volatile-lru")
except Exception:
    pass

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
conn = sqlite3.connect("forensic.db", check_same_thread=False)
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
conn.commit()

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
    """原有扫描逻辑，保持不变"""
    file_paths = ctypes.POINTER(ctypes.c_char_p)()
    file_count = ctypes.c_int(0)
    lib.scan_files(ctypes.c_char_p(root_dir.encode()), ctypes.byref(file_paths), ctypes.byref(file_count))
    results = []
    batch_data = []

    for i in range(file_count.value):
        file_path = file_paths[i].decode()
        content_len = ctypes.c_int(0)
        content_ptr = lib.extract_content(ctypes.c_char_p(file_path.encode()), ctypes.byref(content_len))
        if content_ptr:
            content = ctypes.string_at(content_ptr, content_len.value).decode(errors="ignore")
            package_name = extract_package_name(file_path)  # 调用修改后的包名提取函数
            category = classify_content(content)
            results.append({
                "file_path": file_path,
                "package_name": package_name,
                "content": content,
                "category": category
            })
            r.setex(f"file:{file_path}", 1800, content)
            batch_data.append((file_path, package_name, content, category))

            if len(batch_data) >= 100:
                try:
                    cursor.executemany('''
                    INSERT OR REPLACE INTO file_data (file_path, package_name, content, category)
                    VALUES (?, ?, ?, ?)
                    ''', batch_data)
                    conn.commit()
                    batch_data = []
                except Exception as e:
                    print(f"批量写入SQLite失败：{e}")
    if batch_data:
        try:
            cursor.executemany('''
            INSERT OR REPLACE INTO file_data (file_path, package_name, content, category)
            VALUES (?, ?, ?, ?)
            ''', batch_data)
            conn.commit()
        except Exception as e:
            print(f"批量写入SQLite失败：{e}")
    lib.free_files(file_paths, file_count.value)
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
    cursor.execute('SELECT DISTINCT package_name FROM file_data WHERE package_name != "未知包名"')
    packages = [row[0] for row in cursor.fetchall()]
    return {"data": packages}


@app.post("/scan")
async def api_scan(request: ScanRequest):
    if not os.path.exists(request.root_dir):
        raise HTTPException(status_code=400, detail="目录不存在")
    results = scan_and_extract(request.root_dir)
    return {"status": "success", "count": len(results), "message": f"扫描到{len(results)}个文件"}


@app.post("/query")
async def api_query(request: QueryRequest):
    start_time = time.time()
    if request.source == "redis":
        redis_cursor = r.scan_iter(match="file:*", count=1000)
        matches = []
        for key in redis_cursor:
            value = r.get(key)
            if value is None:
                continue
            content = value.decode(errors="ignore") if isinstance(value, bytes) else str(value)
            if request.keyword in content:
                file_path = key.decode(errors="ignore").replace("file:", "") if isinstance(key, bytes) else str(
                    key).replace("file:", "")
                matches.append({
                    "file_path": file_path,
                    "content": content[:500],
                    "source": "redis"
                })
    else:
        try:
            db_cursor = conn.cursor()
            db_cursor.execute('''
            SELECT file_path, content, package_name FROM file_data
            WHERE content LIKE ? LIMIT 100
            ''', (f"%{request.keyword}%",))
            matches = [{"file_path": row[0], "content": row[1][:500], "package_name": row[2], "source": "sqlite"} for
                       row in db_cursor.fetchall()]
        except Exception:
            matches = []
    cost = round((time.time() - start_time) * 1000, 2)
    return {"status": "success", "cost_ms": cost, "count": len(matches), "data": matches}


@app.post("/release_memory")
async def api_release_memory():
    try:
        keys = r.keys("file:*")
        if keys:
            r.delete(*keys)
    except Exception:
        pass
    return {"status": "success", "message": "内存已释放"}


@app.post("/clear_data")
async def api_clear_data():
    try:
        cursor.execute('DELETE FROM file_data')
        conn.commit()
        keys = r.keys("file:*")
        if keys:
            r.delete(*keys)
        return {"status": "success", "message": "数据已清空"}
    except Exception as e:
        return {"status": "error", "message": f"清空数据失败：{str(e)}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)