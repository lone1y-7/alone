import ctypes
import os
import sqlite3
import time
from typing import List

import fakeredis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

r = fakeredis.FakeRedis(decode_responses=False)

try:
    r.config_set("maxmemory", "10GB")
    r.config_set("maxmemory-policy", "volatile-lru")
except Exception:
    pass

if os.name == "posix":
    lib = ctypes.CDLL("./build/libscanner.so")
elif os.name == "nt":
    lib = ctypes.CDLL("./build/scanner.dll")
else:
    raise Exception("不支持的系统")

lib.scan_files.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)), ctypes.POINTER(ctypes.c_int)]
lib.scan_files.restype = None

lib.extract_content.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
lib.extract_content.restype = ctypes.c_char_p

lib.free_files.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int]
lib.free_files.restype = None

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

app = FastAPI(title="取证比赛高速查询工具")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def scan_and_extract(root_dir: str) -> List[dict]:
    file_paths = ctypes.POINTER(ctypes.c_char_p)()
    file_count = ctypes.c_int(0)

    lib.scan_files(ctypes.c_char_p(root_dir.encode()), ctypes.byref(file_paths), ctypes.byref(file_count))

    results = []
    for i in range(file_count.value):
        file_path = file_paths[i].decode()
        content_len = ctypes.c_int(0)
        content_ptr = lib.extract_content(ctypes.c_char_p(file_path.encode()), ctypes.byref(content_len))

        if content_ptr:
            content = ctypes.string_at(content_ptr, content_len.value).decode(errors="ignore")
            package_name = extract_package_name(file_path)
            category = classify_content(content)

            results.append({
                "file_path": file_path,
                "package_name": package_name,
                "content": content,
                "category": category
            })

            r.setex(f"file:{file_path}", 1800, content)

            try:
                cursor.execute('''
                INSERT OR REPLACE INTO file_data (file_path, package_name, content, category)
                VALUES (?, ?, ?, ?)
                ''', (file_path, package_name, content, category))
                conn.commit()
            except Exception as e:
                print(f"写入SQLite失败：{e}")

            libc = ctypes.CDLL("libc.so.6" if os.name == "posix" else "msvcrt.dll")
            libc.free(content_ptr)

    lib.free_files(file_paths, file_count.value)
    return results

def extract_package_name(file_path: str) -> str:
    android_pattern = "/data/data/"
    if android_pattern in file_path:
        start = file_path.index(android_pattern) + len(android_pattern)
        end = file_path.index("/", start) if "/" in file_path[start:] else len(file_path)
        return file_path[start:end]

    ios_pattern = "/var/mobile/Containers/Bundle/Application/"
    if ios_pattern in file_path:
        parts = file_path.split(ios_pattern)[-1].split("/")
        if len(parts) >= 3:
            return parts[2].replace(".app", "")

    return "未知包名"

def classify_content(content: str) -> str:
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

class ScanRequest(BaseModel):
    root_dir: str

class QueryRequest(BaseModel):
    keyword: str
    source: str = "redis"

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
        keys = r.keys("file:*")
        matches = []
        for key in keys:
            key_str = key if isinstance(key, str) else key.decode()
            value = r.get(key_str)
            if value is None:
                continue
            content = value.decode(errors="ignore") if isinstance(value, bytes) else str(value)
            if request.keyword in content:
                file_path = key_str.replace("file:", "")
                matches.append({
                    "file_path": file_path,
                    "content": content[:500],
                    "source": "redis"
                })
    else:
        cursor.execute('''
        SELECT file_path, content FROM file_data WHERE content LIKE ?
        ''', (f"%{request.keyword}%",))
        matches = [{"file_path": row[0], "content": row[1][:500], "source": "sqlite"} for row in cursor.fetchall()]

    cost = round((time.time() - start_time) * 1000, 2)
    return {"status": "success", "cost_ms": cost, "count": len(matches), "data": matches}

@app.post("/release_memory")
async def api_release_memory():
    try:
        r.memory_purge()
        keys = r.keys("file:*")
        if keys:
            r.delete(*keys)
    except Exception:
        pass
    return {"status": "success", "message": "内存已释放"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
