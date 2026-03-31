import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
try:
    from win32metadata.metadata import Metadata
except ImportError:
    print("Error: 'pip install win32metadata' を実行してください。")

class Win32GenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Win32 Header Generator")
        self.root.geometry("450x300")

        # ターゲット設定
        self.targets = {
            "Kernel (SystemInformation, etc)": "Windows.Win32.System.SystemInformation",
            "User (UI.WindowsAndMessaging)": "Windows.Win32.UI.WindowsAndMessaging",
            "GDI (Graphics.Gdi)": "Windows.Win32.Graphics.Gdi"
        }

        # GUI Layout
        ttk.Label(root, text="1. 抽出対象を選択:", font=('bold', 10)).pack(pady=5)
        self.target_var = tk.StringVar(value=list(self.targets.keys())[0])
        self.combo = ttk.Combobox(root, textvariable=self.target_var, values=list(self.targets.keys()), width=40)
        self.combo.pack(pady=5)

        ttk.Label(root, text="2. 出力形式:", font=('bold', 10)).pack(pady=5)
        self.ext_var = tk.StringVar(value=".h (C)")
        ttk.Radiobutton(root, text="C (.h)", variable=self.ext_var, value=".h").pack()
        ttk.Radiobutton(root, text="C++ (.cpp)", variable=self.ext_var, value=".cpp").pack()

        self.btn_gen = ttk.Button(root, text="保存先を選んで変換実行", command=self.run_generation)
        self.btn_gen.pack(pady=30)

    def map_type(self, type_obj):
        t = str(type_obj)
        mapping = {
            'System.Void': 'void', 'System.Int32': 'int32_t', 'System.UInt32': 'uint32_t',
            'System.Int64': 'int64_t', 'System.UInt64': 'uint64_t', 'System.Boolean': 'bool',
            'System.String': 'const wchar_t*', 'Windows.Win32.Foundation.HANDLE': 'void*',
            'Windows.Win32.Foundation.HWND': 'void*', 'Windows.Win32.Foundation.HRESULT': 'int32_t'
        }
        return mapping.get(t, t.split('.')[-1])

    def run_generation(self):
        try:
            # winmdをロード (初回実行時は少し時間がかかります)
            meta = Metadata.load_default()
            namespace = self.targets[self.target_var.get()]
            ext = self.ext_var.get()
            
            # ファイル保存ダイアログ
            file_path = filedialog.asksaveasfilename(
                defaultextension=ext,
                filetypes=[("Header files", f"*{ext}"), ("All files", "*.*")]
            )
            if not file_path: return

            is_cpp = ext == ".cpp"
            functions = []

            for method in meta.get_methods():
                if method.namespace == namespace:
                    ret = self.map_type(method.return_type)
                    params = [f"{self.map_type(p.type)} {p.name}" for p in method.parameters]
                    p_str = ", ".join(params) if params else "void"
                    decl = f"{ret} {method.name}({p_str});"
                    
                    if is_cpp:
                        functions.append(f'extern "C" {decl}')
                    else:
                        functions.append(decl)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("#pragma once\n#include <stdint.h>\n\n")
                f.write("\n".join(functions))

            messagebox.showinfo("成功", f"{len(functions)}個のAPIを書き出しました！")

        except Exception as e:
            messagebox.showerror("エラー", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = Win32GenApp(root)
    root.mainloop()
