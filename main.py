import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import importlib

class Win32GenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Win32 Header Generator (win32more)")
        self.root.geometry("500x350")

        # win32more 内の実際のモジュールパス
        self.targets = {
            "Kernel32 (SystemInfo)": "win32more.Windows.Win32.System.SystemInformation",
            "User32 (Windows/UI)": "win32more.Windows.Win32.UI.WindowsAndMessaging",
            "GDI (Graphics)": "win32more.Windows.Win32.Graphics.Gdi"
        }

        self.setup_ui()

    def setup_ui(self):
        pad = {'padx': 20, 'pady': 10}
        ttk.Label(self.root, text="APIカテゴリを選択:", font=("Arial", 10, "bold")).pack(anchor="w", **pad)
        self.combo = ttk.Combobox(self.root, values=list(self.targets.keys()), state="readonly", width=50)
        self.combo.current(0)
        self.combo.pack(**pad)

        self.ext_var = tk.StringVar(value=".h")
        opts_frame = ttk.Frame(self.root)
        opts_frame.pack(anchor="w", padx=30)
        ttk.Radiobutton(opts_frame, text="C (.h)", variable=self.ext_var, value=".h").pack(side="left")
        ttk.Radiobutton(opts_frame, text="C++ (.cpp)", variable=self.ext_var, value=".cpp").pack(side="left", padx=20)

        ttk.Button(self.root, text="生成して保存", command=self.generate).pack(pady=30, ipadx=20)

    def generate(self):
        ext = self.ext_var.get()
        path = filedialog.asksaveasfilename(defaultextension=ext)
        if not path: return

        try:
            mod_path = self.targets[self.combo.get()]
            # モジュールを動的にロード
            module = importlib.import_module(mod_path)
            
            lines = ["#pragma once", "#include <windows.h>", ""]
            if ext == ".cpp": lines.append('extern "C" {')

            count = 0
            # モジュール内の関数(CFUNCTYPE)を抽出
            for name in dir(module):
                obj = getattr(module, name)
                # 呼び出し可能かつ、引数型(argtypes)を持つものをWin32APIとして扱う
                if callable(obj) and hasattr(obj, "argtypes"):
                    lines.append(f"void* {name}(...); // From {mod_path}")
                    count += 1

            if ext == ".cpp": lines.append("}")

            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("完了", f"{count}個の関数を抽出しました。")
        except Exception as e:
            messagebox.showerror("Error", f"生成失敗: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Win32GenApp(root)
    root.mainloop()
