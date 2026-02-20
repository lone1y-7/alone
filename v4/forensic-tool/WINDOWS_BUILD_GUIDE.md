# Windows 编译和运行指南

## 环境要求

### 必需软件
- Windows 10 或更高版本
- Visual Studio 2019 或 2022（包含 C++ 开发工具）
- Python 3.8 或更高版本

### 可选软件
- Git（用于版本控制）

---

## 文件说明

### 核心文件
- `src/file_scanner.c` - C 语言源代码（支持 Windows 和 Linux）
- `include/dirent.h` - Windows 兼容的 dirent 头文件
- `build.bat` - Windows 编译脚本
- `main.py` - Python FastAPI 后端服务
- `ui.py` - tkinter 图形界面

### 编译输出
- `build/scanner.dll` - Windows 动态链接库（编译后生成）
- `build/scanner.lib` - Windows 导入库（编译后生成）
- `src/file_scanner.obj` - 目标文件（编译后生成）

---

## 编译步骤

### 步骤 1: 打开 VS x64 命令提示符

1. 点击 Windows "开始" 菜单
2. 搜索 "x64 Native Tools Command Prompt for VS"
3. 选择对应的 Visual Studio 版本（VS 2019 或 VS 2022）
4. 打开命令提示符

### 步骤 2: 切换到项目目录

```cmd
cd /d C:\path\to\forensic-tool
```

将 `C:\path\to\forensic-tool` 替换为你的实际路径

### 步骤 3: 运行编译脚本

```cmd
build.bat
```

编译过程：
1. 检查 VS x64 环境
2. 编译 C 源文件为目标文件
3. 链接生成 DLL 文件

### 步骤 4: 验证编译结果

编译成功后会显示：
```
================================================
编译成功！
================================================

生成的文件：
   - build\scanner.dll      (动态链接库)
   - build\scanner.lib       (导入库)
   - src\file_scanner.obj    (目标文件)

文件信息：
...
```

---

## 运行步骤

### 步骤 1: 安装 Python 依赖

```cmd
cd forensic-tool
pip install -r requirements.txt
pip install fakeredis
```

### 步骤 2: 启动 API 服务

**方式 1: 后台运行（推荐）**

```cmd
start /B python main.py
```

**方式 2: 前台运行（查看日志）**

```cmd
python main.py
```

服务将运行在: http://localhost:8000

### 步骤 3: 测试服务

打开新的命令提示符窗口：

```cmd
# 健康检查
curl http://localhost:8000/

# 扫描测试数据
curl -X POST http://localhost:8000/scan ^
  -H "Content-Type: application/json" ^
  -d "{\"root_dir\": \"test_data\"}"

# 获取包名列表
curl http://localhost:8000/packages

# 关键词查询
curl -X POST http://localhost:8000/query ^
  -H "Content-Type: application/json" ^
  -d "{\"keyword\": \"password\", \"source\": \"sqlite\"}"

# 释放内存
curl -X POST http://localhost:8000/release_memory
```

### 步骤 4: 启动图形界面（可选）

```cmd
python ui.py
```

---

## 常见问题

### Q1: 编译错误 "未定义 VSCMD_VER"

**原因**: 未在 VS x64 命令提示符中运行

**解决**:
1. 重新打开 "x64 Native Tools Command Prompt for VS"
2. 切换到项目目录
3. 运行 build.bat

### Q2: 编译错误 "无法打开 include 文件 'dirent.h'"

**原因**: Windows 没有 dirent.h 头文件

**解决**: 项目已提供兼容的 dirent.h，确保它存在于 `include/` 目录

### Q3: 运行错误 "无法加载 DLL"

**原因**: DLL 文件不存在或路径错误

**解决**:
1. 确保已成功编译 `build/scanner.dll`
2. 检查 main.py 中的路径设置是否正确
3. 使用绝对路径或从项目根目录运行

### Q4: 运行错误 "Connection aborted"

**原因**: 内存管理问题（已在新版本中修复）

**解决**: 确保使用最新版本的代码

---

## API 文档

启动服务后，可以访问自动生成的 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 代码结构

### file_scanner.c 的工作原理

1. **平台检测**
   - 使用 `#ifdef _WIN32` 检测 Windows 平台
   - Windows 下使用 Windows API 实现目录操作
   - Linux 下使用 POSIX API

2. **目录扫描**
   - `opendir()` - 打开目录
   - `readdir()` - 读取目录项
   - `closedir()` - 关闭目录

3. **文件过滤**
   - 检查文件扩展名
   - 只处理支持的文件类型

4. **内存管理**
   - 使用 `calloc()` 分配内存（初始化为 0）
   - 提供 `free_files()` 函数释放内存

5. **DLL 导出**
   - 使用 `#ifdef BUILD_DLL` 定义导出宏
   - 使用 `__declspec(dllexport)` 导出函数

### dirent.h 的 Windows 实现

1. **结构定义**
   - `struct dirent` - 目录项结构
   - `struct DIR` - 目录流结构

2. **函数实现**
   - `opendir()` - 打开目录（使用 FindFirstFileA）
   - `readdir()` - 读取目录项（使用 FindNextFileA）
   - `closedir()` - 关闭目录（使用 FindClose）

3. **平台兼容**
   - Windows: 使用 Windows API 实现
   - Linux: 使用系统头文件（#include_next）

---

## 技术细节

### 编译选项说明

```cmd
# /c - 只编译，不链接
# /D BUILD_DLL - 定义 BUILD_DLL 宏
# /DWIN32 - 定义 WIN32 宏
# /D_WINDOWS - 定义 WINDOWS 宏
# /W3 - 警告级别 3
# /Ox - 最高优化级别
# /I include - 添加 include 目录到搜索路径
# /wd4133 - 禁用指针转换警告
# /wd4996 - 禁用不安全函数警告
# /Fo:src\file_scanner.obj - 指定输出文件名
cl.exe /c /D BUILD_DLL /DWIN32 /D_WINDOWS /W3 /Ox /Oi /Oy /GL /DNDEBUG /MD /EHsc /I include /wd4133 /wd4996 /Fo:src\file_scanner.obj src\file_scanner.c

# /DLL - 生成 DLL
# /OUT:build\scanner.dll - 指定输出文件名
# /IMPLIB:build\scanner.lib - 指定导入库文件名
# /MACHINE:x64 - 生成 64 位代码
link.exe /DLL /OUT:build\scanner.dll /IMPLIB:build\scanner.lib src\file_scanner.obj user32.lib kernel32.lib
```

### DLL 导出函数

三个导出函数供 Python 调用：

1. `scan_files()` - 扫描目录
   - 输入: 目录路径
   - 输出: 文件路径数组

2. `extract_content()` - 提取文件内容
   - 输入: 文件路径
   - 输出: 文件内容和长度

3. `free_files()` - 释放内存
   - 输入: 文件路径数组
   - 输出: 无

---

## 性能优化

### 已实现的优化

1. **文件大小限制** - 最大 100MB，避免内存溢出
2. **内存初始化** - 使用 calloc 替代 malloc
3. **批量扫描** - 一次调用扫描整个目录树
4. **类型过滤** - 只处理支持的文件类型

### 建议的优化

1. **多线程扫描** - 并发扫描多个目录
2. **内存池** - 预分配内存，减少 malloc/free 调用
3. **缓存结果** - 缓存扫描结果，避免重复扫描

---

## 调试技巧

### 启用调试输出

在 Python 代码中添加调试信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("正在扫描目录: %s", root_dir)
logger.debug("找到文件: %s", file_path)
```

### 使用调试器

1. 在 VS 中打开 `file_scanner.c`
2. 设置断点
3. 在 VS 中运行 `main.py`

---

## 提交到 Git

```cmd
# 查看修改
git status

# 添加修改的文件
git add src/file_scanner.c include/dirent.h build.bat build/scanner.dll

# 提交
git commit -m "feat: 添加 Windows 平台支持

- 创建 Windows 兼容的 dirent.h 头文件
- 修改 file_scanner.c 支持 Windows DLL 编译
- 更新 build.bat 编译脚本
- 添加详细的编译和运行文档"

# 推送
git push origin 260210-feat-forensic-database-tool
```

---

## 下一步

- 查看 README.md 了解项目概述
- 访问 http://localhost:8000/docs 查看 API 文档
- 运行测试验证功能
- 根据需要添加新功能

---

## 联系方式

如有问题，请查看：
- 项目文档
- GitHub Issues
- 提交反馈

---

**注意**: 请妥善保管代码和编译产物，不要在公开场合分享敏感信息。
