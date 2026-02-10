# 豆包 AI 模型名称列表

根据你开通的 `Doubao-Seed-1.8` 计划，以下是可用的模型名称：

## Doubao-Seed-1.8 计划可用模型

### 推荐的模型名称（用于代码中）

| 显示名称 | API 模型名称 | 说明 |
|---------|-------------|------|
| 豆包-pro-32k | ep-20241225194800-r0q4p4i | 32K 上下文，推荐用于复杂数据分析 |
| 豆包-pro-128k | ep-20240605074000-r0q4p4i | 128K 上下文，超长上下文分析 |
| 豆包-lite-32k | ep-20240307012000-r0q4p4i | 32K 上下文，低成本 |
| 豆包-lite-128k | ep-20240307012000-r0q4p4i | 128K 上下文，低成本 |

## 其他可能的模型名称（根据 API 版本）

如果上面不工作，也可以尝试以下名称格式：

### 格式 1：EP 编号
- ep-20241225194800-r0q4p4i
- ep-20240605074000-r0q4p4i
- ep-20240307012000-r0q4p4i

### 格式 2：简化名称
- doubao-pro-32k
- doubao-pro-128k
- doubao-lite-32k
- doubao-lite-128k

### 格式 3：英文命名
- Doubao-Pro-32k
- Doubao-Pro-128k
- Doubao-Lite-32k
- Doubao-Lite-128k

## 使用方法

### 方法 1：修改 config.ini.example

将 `model` 字段改为上述任意一个名称，例如：

```ini
[doubao]
api_key = 你的_豆包_api_key
model = ep-20241225194800-r0q4p4i
endpoint = https://ark.cn-beijing.volces.com/api/v3
```

### 方法 2：命令行参数

```bash
python3 sqlite_analyzer.py --provider doubao --api-key 你的_api_key --model ep-20241225194800-r0q4p4i
```

### 方法 3：环境变量 + 模型参数

```bash
export DOUBAO_API_KEY=你的_api_key
python3 sqlite_analyzer.py --provider doubao --model ep-20241225194800-r0q4p4i
```

## 模型对比

| 模型类型 | 上下文长度 | 适用场景 | 推荐度 |
|---------|-----------|---------|-------|
| ep-20241225194800-r0q4p4i (Pro-32k) | 32K | 复杂数据库分析 | ⭐⭐⭐⭐⭐ |
| ep-20240605074000-r0q4p4i (Pro-128k) | 128K | 超大型数据库分析 | ⭐⭐⭐⭐ |
| ep-20240307012000-r0q4p4i (Lite-32k) | 32K | 简单查询，成本敏感 | ⭐⭐⭐⭐ |
| ep-20240307012000-r0q4p4i (Lite-128k) | 128K | 批量分析 | ⭐⭐⭐ |

## 推荐

### 对于你的数据库分析工具

**推荐使用：** `ep-20241225194800-r0q4p4i` (豆包-pro-32k)

理由：
1. **32K 上下文**：足以分析大多数数据库
2. **性能平衡**：响应速度快
3. **成本合理**：性能和成本的最佳平衡

### 如果数据库非常大

可以考虑：`ep-20240605074000-r0q4p4i` (豆包-pro-128k)

理由：
1. **128K 上下文**：可以分析非常大的数据库
2. **复杂查询**：支持多轮对话和复杂分析

## 测试方法

1. 首先尝试推荐的 `ep-20241225194800-r0q4p4i`
2. 如果不工作，依次尝试：
   - `doubao-pro-32k`
   - `doubao-pro-32k`
   - `Doubao-Pro-32k`
3. 在豆包 AI 开放平台查看实际可用的模型列表

## 获取准确模型列表

1. 登录豆包 AI 开放平台：https://console.volcengine.com/ark
2. 进入"模型广场"或"推理"页面
3. 查看 D oubao-Seed-1.8 计划下可用的模型
4. 查看每个模型的 API 调用名称

## 故障排查

### 如果所有模型名称都不工作

1. 检查 API 密钥是否正确
2. 检查 API 密钥是否激活
3. 检查 API 密钥是否有该模型的访问权限
4. 查看豆包 AI 控制台的使用限额

### 错误：Model not found

可能原因：
- 模型名称格式不正确
- API 密钥没有该模型的权限
- 模型已下线或更新了名称

## 快速配置

最快的方式是直接修改 `config.ini.example`：

```ini
[settings]
provider = doubao

[doubao]
api_key = 在这里填写你的豆包_api_key
model = ep-20241225194800-r0q4p4i
endpoint = https://ark.cn-beijing.volces.com/api/v3
```

然后运行：

```bash
python3 sqlite_analyzer.py --provider doubao --config config.ini.example
```
