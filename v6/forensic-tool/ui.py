import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
import os


class ForensicToolUI:
    def __init__(self, root):
        self.root = root
        self.root.title("取证比赛高速查询工具")
        self.root.geometry("1600x900")

        # 检测是否为Windows环境，默认使用文字图标
        self.use_emoji = (os.name != 'nt')

        self.left_frame = ttk.Frame(root, width=600)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(self.left_frame, text="应用列表", font=("Arial", 12, "bold")).pack(pady=5)

        # 创建带图标的 Treeview，显示包名、应用名称
        list_container = ttk.Frame(self.left_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.package_list = ttk.Treeview(list_container, columns=("icon", "app_name", "package_name"), show="headings")
        self.package_list.column("icon", width=50, minwidth=50, stretch=False, anchor="center")
        self.package_list.column("app_name", width=200, minwidth=150, stretch=True)
        self.package_list.column("package_name", width=300, minwidth=200, stretch=True)
        self.package_list.heading("icon", text="")
        self.package_list.heading("app_name", text="应用名称")
        self.package_list.heading("package_name", text="包名")

        # 双击显示完整包名
        self.package_list.bind("<Double-1>", self.show_full_package_name)

        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.package_list.yview)
        hscrollbar = ttk.Scrollbar(list_container, orient="horizontal", command=self.package_list.xview)
        self.package_list.configure(yscrollcommand=scrollbar.set, xscrollcommand=hscrollbar.set)

        self.package_list.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        hscrollbar.grid(row=1, column=0, sticky="ew")

        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        self.right_frame = ttk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 分类选择区域
        category_frame = ttk.LabelFrame(self.right_frame, text="分类查询", padding=10)
        category_frame.pack(fill=tk.X, pady=5)

        self.category_var = tk.StringVar(value="")
        category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, state="readonly", width=20)
        category_combo.pack(side=tk.LEFT, padx=5)
        category_combo['values'] = ["全部", "账号密码", "管理员权限", "网络配置", "数据库连接", "API密钥", "加密信息",
                                    "位置信息", "设备信息", "通信记录", "文件路径", "日志信息", "时间戳", "配置文件",
                                    "用户数据", "支付信息", "会话信息"]

        ttk.Button(category_frame, text="按分类查询", command=self.query_by_category).pack(side=tk.LEFT, padx=5)

        # 关键词查询区域
        ttk.Label(self.right_frame, text="查询关键词").pack(pady=5)
        query_frame = ttk.Frame(self.right_frame)
        query_frame.pack(fill=tk.X, pady=5)

        self.keyword_entry = ttk.Entry(query_frame, font=("Arial", 12))
        self.keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.source_var = tk.StringVar(value="redis")
        ttk.Radiobutton(query_frame, text="Redis（高速）", variable=self.source_var, value="redis").pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Radiobutton(query_frame, text="SQLite（本地）", variable=self.source_var, value="sqlite").pack(side=tk.LEFT,
                                                                                                         padx=5)

        button_frame = ttk.Frame(self.right_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="查询", command=self.query).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新应用列表", command=self.load_packages).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空数据", command=self.clear_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="释放内存", command=self.release_memory).pack(side=tk.LEFT, padx=5)

        # 扫描目录区域
        ttk.Label(self.right_frame, text="扫描目录").pack(pady=5)
        scan_frame = ttk.Frame(self.right_frame)
        scan_frame.pack(fill=tk.X, pady=5)

        self.path_entry = ttk.Entry(scan_frame, font=("Arial", 12))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(scan_frame, text="浏览", command=self.browse_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(scan_frame, text="扫描", command=self.scan_directory).pack(side=tk.LEFT, padx=5)

        # 查询结果显示区域
        self.result_text = scrolledtext.ScrolledText(self.right_frame, font=("Arial", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

        self.result_text.insert(tk.END, "欢迎使用取证工具\n")
        self.result_text.insert(tk.END, "功能说明：\n")
        self.result_text.insert(tk.END, "- 支持扫描并显示应用名称和图标\n")
        self.result_text.insert(tk.END, "- 支持分类查询：账号密码、管理员权限、API密钥等\n")
        self.result_text.insert(tk.END, "- 支持关键词快速查询\n")
        self.result_text.insert(tk.END, "请先选择并扫描目录，然后进行查询\n")
        self.result_text.insert(tk.END, "----------------------------------------\n\n")
        # 初始化关键词高亮标签
        self.result_text.tag_configure("highlight", background="yellow", foreground="red", font=("Arial", 10, "bold"))

    def show_full_package_name(self, event):
        selection = self.package_list.selection()
        if selection:
            item = selection[0]
            # 获取包名（第三列）
            package_name = self.package_list.item(item, "values")[2]

            try:
                # 调用 API 查询该包名的文件路径
                resp = requests.get(f"http://localhost:8000/package_paths?package_name={package_name}", timeout=10)
                result = resp.json()

                if result.get("status") == "success" and result.get("paths"):
                    paths = result["paths"]

                    # 如果有多个路径，让用户选择
                    if len(paths) == 1:
                        self.open_in_explorer(paths[0], package_name)
                    else:
                        # 创建选择对话框
                        dialog = tk.Toplevel(self.root)
                        dialog.title(f"选择路径 - {package_name}")
                        dialog.geometry("600x400")

                        ttk.Label(dialog, text=f"包名：{package_name}", font=("Arial", 12, "bold")).pack(pady=10)
                        ttk.Label(dialog, text="找到多个路径，请选择一个打开：").pack(pady=5)

                        # 创建带滚动条的列表
                        list_container = ttk.Frame(dialog)
                        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

                        scrollbar = ttk.Scrollbar(list_container)
                        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                        path_list = tk.Listbox(list_container, yscrollcommand=scrollbar.set, font=("Arial", 10))
                        path_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                        scrollbar.config(command=path_list.yview)

                        for path in paths:
                            path_list.insert(tk.END, path)

                        # 双击打开路径
                        def on_double_click(event):
                            selection = path_list.curselection()
                            if selection:
                                selected_path = path_list.get(selection[0])
                                dialog.destroy()
                                self.open_in_explorer(selected_path, package_name)

                        path_list.bind("<Double-1>", on_double_click)

                        # 添加确认按钮
                        button_frame = ttk.Frame(dialog)
                        button_frame.pack(pady=10)

                        def on_confirm():
                            selection = path_list.curselection()
                            if selection:
                                selected_path = path_list.get(selection[0])
                                dialog.destroy()
                                self.open_in_explorer(selected_path, package_name)

                        ttk.Button(button_frame, text="打开选中路径", command=on_confirm).pack(side=tk.LEFT, padx=5)
                        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
                else:
                    messagebox.showwarning("提示", f"未找到包名 '{package_name}' 对应的文件路径")

            except Exception as e:
                messagebox.showerror("错误", f"打开路径失败：{e}")

    def insert_highlighted_text(self, content, keyword):
        """
        在文本框中插入内容，并高亮显示关键词
        :param content: 要显示的文本内容
        :param keyword: 要高亮的关键词（支持大小写不敏感）
        """
        if not keyword or not content:
            self.result_text.insert(tk.END, content)
            return

        # 转换为小写，实现大小写不敏感匹配
        content_lower = content.lower()
        keyword_lower = keyword.lower()
        start_idx = 0

        while True:
            # 查找关键词位置
            pos = content_lower.find(keyword_lower, start_idx)
            if pos == -1:
                # 插入剩余文本
                self.result_text.insert(tk.END, content[start_idx:])
                break

            # 插入关键词前的文本
            self.result_text.insert(tk.END, content[start_idx:pos])
            # 插入高亮的关键词
            keyword_end = pos + len(keyword)
            self.result_text.insert(tk.END, content[pos:keyword_end], "highlight")
            # 更新起始位置
            start_idx = keyword_end

    def open_in_explorer(self, path, package_name):
        import subprocess
        import os

        try:
            # 从文件路径中提取包名所在的目录
            normalized_path = path.replace("\\", "/")
            path_parts = [p for p in normalized_path.split("/") if p]

            # 找到包名在路径中的位置
            package_index = -1
            for i, part in enumerate(path_parts):
                if part == package_name:
                    package_index = i
                    break

            if package_index != -1 and package_index > 0:
                # 包名所在目录是包名的前一级
                directory_parts = path_parts[:package_index + 1]
                directory = "/" + "/".join(directory_parts)

                # 移除开头的根目录标记（如 /D:/）
                if directory.startswith("/") and len(directory) > 1 and directory[2] == ":":
                    directory = directory[1:]
            else:
                # 如果找不到包名，使用文件所在目录
                directory = os.path.dirname(path)

            # 在 Windows 环境下转换路径格式
            if os.name == 'nt':
                directory = directory.replace("/", "\\")

            print(f"打开目录：{directory}")

            # 根据操作系统选择打开方式
            if os.name == 'nt':  # Windows
                subprocess.Popen(['explorer', directory])
            elif os.name == 'posix':  # Linux/Mac
                subprocess.Popen(['xdg-open', directory])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件资源管理器：{e}")

    def load_packages(self):
        try:
            resp = requests.get("http://localhost:8000/packages", timeout=5)
            package_data = resp.json().get("data", [])

            if not package_data:
                self.result_text.insert(tk.END, "当前没有应用数据，请先扫描目录\n\n")
                return

            self.package_list.delete(*self.package_list.get_children())

            # 按应用名称排序
            package_data_sorted = sorted(package_data, key=lambda x: x["app_name"])

            for pkg_info in package_data_sorted:
                # 在Windows环境下，如果图标显示异常，尝试使用文字版本
                icon = pkg_info.get("icon", "📱")
                # 如果是emoji且在Windows下，尝试转换为文字（这里简单处理）
                if os.name == 'nt' and len(icon) > 2 and ord(icon[0]) > 127:
                    # 这是一个emoji，使用文字替代
                    app_name = pkg_info.get("app_name", pkg_info["package_name"])
                    # 根据应用名称推测类型（简单实现）
                    if "微信" in app_name or "QQ" in app_name or "钉钉" in app_name:
                        icon = "[聊天]"
                    elif "淘宝" in app_name or "京东" in app_name or "美团" in app_name:
                        icon = "[购物]"
                    elif "支付宝" in app_name or "银行" in app_name or "银联" in app_name:
                        icon = "[金融]"
                    elif "音乐" in app_name or "视频" in app_name or "抖音" in app_name:
                        icon = "[媒体]"
                    elif "地图" in app_name:
                        icon = "[地图]"
                    elif "游戏" in app_name:
                        icon = "[游戏]"
                    else:
                        icon = "[应用]"

                app_name = pkg_info.get("app_name", pkg_info["package_name"])
                package_name = pkg_info["package_name"]
                self.package_list.insert("", tk.END, values=(icon, app_name, package_name))

            self.result_text.insert(tk.END, f"✓ 已加载 {len(package_data_sorted)} 个应用\n\n")
        except Exception as e:
            self.result_text.insert(tk.END, f"✗ 加载应用列表失败：{e}\n\n")

    def query(self):
        keyword = self.keyword_entry.get()
        if not keyword:
            messagebox.showwarning("警告", "请输入查询关键词！")
            return

        try:
            resp = requests.post(
                "http://localhost:8000/query",
                json={"keyword": keyword, "source": self.source_var.get()},
                timeout=30
            )
            result = resp.json()
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"查询耗时：{result['cost_ms']}ms\n")
            self.result_text.insert(tk.END, f"匹配数量：{result['count']}\n\n")

            for item in result["data"]:
                category = item.get('category', '未分类')
                self.result_text.insert(tk.END, f"文件路径：{item['file_path']}\n")
                self.result_text.insert(tk.END, f"分类：{category}\n")
                self.result_text.insert(tk.END, "内容片段：")
                # 高亮显示关键词
                self.insert_highlighted_text(item['content'] + "\n", keyword)
                self.result_text.insert(tk.END, "------------------------\n")
        except Exception as e:
            messagebox.showerror("错误", f"查询失败：{e}")

    def query_by_category(self):
        from app_metadata import CATEGORY_KEYWORDS  # 导入分类关键词库
        category = self.category_var.get()
        if not category or category == "全部":
            messagebox.showwarning("警告", "请选择要查询的分类！")
            return
        category_keywords = CATEGORY_KEYWORDS.get(category, [])
        if not category_keywords:
            messagebox.showerror("错误", f"无效的分类名称：{category}")
            return
        try:
            # 调用新增的分类查询接口
            resp = requests.post(
                "http://localhost:8000/query_by_category",
                json={"keyword": category, "source": self.source_var.get()},
                timeout=30
            )
            # 检查响应状态码
            if resp.status_code != 200:
                messagebox.showerror("错误", f"接口返回异常：{resp.status_code}")
                return

            result = resp.json()

            if result.get("status") == "error":
                messagebox.showerror("错误", result["message"])
                return

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"分类查询：{category}\n")
            self.result_text.insert(tk.END, f"匹配关键词：{', '.join(result.get('matched_keywords', []))}\n")
            self.result_text.insert(tk.END, f"查询耗时：{result['cost_ms']}ms\n")
            self.result_text.insert(tk.END, f"匹配数量：{result['count']}\n\n")

            if result["count"] == 0:
                self.result_text.insert(tk.END, "未找到该分类的匹配结果\n")
            else:
                for item in result["data"]:
                    self.result_text.insert(tk.END, f"文件路径：{item['file_path']}\n")
                    if "package_name" in item and item["package_name"] != "未知包名":
                        self.result_text.insert(tk.END, f"包名：{item['package_name']}\n")
                    self.result_text.insert(tk.END, f"分类：{item['category']}\n")
                    self.result_text.insert(tk.END, f"内容片段：{item['content']}\n")
                    # 高亮显示该分类下的所有关键词
                    content = item['content']
                    # 先插入原始文本，再逐个标记关键词
                    temp_idx = self.result_text.index(tk.END)
                    self.result_text.insert(tk.END, content + "\n")

                    # 为每个关键词添加高亮
                    for kw in category_keywords:
                        if kw.lower() in content.lower():
                            # 查找所有匹配位置并高亮
                            content_lower = content.lower()
                            kw_lower = kw.lower()
                            start = 0
                            while True:
                                pos = content_lower.find(kw_lower, start)
                                if pos == -1:
                                    break
                                # 计算在文本框中的位置
                                start_pos = f"{temp_idx}+{pos}c"
                                end_pos = f"{temp_idx}+{pos + len(kw)}c"
                                # 添加高亮标签
                                self.result_text.tag_add("highlight", start_pos, end_pos)
                                start = pos + len(kw)
                    self.result_text.insert(tk.END, "------------------------\n")

        except requests.exceptions.ConnectionError:
            messagebox.showerror("错误", "无法连接到后端服务，请确认 main.py 已启动！")
        except requests.exceptions.Timeout:
            messagebox.showerror("错误", "请求超时，请重试！")
        except ValueError:  # JSON解析失败
            messagebox.showerror("错误", "后端返回非JSON数据，请检查服务日志！")
        except Exception as e:
            messagebox.showerror("错误", f"分类查询失败：{str(e)}")

    def browse_directory(self):
        directory = filedialog.askdirectory(title="选择要扫描的目录")
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)

    def clear_data(self):
        if messagebox.askyesno("确认", "确定要清空所有扫描数据吗？"):
            try:
                resp = requests.post("http://localhost:8000/clear_data", timeout=10)
                result = resp.json()
                self.package_list.delete(*self.package_list.get_children())
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "✓ 数据已清空\n")
                self.result_text.insert(tk.END, "----------------------------------------\n\n")
            except Exception as e:
                messagebox.showerror("错误", f"清空数据失败：{e}")

    def scan_directory(self):
        root_dir = self.path_entry.get()
        if not root_dir:
            messagebox.showwarning("警告", "请先选择要扫描的目录！")
            return

        self.result_text.insert(tk.END, f"正在扫描目录: {root_dir}\n")
        self.result_text.insert(tk.END, "请稍候...\n\n")
        self.root.update()

        try:
            resp = requests.post(
                "http://localhost:8000/scan",
                json={"root_dir": root_dir},
                timeout=300
            )
            result = resp.json()

            self.result_text.insert(tk.END, f"✓ {result['message']}\n")
            self.result_text.insert(tk.END, "----------------------------------------\n")

            self.load_packages()
        except Exception as e:
            messagebox.showerror("错误", f"扫描失败：{e}")

    def release_memory(self):
        try:
            resp = requests.post("http://localhost:8000/release_memory", timeout=10)
            result = resp.json()
            messagebox.showinfo("成功", result['message'])
        except Exception as e:
            messagebox.showerror("错误", f"释放内存失败：{e}")
            messagebox.showerror("错误", f"释放内存失败：{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ForensicToolUI(root)
    root.mainloop()