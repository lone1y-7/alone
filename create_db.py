import sqlite3
from datetime import datetime, timedelta
import random

def create_sample_database():
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            description TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed',
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    conn.commit()

    if not cursor.execute('SELECT COUNT(*) FROM customers').fetchone()[0]:
        customers = [
            ('张三', 'zhangsan@example.com', 28, '北京'),
            ('李四', 'lisi@example.com', 35, '上海'),
            ('王五', 'wangwu@example.com', 42, '广州'),
            ('赵六', 'zhaoliu@example.com', 31, '深圳'),
            ('钱七', 'qianqi@example.com', 26, '杭州')
        ]
        cursor.executemany('INSERT INTO customers (name, email, age, city) VALUES (?, ?, ?, ?)', customers)

    if not cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]:
        products = [
            ('笔记本电脑', '电子产品', 5999.00, 50, '高性能商务笔记本电脑'),
            ('无线鼠标', '电子产品', 99.00, 200, '人体工学设计无线鼠标'),
            ('机械键盘', '电子产品', 399.00, 80, '青轴机械键盘，手感舒适'),
            ('办公桌', '办公用品', 1299.00, 30, '简约现代风格办公桌'),
            ('台灯', '办公用品', 199.00, 150, 'LED护眼台灯，可调亮度'),
            ('咖啡机', '家电', 899.00, 40, '全自动意式咖啡机'),
            ('空气净化器', '家电', 1599.00, 25, '高效去除PM2.5'),
            ('运动鞋', '服装', 299.00, 100, '轻便透气跑步鞋'),
            ('T恤', '服装', 79.00, 300, '纯棉舒适T恤'),
            ('背包', '配件', 199.00, 120, '多功能商务背包')
        ]
        cursor.executemany('INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)', products)

    if not cursor.execute('SELECT COUNT(*) FROM orders').fetchone()[0]:
        customers = cursor.execute('SELECT id FROM customers').fetchall()
        products = cursor.execute('SELECT id, price FROM products').fetchall()

        for _ in range(100):
            customer_id = random.choice(customers)[0]
            product_id, price = random.choice(products)
            quantity = random.randint(1, 5)
            total_price = price * quantity

            days_ago = random.randint(0, 30)
            order_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                INSERT INTO orders (customer_id, product_id, quantity, total_price, order_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (customer_id, product_id, quantity, total_price, order_date, 'completed'))

    conn.commit()
    conn.close()
    print('数据库创建完成！包含以下表：customers, products, orders')

if __name__ == '__main__':
    create_sample_database()
