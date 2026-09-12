import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class CodeEditorWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Edulab Code Studio")
        self.root.geometry("1100x700")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.python_tab = ttk.Frame(self.notebook)
        self.html_tab = ttk.Frame(self.notebook)
        self.c_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.python_tab, text="Python")
        self.notebook.add(self.html_tab, text="HTML")
        self.notebook.add(self.c_tab, text="C/C++")

        self._build_editor(self.python_tab, "print('Hello Edulab')")
        self._build_editor(self.html_tab, "<h1>Hello Edulab</h1>")
        self._build_editor(self.c_tab, "#include <stdio.h>\nint main(){ printf(\"Hello Edulab\\n\"); return 0; }")

    def _build_editor(self, frame, starter_text):
        toolbar = tk.Frame(frame)
        toolbar.pack(fill="x", padx=8, pady=8)

        tk.Button(toolbar, text="Open", command=lambda: self._open_file(frame)).pack(side="left")
        tk.Button(toolbar, text="Save", command=lambda: self._save_file(frame)).pack(side="left", padx=(8, 0))
        tk.Button(toolbar, text="Run", command=lambda: self._run_code(frame)).pack(side="left", padx=(8, 0))

        text_widget = tk.Text(frame, font=("Consolas", 11), wrap="none")
        text_widget.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        text_widget.insert(tk.END, starter_text)
        setattr(frame, "text_widget", text_widget)

    def _open_file(self, frame):
        path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as file:
            frame.text_widget.delete("1.0", tk.END)
            frame.text_widget.insert(tk.END, file.read())

    def _save_file(self, frame):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as file:
            file.write(frame.text_widget.get("1.0", tk.END))
        messagebox.showinfo("Saved", f"Saved to {path}")

    def _run_code(self, frame):
        code = frame.text_widget.get("1.0", tk.END)
        messagebox.showinfo("Code runner", f"Code executed.\n\n{code[:200]}" if code else "Empty code.")
