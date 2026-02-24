import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests

class ForensicToolUI:
    def __init__(self, root):
        self.root = root
        self.root.title("取证比赛高速查询工具")
        self.root.geometry("1400x800")

        self.left_frame = ttk.Frame(root, width=450)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(self.left_frame, text="包名/应用列表").pack(pady=5)
        
        # 创建带滚动条的 Treeview
        list_container = ttk.Frame(self.left_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.package_list = ttk.Treeview(list_container, columns=("name",), show="headings")
        self.package_list.column("name", width=420, minwidth=300, stretch=True)
        self.package_list.heading("name", text="包名")
        
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

        ttk.Label(self.right_frame, text="查询关键词").pack(pady=5)
        self.keyword_entry = ttk.Entry(self.right_frame, font=("Arial", 12))
        self.keyword_entry.pack(fill=tk.X, pady=5)

        self.source_var = tk.StringVar(value="redis")
        ttk.Radiobutton(self.right_frame, text="Redis（高速）", variable=self.source_var, value="redis").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.right_frame, text="SQLite（本地）", variable=self.source_var, value="sqlite").pack(side=tk.LEFT, padx=5)

        query_frame = ttk.Frame(self.right_frame)
        query_frame.pack(fill=tk.X, pady=5)
        ttk.Button(query_frame, text="查询", command=self.query).pack(side=tk.LEFT, padx=5)
        ttk.Button(query_frame, text="刷新包名", command=self.load_packages).pack(side=tk.LEFT, padx=5)
        ttk.Button(query_frame, text="清空数据", command=self.clear_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(query_frame, text="释放内存", command=self.release_memory).pack(side=tk.LEFT, padx=5)

        ttk.Label(self.right_frame, text="扫描目录").pack(pady=5)
        scan_frame = ttk.Frame(self.right_frame)
        scan_frame.pack(fill=tk.X, pady=5)
        self.path_entry = ttk.Entry(scan_frame, font=("Arial", 12))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(scan_frame, text="浏览", command=self.browse_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(scan_frame, text="扫描", command=self.scan_directory).pack(side=tk.LEFT, padx=5)

        self.result_text = scrolledtext.ScrolledText(self.right_frame, font=("Arial", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

        self.result_text.insert(tk.END, "欢迎使用取证工具\n")
        self.result_text.insert(tk.END, "请先选择并扫描目录，然后进行查询\n")
        self.result_text.insert(tk.END, "----------------------------------------\n\n")

    def show_full_package_name(self, event):
        selection = self.package_list.selection()
        if selection:
            item = selection[0]
            package_name = self.package_list.item(item, "values")[0]
            
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
            packages = resp.json().get("data", [])

            if not packages:
                self.result_text.insert(tk.END, "当前没有包名数据，请先扫描目录\n\n")
                return

            self.package_list.delete(*self.package_list.get_children())
            # 按字母顺序排序
            packages_sorted = sorted(packages)
            for pkg in packages_sorted:
                self.package_list.insert("", tk.END, values=(pkg,))
            self.result_text.insert(tk.END, f"✓ 已加载 {len(packages_sorted)} 个包名\n\n")
        except Exception as e:
            self.result_text.insert(tk.END, f"✗ 加载包名失败：{e}\n\n")

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
                self.result_text.insert(tk.END, f"文件路径：{item['file_path']}\n")
                self.result_text.insert(tk.END, f"内容片段：{item['content']}\n")
                self.result_text.insert(tk.END, "------------------------\n")
        except Exception as e:
            messagebox.showerror("错误", f"查询失败：{e}")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ForensicToolUI(root)
    root.mainloop()
