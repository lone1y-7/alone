# 取证比赛高速查询工具

## 项目概述

这是一个专为取证比赛设计的高性能数据库工具，核心特点：

- **极致查询速度**：Python框架 + C语言核心 + Redis内存缓存
- **防内存溢出**：Redis内存淘汰策略 + 过期时间控制
- **完整功能**：文件扫描、数据提取、包名检索、分类解析
- **API化接口**：FastAPI提供高性能RESTful API
- **可视化界面**：tkinter图形界面展示包名和查询结果

## 技术架构

```
┌─────────────────────────────────────────┐
│         用户界面（tkinter）              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         FastAPI 接口层                  │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼────┐   ┌───▼────┐   ┌───▼────┐
│ Redis  │   │ SQLite │   │  C核心 │
│ 内存库  │   │ 本地库 │   │ 扫描器  │
└────────┘   └────────┘   └────────┘
```

## 目录结构

```
forensic-tool/
├── src/
│   └── file_scanner.c      # C语言核心扫描模块
├── include/
│   └── file_scanner.h      # C语言头文件
├── build/
│   └── libscanner.so       # 编译后的动态链接库
├── main.py                 # FastAPI主程序
├── ui.py                   # tkinter可视化界面
├── requirements.txt        # Python依赖
├── build.sh                # 编译脚本
└── README.md               # 项目说明
```

## 安装步骤

### 1. 编译C模块

```bash
cd forensic-tool
chmod +x build.sh
./build.sh
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 3. 启动Redis服务

```bash
redis-server
```

## 使用方法

### 启动API服务

```bash
python main.py
```

服务将在 http://localhost:8000 启动

### 启动可视化界面

```bash
python ui.py
```

## API接口

### 1. 扫描目录
```
POST /scan
{
  "root_dir": "/path/to/scan"
}
```

### 2. 关键词查询
```
POST /query
{
  "keyword": "搜索关键词",
  "source": "redis"
}
```

### 3. 获取包名列表
```
GET /packages
```

### 4. 释放内存
```
POST /release_memory
```

## 性能优化

- C语言核心模块实现高速文件扫描
- Redis内存缓存提供毫秒级查询
- SQLite本地存储保证数据持久化
- FastAPI异步处理提升并发性能

## 防内存溢出机制

- Redis设置maxmemory为10GB
- 使用volatile-lru淘汰策略
- 文件缓存设置30分钟过期时间
- C模块严格管理内存分配和释放

## 扩展支持

- 支持Android包名提取（/data/data/路径）
- 支持iOS应用识别（.app目录）
- 自动分类：账号密码、位置信息、通信记录等
- 可扩展MCP架构
