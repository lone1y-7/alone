# SQLite 数据库 AI 分析工具

使用本地部署的 Ollama + llama2 模型分析 SQLite 数据库，支持智能关联发现和数据取证分析。

## 功能特性

### 核心功能
- **AI 智能分析**：使用本地 Ollama + llama2 模型进行数据分析
- **交互式查询**：自然语言提问数据库相关问题
- **SQL 查询执行**：直接执行 SQL 语句并查看结果
- **数据关联发现**：自动检测表之间的显式和隐式关联
- **JOIN 查询建议**：根据关联关系自动生成 SQL JOIN 语句

### 数据关联分析
- **外键关系检测**：自动识别数据库定义的外键约束
- **隐式关联发现**：基于字段名称和数据内容发现隐式关联
- **数据重叠率计算**：计算字段间的数据交集比例
- **置信度评估**：高/中两个等级评估关联可靠性

### 智能回答模式
- **纯中文回答**：所有解释和分析使用中文
- **保留英文术语**：SQL 关键词、表名、字段名、技术术语保持英文
- **专业分析**：提供数据洞察和改进建议

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
| `relationships` | 分析表之间的关联关系 |
| `suggest-join <表1> [表2]` | 生成 JOIN 查询建议 |
| `quit` | 退出程序 |

## 使用示例

### 基础查询

#### 查看表列表

```
> tables
数据库中的表: customers, sqlite_sequence, products, orders
```

#### 查看表结构

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

#### 执行查询

```
> query SELECT * FROM orders LIMIT 3
查询结果:
  {'id': 1, 'customer_id': 2, 'product_id': 3, 'quantity': 2, 'total_price': 798.0, 'order_date': '2026-01-15 10:30:00', 'status': 'completed'}
  {'id': 2, 'customer_id': 1, 'product_id': 1, 'quantity': 1, 'total_price': 5999.0, 'order_date': '2026-01-18 14:20:00', 'status': 'completed'}
  {'id': 3, 'customer_id': 4, 'product_id': 7, 'quantity': 1, 'total_price': 1599.0, 'order_date': '2026-01-20 09:15:00', 'status': 'completed'}
```

### AI 分析

#### 提问分析

```
> ask 哪个城市的客户订单最多？
```

#### 整体分析

```
> analyze
```

AI 会提供：
1. 数据库整体概况
2. 各表的数据特点
3. 可能的业务场景分析
4. 数据质量评估
5. 改进建议

### 数据关联分析

#### 查看所有表关联

```
> relationships
```

**输出示例：**

```
============================================================
数据库表关系分析 / Database Table Relationships Analysis
============================================================

📊 关系摘要 / Relationship Summary:
  - 显式外键关系 / Explicit Foreign Keys: 2
  - 隐式数据关联 / Implicit Data Relationships: 3

🔗 显式外键关系 / Explicit Foreign Keys:

  orders.product_id -> products.id
    ON UPDATE: NO ACTION, ON DELETE: NO ACTION

  orders.customer_id -> customers.id
    ON UPDATE: NO ACTION, ON DELETE: NO ACTION

🔍 隐式数据关联 / Implicit Data Relationships:

  customers.id <-> products.id
    数据重叠率 / Overlap Ratio: 100.00%
    置信度 / Confidence: high

  products.id <-> orders.id
    数据重叠率 / Overlap Ratio: 100.00%
    置信度 / Confidence: high

============================================================
```

#### 生成 JOIN 查询建议

**示例 1：查询两个表之间的关联**

```
> suggest-join customers orders
```

**输出：**

```
找到 2 个关联建议:

1. 关联 / Relationship: customers.id <-> orders.customer_id
   置信度 / Confidence: high
   查询 / Query:
   SELECT * FROM customers JOIN orders ON customers.id = orders.customer_id

2. 关联 / Relationship: orders.id <-> customers.id
   置信度 / Confidence: high
   查询 / Query:
   SELECT * FROM orders JOIN customers ON orders.id = customers.id
```

**示例 2：查询某个表的所有关联**

```
> suggest-join orders
```

查看 orders 表的所有可能关联关系。

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

## 数据关联发现功能详解

详细的关联分析功能使用说明，请参考：`RELATIONSHIPS_GUIDE.md`

### 检测原理

1. **外键关系**：通过 `PRAGMA foreign_key_list` 命令读取数据库定义的外键约束

2. **隐式关联发现**：基于以下两种线索
   - 字段名称相似性：识别常见命名模式
   - 数据内容重叠率：计算字段间的数据交集比例

### 置信度等级

- **高**：数据重叠率 ≥ 90%
- **中**：数据重叠率 ≥ 70%

### 应用场景

- 数据库文档化
- 复杂查询构建
- 数据质量检查
- 迁移和重构

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
- `RELATIONSHIPS_GUIDE.md` - 数据关联分析使用指南

## 开发计划

未来计划添加的功能：

- [ ] 数据完整性检查
- [ ] 异常模式检测
- [ ] 时间线分析
- [ ] 敏感数据扫描
- [ ] 取证报告生成
- [ ] 数据可视化
- [ ] ER 图生成

## 贡献

欢迎提交 Issue 和 Pull Request！
