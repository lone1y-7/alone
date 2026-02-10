# 快速配置 API 密钥指南

## 方式 1：命令行参数（最简单）

### 步骤
1. 打开命令行
2. 直接输入以下命令：

```bash
python3 sqlite_analyzer.py --provider doubao --api-key 你的_豆包_api_key
```

### 示例
```bash
python3 sqlite_analyzer.py --provider doubao --api-key sk-dcba9876543210abcdefghijklmnopqrst
```

## 方式 2：环境变量（推荐 Linux/macOS）

### 步骤 1：临时设置（当前会话）

```bash
export DOUBAO_API_KEY=你的_豆包_api_key
python3 sqlite_analyzer.py --provider doubao
```

### 步骤 2：永久设置（推荐）

#### Linux (Ubuntu, CentOS 等)

```bash
# 编辑 ~/.bashrc
echo 'export DOUBAO_API_KEY=你的_豆包_api_key' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc

# 验证
echo $DOUBAO_API_KEY
```

#### macOS

```bash
# 编辑 ~/.zshrc（如果使用 zsh）
echo 'export DOUBAO_API_KEY=你的_豆包_api_key' >> ~/.zshrc

# 重新加载配置
source ~/.zshrc

# 验证
echo $DOUBAO_API_KEY
```

### 使用
```bash
python3 sqlite_analyzer.py --provider doubao
```

## 方式 3：配置文件（最安全）

### 步骤 1：创建配置文件

```bash
# 复制示例配置文件
cp config.ini.example config.ini

# 编辑配置文件
nano config.ini  # 或使用 vim、vscode 等编辑器
```

### 步骤 2：填写配置

打开 `config.ini`，找到 `[doubao]` 部分：

```ini
[doubao]
api_key = 在这里填写你的豆包_api_key
model = doubao-pro-32k
endpoint = https://ark.cn-beijing.volces.com/api/v3
```

将 `在这是里填写你的豆包_api_key` 替换为你的实际 API 密钥。

### 步骤 3：使用配置文件

```bash
python3 sqlite_analyzer.py --provider doubao --config config.ini
```

## Windows 配置

### 方法 1：命令提示符

```cmd
set DOUBAO_API_KEY=你的_豆包_api_key
python3 sqlite_analyzer.py --provider doubao
```

### 方法 2：PowerShell

```powershell
# 临时设置
$env:DOUBAO_API_KEY="你的_豆包_api_key"
python3 sqlite_analyzer.py --provider doubao

# 永久设置（添加到配置文件）
notepad $PROFILE

# 在文件末尾添加：
$env:DOUBAO_API_KEY="你的_豆包_api_key"
```

### 方法 3：配置文件

1. 创建 `config.ini` 文件
2. 填写你的 API 密钥
3. 运行：

```cmd
python3 sqlite_analyzer.py --provider doubao --config config.ini
```

## 验证配置

配置完成后，启动程序验证：

```bash
python3 sqlite_analyzer.py --provider doubao
```

你应该看到类似输出：

```
=== SQLite 数据库 AI 分析工具 ===
数据库: example.db
AI 提供商: 豆包 AI (doubao-pro-32k)

命令:
  analyze - 使用 AI 分析整个数据库
  ask <问题> - 向 AI 提问关于数据库的问题
  tables - 查看所有表
  schema <表名> - 查看表结构
  query <SQL语句> - 执行 SQL 查询
  relationships - 分析表之间的关联关系
  suggest-join <表1> [表2] - 生成 JOIN 查询建议
  quit - 退出
```

## 测试 API 连接

输入以下命令测试：

```
> ask 你好
```

如果豆包 AI 配置正确，你应该会收到回复。

## 获取豆包 API 密钥

1. 访问字节跳动 AI 开放平台：https://console.volcengine.com/ark
2. 注册/登录账号
3. 进入 API 密钥管理页面
4. 创建新的 API 密钥
5. 复制 API 密钥（格式类似：`sk-dcba9876543210...`）

## 推荐配置方式

### 对于个人用户
推荐使用 **配置文件**：
- 安全性好（API 密钥不暴露在命令历史）
- 可以配置多个 AI 提供商
- 易于管理和更新

### 对于开发者
推荐使用 **环境变量**：
- 适合 CI/CD 流水线
- 适合多环境开发
- 不会意外提交到代码仓库

## 常见问题

### Q: API 密钥格式不对？
A: 豆包 API 密钥通常以 `sk-` 开头，请确保复制完整。

### Q: 提示 API 密钥无效？
A: 请检查：
1. API 密钥是否复制完整
2. API 密钥是否过期
3. 是否使用了正确的 API 密钥（豆包 vs 其他服务）

### Q: 不想每次都输入密钥？
A: 使用环境变量或配置文件，这是推荐方式。

### Q: 如何保护 API 密钥？
A: 建议：
1. 不要在命令历史中直接输入 API 密钥
2. 使用环境变量或配置文件
3. 将 config.ini 添加到 .gitignore
4. 不要将 API 密钥提交到代码仓库

## 配置示例

### 示例 1：使用默认配置

```bash
python3 sqlite_analyzer.py
```
默认使用本地 Ollama (llama2)

### 示例 2：使用豆包，命令行参数

```bash
python3 sqlite_analyzer.py --provider doubao --api-key sk-xxxxxxxxxx
```

### 示例 3：使用豆包，环境变量

```bash
export DOUBAO_API_KEY=sk-xxxxxxxxxx
python3 sqlite_analyzer.py --provider doubao
```

### 示例 4：使用豆包，配置文件

```bash
# 先配置 config.ini
# 然后运行
python3 sqlite_analyzer.py --provider doubao --config config.ini
```

### 示例 5：指定不同模型

```bash
# 使用 doubao-pro-4k（更快，成本更低）
python3 sqlite_analyzer.py --provider doubao --api-key sk-xx --model doubao-pro-4k

# 使用 doubao-lite-4k（最低成本）
python3 sqlite_analyzer.py --provider doubao --api-key sk-xx --model doubao-lite-4k
```

## 安全提醒

⚠️ **重要**：
- 不要将包含 API 密钥的配置文件提交到 Git
- 建议将 `config.ini` 添加到 `.gitignore`
- 不要在公共场合分享 API 密钥
- 定期更换 API 密钥
- 监控 API 使用情况，发现异常及时处理

## 下一步

配置完成后，你可以：
- 使用 `analyze` 命令分析整个数据库
- 使用 `ask <问题>` 提问具体问题
- 使用 `relationships` 分析表关联关系
- 参考详细文档：`DOUBAO_GUIDE.md`
