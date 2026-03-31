import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict

try:
    from win32metadata.metadata import Metadata
except ImportError:
    print("Error: 'pip install win32metadata' is required.")

class Win32HeaderGenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Win32 API Header Generator v1.0")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        # ターゲット名前空間の定義
        self.categories: Dict[str, list] = {
            "Kernel (System/Threading/File)": [
                "Windows.Win32.System.SystemInformation",
                "Windows.Win32.System.Threading",
                "Windows.Win32.Storage.FileSystem"
            ],
            "User (Windows/Messaging/Input)": [
                "Windows.Win32.UI.WindowsAndMessaging",
                "Windows.Win32.UI.Input.KeyboardAndMouse"
            ],
            "GDI (Graphics/Drawing)": [
                "Windows.Win32.Graphics.Gdi"
            ]
        }

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", padding=5)

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="1. APIカテゴリを選択", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        self.cat_var = tk.StringVar(value=list(self.categories.keys())[0])
        self.combo = ttk.Combobox(main_frame, textvariable=self.cat_var, values=list(self.categories.keys()), state="readonly", width=50)
        self.combo.pack(pady=(5, 15))

        ttk.Label(main_frame, text="2. 出力言語 / 拡張子", font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        self.lang_var = tk.StringVar(value="C")
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(pady=5, anchor=tk.W)
        ttk.Radiobutton(lang_frame, text="C (.h)", variable=self.lang_var, value="C").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(lang_frame, text="C++ (.cpp)", variable=self.lang_var, value="CPP").pack(side=tk.LEFT, padx=10)

        self.progress = ttk.Progressbar(main_frame, mode='determinate', length=400)
        self.progress.pack(pady=20)

        self.btn_run = ttk.Button(main_frame, text="保存先を指定して生成開始", command=self.generate)
        self.btn_run.pack(fill=tk.X, pady=10)

    def map_type(self, type_obj) -> str:
        t = str(type_obj)
        mapping = {
            'System.Void': 'void', 'System.Int32': 'int32_t', 'System.UInt32': 'uint32_t',
            'System.Int64': 'int64_t', 'System.UInt64': 'uint64_t', 'System.Boolean': 'bool',
            'System.String': 'const wchar_t*', 'Windows.Win32.Foundation.HANDLE': 'HANDLE',
            'Windows.Win32.Foundation.HWND': 'HWND', 'Windows.Win32.Foundation.HRESULT': 'HRESULT',
            'Windows.Win32.Foundation.LPARAM': 'LPARAM', 'Windows.Win32.Foundation.WPARAM': 'WPARAM'
        }
        return mapping.get(t, t.split('.')[-1])

    def generate(self):
        ext = ".h" if self.lang_var.get() == "C" else ".cpp"
        file_path = filedialog.asksaveasfilename(
            title="ヘッダーの保存先",
            defaultextension=ext,
            filetypes=[("Header Files", f"*{ext}")]
        )
        if not file_path: return

        try:
            meta = Metadata.load_default()
            namespaces = self.categories[self.cat_var.get()]
            lines = ["#pragma once", "#include <stdint.h>", "#include <windows.h>", ""]
            
            if self.lang_var.get() == "CPP":
                lines.append('extern "C" {')

            methods = [m for m in meta.get_methods() if m.namespace in namespaces]
            self.progress['maximum'] = len(methods)

            for i, m in enumerate(methods):
                ret = self.map_type(m.return_type)
                params = [f"{self.map_type(p.type)} {p.name}" for p in m.parameters]
                p_str = ", ".join(params) if params else "void"
                lines.append(f"{ret} {m.name}({p_str});")
                if i % 10 == 0:
                    self.progress['value'] = i
                    self.root.update()

            if self.lang_var.get() == "CPP":
                lines.append('}')

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            self.progress['value'] = len(methods)
            messagebox.showinfo("完了", f"生成成功: {len(methods)}個のAPIを抽出しました。")
        except Exception as e:
            messagebox.showerror("Error", f"失敗しました: {str(e)}")
        finally:
            self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = Win32HeaderGenApp(root)
    root.mainloop()
