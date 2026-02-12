import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests

class ForensicToolUI:
    def __init__(self, root):
        self.root = root
        self.root.title("取证比赛高速查询工具")
        self.root.geometry("1200x800")

        self.left_frame = ttk.Frame(root, width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(self.left_frame, text="包名/应用列表").pack(pady=5)
        self.package_list = ttk.Treeview(self.left_frame, columns=("name",), show="tree")
        self.package_list.pack(fill=tk.BOTH, expand=True)

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

    def load_packages(self):
        try:
            resp = requests.get("http://localhost:8000/packages", timeout=5)
            packages = resp.json().get("data", [])

            if not packages:
                self.result_text.insert(tk.END, "当前没有包名数据，请先扫描目录\n\n")
                return

            self.package_list.delete(*self.package_list.get_children())
            for pkg in packages:
                self.package_list.insert("", tk.END, text=pkg)
            self.result_text.insert(tk.END, f"✓ 已加载 {len(packages)} 个包名\n\n")
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
