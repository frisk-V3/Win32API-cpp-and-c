import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import win32more
from win32more.core import Package

class Win32GenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Win32 Header Gen (win32more engine)")
        self.root.geometry("500x380")
        
        # ターゲットモジュールの定義
        self.api_map = {
            "Kernel32 (System/Files)": "win32more.Windows.Win32.System.SystemInformation",
            "User32 (Windows/UI)": "win32more.Windows.Win32.UI.WindowsAndMessaging",
            "GDI (Graphics)": "win32more.Windows.Win32.Graphics.Gdi"
        }
        self.setup_ui()

    def setup_ui(self):
        pad = {'padx': 20, 'pady': 10}
        ttk.Label(self.root, text="1. APIカテゴリの選択:", font=("Arial", 10, "bold")).pack(anchor="w", **pad)
        self.target_cat = tk.StringVar()
        self.combo = ttk.Combobox(self.root, textvariable=self.target_cat, values=list(self.api_map.keys()), state="readonly", width=55)
        self.combo.set(list(self.api_map.keys())[0])
        self.combo.pack(**pad)

        self.lang_var = tk.StringVar(value=".h")
        ttk.Radiobutton(self.root, text="C Header (.h)", variable=self.lang_var, value=".h").pack(anchor="w", padx=30)
        ttk.Radiobutton(self.root, text="C++ Header (.cpp)", variable=self.lang_var, value=".cpp").pack(anchor="w", padx=30)

        self.btn_save = ttk.Button(self.root, text="保存して生成実行", command=self.process)
        self.btn_save.pack(pady=30, ipadx=20, ipady=5)

    def process(self):
        ext = self.lang_var.get()
        save_path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[("Header", f"*{ext}")])
        if not save_path: return

        try:
            module_name = self.api_map[self.target_cat.get()]
            # 動的にインポート
            module = __import__(module_name, fromlist=['*'])
            
            output = ["#pragma once", "#include <stdint.h>", "#include <windows.h>", ""]
            if ext == ".cpp": output.append('extern "C" {')

            # 属性を走査して関数を探す
            count = 0
            for name in dir(module):
                attr = getattr(module, name)
                if callable(attr) and hasattr(attr, 'restype'):
                    # 簡易的なプロトタイプ生成
                    output.append(f"// {name} (Exported from {module_name})")
                    output.append(f"void* {name}(...);") # win32moreの型推論は複雑なため簡易化
                    count += 1

            if ext == ".cpp": output.append("}")

            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(output))
            
            messagebox.showinfo("成功", f"{count} 個の関数定義（プレースホルダ）を書き出しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"モジュールの読み込みに失敗しました: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    Win32GenApp(root)
    root.mainloop()
