# 数据关联发现功能使用指南

## 新增功能

### 1. 外键关系分析
自动检测数据库中定义的外键约束。

### 2. 隐式数据关联发现
基于数据内容和字段名称，发现表之间的隐式关联关系。

### 3. JOIN 查询建议
根据发现的关联关系，自动生成 SQL JOIN 查询语句。

## 使用方法

### 查看所有表关联关系

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

### 生成 JOIN 查询建议

```
> suggest-join <表1> [表2]
```

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

**输出：**

```
找到 3 个关联建议:

1. 关联 / Relationship: orders.product_id <-> products.id
   置信度 / Confidence: high
   查询 / Query:
   SELECT * FROM orders JOIN products ON orders.product_id = products.id

2. 关联 / Relationship: orders.customer_id <-> customers.id
   置信度 / Confidence: high
   查询 / Query:
   SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id
...
```

## 检测原理

### 1. 外键关系
通过 `PRAGMA foreign_key_list` 命令读取数据库定义的外键约束。

### 2. 隐式关联发现
基于以下两种线索：

#### 字段名称相似性
识别常见模式：
- `id` ↔ `user_id`, `customer_id`, `product_id`
- `customer` ↔ `customer_id`, `cust_id`
- `product` ↔ `product_id`, `item_id`
- `order` ↔ `order_id`, `order_number`

#### 数据内容重叠率
计算两个字段的数据重叠率：

```
重叠率 = (交集大小) / (较小集合的大小)
```

- 重叠率 ≥ 90%：高置信度
- 重叠率 ≥ 70%：中等置信度

## 应用场景

### 场景 1：数据库文档化
快速了解数据库结构和表之间的关系。

```
> relationships
```

### 场景 2：复杂查询构建
自动生成 JOIN 查询，避免手动编写复杂的 SQL。

```
> suggest-join orders customers products
```

### 场景 3：数据质量检查
发现定义但未使用的外键，或隐式但未显式定义的关联。

```
> relationships
# 对比显式外键和隐式关联
```

### 场景 4：迁移和重构
在数据库迁移或重构时，确保所有关联关系都被保留。

```
> suggest-join <表名>
# 查看该表的所有关联，确保迁移后正确重建
```

## 示例数据库测试

在 `example.db` 上测试：

```bash
python3 sqlite_analyzer.py
```

运行以下命令：

1. 查看所有表关联：
```
> relationships
```

2. 生成 customers 和 orders 的 JOIN 查询：
```
> suggest-join customers orders
```

3. 验证生成的查询：
```
> query SELECT c.name, o.total_price, o.order_date
     FROM customers c
     JOIN orders o ON c.id = o.customer_id
     LIMIT 5
```

## 注意事项

1. **数据采样**：隐式关联分析使用数据采样（默认 100 条）来计算重叠率，可能不完全准确。
2. **性能**：对于大型数据库，关系分析可能需要一些时间。
3. **建议仅供参考**：自动生成的 JOIN 查询建议需要根据实际业务需求进行调整。
4. **字段类型**：当前只分析 INTEGER 和 TEXT 类型字段的关联。

## 扩展功能

未来可以添加的功能：

1. **N:M 关系检测**：识别多对多关系
2. **层级关系检测**：识别树形结构（如部门、分类）
3. **时序关联**：基于时间戳发现前后事件关系
4. **ER 图生成**：自动生成实体关系图
5. **数据血缘分析**：追踪数据来源和流转路径
