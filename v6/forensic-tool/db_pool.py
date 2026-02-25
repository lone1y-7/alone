import sqlite3
from contextlib import contextmanager
from threading import Lock
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabasePool:
    """
    SQLite 连接池

    功能:
    - 管理多个数据库连接
    - 自动处理连接的获取和释放
    - 应用性能优化配置
    - 线程安全
    """

    def __init__(self, db_path: str, pool_size: int = 10):
        """
        初始化数据库连接池

        Args:
            db_path: 数据库文件路径
            pool_size: 连接池大小
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.connections = []
        self.lock = Lock()
        self._init_pool()

    def _init_pool(self):
        """初始化连接池"""
        logger.info(f"初始化数据库连接池 (大小: {self.pool_size})...")

        for i in range(self.pool_size):
            try:
                conn = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    isolation_level=None,  # 自动提交模式
                    timeout=30
                )

                # 应用性能优化配置
                self._apply_optimizations(conn)

                self.connections.append(conn)
                logger.info(f"✓ 连接 {i+1}/{self.pool_size} 已创建")

            except Exception as e:
                logger.error(f"✗ 创建连接 {i+1} 失败: {e}")
                raise

        logger.info(f"✓ 数据库连接池初始化完成 ({len(self.connections)} 个连接)")

    def _apply_optimizations(self, conn: sqlite3.Connection):
        """
        应用 SQLite 性能优化配置

        Args:
            conn: 数据库连接
        """
        optimizations = [
            ('journal_mode', 'WAL'),           # WAL 模式，提高并发
            ('synchronous', 'NORMAL'),          # 降低同步级别
            ('cache_size', '-64000'),           # 64MB 缓存
            ('temp_store', 'MEMORY'),          # 临时表在内存
            ('mmap_size', '268435456'),        # 256MB 内存映射
            ('page_size', '4096'),             # 页面大小
            ('locking_mode', 'NORMAL'),         # 锁定模式
            ('busy_timeout', '30000'),          # 忙等待超时 30 秒
        ]

        for key, value in optimizations:
            try:
                conn.execute(f'PRAGMA {key}={value}')
                logger.debug(f"✓ PRAGMA {key}={value}")
            except Exception as e:
                logger.warning(f"✗ PRAGMA {key}={value} 失败: {e}")

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接（上下文管理器）

        使用示例:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM file_data')
                results = cursor.fetchall()

        Yields:
            sqlite3.Connection: 数据库连接
        """
        with self.lock:
            conn = self.connections.pop()
            logger.debug(f"获取连接 (剩余: {len(self.connections)})")

        try:
            yield conn
        finally:
            with self.lock:
                self.connections.append(conn)
                logger.debug(f"释放连接 (剩余: {len(self.connections)})")

    def execute(self, sql: str, params: tuple = None):
        """
        执行 SQL 语句（简化版）

        Args:
            sql: SQL 语句
            params: 参数

        Returns:
            执行结果
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor

    def executemany(self, sql: str, params_list: list):
        """
        批量执行 SQL 语句

        Args:
            sql: SQL 语句
            params_list: 参数列表

        Returns:
            执行结果
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(sql, params_list)
            return cursor

    def fetchall(self, sql: str, params: tuple = None) -> list:
        """
        查询所有结果

        Args:
            sql: SQL 语句
            params: 参数

        Returns:
            查询结果列表
        """
        cursor = self.execute(sql, params)
        return cursor.fetchall()

    def fetchone(self, sql: str, params: tuple = None) -> tuple:
        """
        查询单个结果

        Args:
            sql: SQL 语句
            params: 参数

        Returns:
            查询结果（单行）
        """
        cursor = self.execute(sql, params)
        return cursor.fetchone()

    def get_connection_count(self) -> int:
        """获取当前可用连接数"""
        return len(self.connections)

    def close_all(self):
        """关闭所有连接"""
        logger.info("关闭所有数据库连接...")
        with self.lock:
            for i, conn in enumerate(self.connections):
                try:
                    conn.close()
                    logger.info(f"✓ 连接 {i+1} 已关闭")
                except Exception as e:
                    logger.error(f"✗ 关闭连接 {i+1} 失败: {e}")
            self.connections.clear()
        logger.info("✓ 所有数据库连接已关闭")

    def __del__(self):
        """析构函数，确保连接被关闭"""
        if self.connections:
            self.close_all()

    def __enter__(self):
        """支持上下文管理器协议"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        self.close_all()
        return False


# 使用示例
if __name__ == "__main__":
    import os

    # 创建测试数据库
    test_db = "test_pool.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    # 初始化连接池
    db_pool = DatabasePool(test_db, pool_size=5)

    # 创建测试表
    with db_pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE test (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value INTEGER
        )
        ''')

    # 批量插入测试数据
    test_data = [(i, f"name_{i}", i * 10) for i in range(100)]
    db_pool.executemany('INSERT INTO test (id, name, value) VALUES (?, ?, ?)', test_data)

    # 查询测试
    results = db_pool.fetchall('SELECT * FROM test WHERE value > 500')
    print(f"查询结果: {len(results)} 条记录")

    # 测试并发查询
    import threading
    import time

    def query_thread(thread_id):
        """测试线程"""
        start = time.time()
        results = db_pool.fetchall('SELECT * FROM test')
        elapsed = (time.time() - start) * 1000
        print(f"线程 {thread_id}: 查询 {len(results)} 条记录, 耗时 {elapsed:.2f} ms")

    # 创建多个线程测试并发
    threads = []
    for i in range(10):
        t = threading.Thread(target=query_thread, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # 清理
    db_pool.close_all()
    os.remove(test_db)

    print("\n✓ 连接池测试完成")
