# 豆包 AI 集成指南

## 快速开始

### 1. 获取豆包 AI API 密钥

1. 访问 [字节跳动 AI 开放平台](https://console.volcengine.com/ark)
2. 注册/登录账号
3. 创建 API Key

### 2. 配置 API 密钥

#### 方法一：命令行参数

```bash
python3 sqlite_analyzer.py \
    --provider doubao \
    --api-key your_api_key_here
```

#### 方法二：环境变量

```bash
export DOUBAO_API_KEY=your_api_key_here
python3 sqlite_analyzer.py --provider doubao
```

#### 方法三：配置文件

1. 复制配置示例：
```bash
cp config.example config.ini
```

2. 编辑 `config.ini`，填写你的 API 密钥

3. 使用配置文件：
```bash
python3 sqlite_analyzer.py --provider doubao --config config.ini
```

## 豆包 AI 模型说明

### 推荐模型

| 模型 | 上下文长度 | 适用场景 |
|------|-----------|---------|
| `doubao-pro-32k` | 32K tokens | 复杂数据库分析，需要长上下文 |
| `doubao-pro-4k` | 4K tokens | 简单查询，快速响应 |
| `doubao-lite-4k` | 4K tokens | 成本敏感场景 |

### 选择建议

- **大数据库分析**：使用 `doubao-pro-32k`
- **快速查询**：使用 `doubao-pro-4k`
- **批量分析**：使用 `doubao-lite-4k`

## 使用示例

### 基础使用

```bash
# 使用默认模型（doubao-pro-32k）
python3 sqlite_analyzer.py \
    --provider doubao \
    --api-key your_api_key_here

# 指定模型
python3 sqlite_analyzer.py \
    --provider doubao \
    --api-key your_api_key_here \
    --model doubao-pro-4k
```

### 交互式命令

```bash
# 启动后
> analyze
使用豆包 AI 分析数据库...

> ask 哪个产品的销售额最高？
豆包 AI 会分析数据并回答...
```

## 高级配置

### 自定义 API 端点

如果需要使用自定义 API 端点：

```bash
python3 sqlite_analyzer.py \
    --provider doubao \
    --api-key your_api_key_here \
    --endpoint https://your-custom-endpoint.com/api/v3
```

### 模型参数调优

在代码中可以调整以下参数：

```python
data = {
    'model': self.doubao_model,
    'messages': messages,
    'temperature': 0.7,      # 温度参数，0-1，越高越随机
    'max_tokens': 4096,      # 最大生成长度
    'top_p': 0.9             # 核采样参数
}
```

## 成本估算

### 豆包 AI 定价（参考）

| 模型 | 价格（每千 tokens） | 说明 |
|------|------------------|------|
| doubao-pro-32k | ¥0.0008 | 高性能模型 |
| doubao-pro-4k | ¥0.0004 | 快速响应 |
| doubao-lite-4k | ¥0.0001 | 成本优化 |

### 示例计算

假设分析一个包含 3 个表的数据库：
- 输入：约 2000 tokens
- 输出：约 1500 tokens

**doubao-pro-32k**:
- 总计：3500 tokens
- 成本：3500 / 1000 × ¥0.0008 = ¥0.0028

**doubao-lite-4k**:
- 总计：3500 tokens
- 成本：3500 / 1000 × ¥0.0001 = ¥0.00035

## 故障排查

### API 密钥错误

```
错误: 调用豆包 AI 失败: 401 - {"error":"Invalid API key"}
```

**解决方案**：
- 检查 API 密钥是否正确
- 确认 API 密钥未过期

### 网络连接错误

```
错误: 调用豆包 AI 失败: ConnectionError
```

**解决方案**：
- 检查网络连接
- 确认可以访问外网
- 检查防火墙设置

### 模型不支持

```
错误: 调用豆包 AI 失败: 400 - {"error":"Model not found"}
```

**解决方案**：
- 确认模型名称正确
- 查看支持的模型列表

## 对比：豆包 AI vs Ollama

| 特性 | 豆包 AI | Ollama (llama2) |
|------|---------|-----------------|
| **响应速度** | 快（网络） | 中（本地推理） |
| **分析能力** | 强 | 中 |
| **上下文长度** | 32K tokens | 4K tokens |
| **成本** | 按使用付费 | 免费 |
| **隐私** | 数据上传 | 数据本地 |
| **网络依赖** | 需要 | 不需要 |

## 使用建议

### 使用豆包 AI 当：
- ✅ 需要强大的分析能力
- ✅ 分析复杂的大型数据库
- ✅ 需要快速响应
- ✅ 数据不敏感
- ✅ 偶尔使用

### 使用本地 Ollama 当：
- ✅ 数据包含敏感信息
- ✅ 需要长期频繁使用
- ✅ 网络不稳定
- ✅ 成本敏感
- ✅ 需要完全离线

## API 限制

### 配额限制

- 每分钟请求数：60
- 每天请求数：10000
- 并发请求数：5

### 如果超出限制

```
错误: 调用豆包 AI 失败: 429 - {"error":"Rate limit exceeded"}
```

**解决方案**：
- 等待一段时间后重试
- 考虑升级账户等级
- 使用本地 Ollama 作为备选

## 最佳实践

### 1. API 密钥安全

```bash
# 不要在命令行中直接写 API 密钥
# ❌ 错误做法
python3 sqlite_analyzer.py --api-key sk-xxxxxxxxx

# ✅ 正确做法：使用环境变量
export DOUBAO_API_KEY=sk-xxxxxxxxx
python3 sqlite_analyzer.py --provider doubao
```

### 2. 成本优化

- 使用 `doubao-lite-4k` 进行批量分析
- 合理设置 `max_tokens` 限制
- 缓存常用查询结果

### 3. 提示词优化

- 精简描述，只包含必要信息
- 使用明确的提问方式
- 分步骤进行复杂分析

## 更新日志

### v2.0.0 (2026-02-10)
- ✅ 新增豆包 AI 支持
- ✅ 支持命令行参数配置
- ✅ 支持环境变量配置
- ✅ 支持配置文件
- ✅ 新增成本估算
- ✅ 新增 API 限制说明

## 反馈与支持

如有问题或建议，请通过以下方式反馈：
- GitHub Issues
- 文档更新

## 相关文档

- [README.md](README.md) - 主文档
- [RELATIONSHIPS_GUIDE.md](RELATIONSHIPS_GUIDE.md) - 数据关联分析指南
