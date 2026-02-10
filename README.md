# SQLite 数据库 AI 分析工具

使用本地部署的 Ollama + llama2 模型分析 SQLite 数据库。

## 安装

### 1. 安装 Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. 启动 Ollama 服务

```bash
nohup ollama serve > /tmp/ollama.log 2>&1 &
```

### 3. 下载 llama2 模型

```bash
ollama pull llama2
```

注意：首次下载需要约 3.8GB 空间，可能需要较长时间。

## 使用

### 方法一：使用启动脚本

```bash
./start_services.sh
python3 sqlite_analyzer.py
```

### 方法二：手动启动

```bash
# 启动 Ollama
ollama serve &

# 运行分析程序
python3 sqlite_analyzer.py
```

### 测试环境

```bash
python3 test.py
```

## 交互式命令

进入程序后，可以使用以下命令：

| 命令 | 说明 |
|------|------|
| `analyze` | 使用 AI 分析整个数据库 |
| `ask <问题>` | 向 AI 提问关于数据库的问题 |
| `tables` | 查看所有表 |
| `schema <表名>` | 查看表结构 |
| `query <SQL语句>` | 执行 SQL 查询 |
| `quit` | 退出程序 |

## 示例

### 查看表列表

```
> tables
数据库中的表: customers, sqlite_sequence, products, orders
```

### 查看表结构

```
> schema customers
表 customers 的结构:
  id: INTEGER
  name: TEXT
  email: TEXT
  age: INTEGER
  city: TEXT
  created_at: TIMESTAMP
```

### 执行查询

```
> query SELECT * FROM orders LIMIT 3
查询结果:
  {'id': 1, 'customer_id': 2, 'project_id': 3, 'quantity': 2, 'total_price': 798.0, 'order_date': '2026-01-15 10:30:00', 'status': 'completed'}
  {'id': 2, 'customer_id': 1, 'project_id': 1, 'quantity': 1, 'total_price': 5999.0, 'order_date': '2026-01-18 14:20:00', 'status': 'completed'}
  {'id': 3, 'customer_id': 4, 'project_id': 7, 'quantity': 1, 'total_price': 1599.0, 'order_date': '2026-01-20 09:15:00', 'status': 'completed'}
```

### AI 分析

```
> ask 哪个城市的客户订单最多？
```

```
> analyze
```

## 示例数据库

程序包含一个示例数据库 `example.db`，包含以下表：

- **customers**: 客户信息（5 条记录）
- **products**: 产品信息（10 条记录）
- **orders**: 订单记录（100 条记录）

## 自定义数据库

要分析你自己的 SQLite 数据库：

1. 将数据库文件放到工作目录
2. 修改 `sqlite_analyzer.py` 中的数据库路径：

```python
analyzer = SQLiteAnalyzer('你的数据库.db', 'http://localhost:11434')
```

3. 运行程序

## 故障排查

### Ollama 服务未运行

```bash
ps aux | grep ollama
```

如果未运行，重新启动：

```bash
ollama serve &
```

### 模型未下载

```bash
ollama list
```

如果 llama2 不在列表中，下载它：

```bash
ollama pull llama2
```

### 查看 Ollama 日志

```bash
tail -f /tmp/ollama.log
```

## 系统要求

- Python 3.7+
- Ollama 0.10+
- 至少 4GB 内存（用于运行 llama2 模型）
- 至少 8GB 可用磁盘空间（用于存储模型）

## 文件说明

- `create_db.py` - 创建示例数据库
- `example.db` - 示例 SQLite 数据库
- `sqlite_analyzer.py` - 主分析程序
- `test.py` - 测试程序
- `start_services.sh` - 启动服务脚本
- `README.md` - 本文档
