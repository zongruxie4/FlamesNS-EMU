#!/usr/bin/env python3
"""
EmuNX 1.x — Ryujinx-Inspired GUI Edition (800×600)
--------------------------------------------------
A Samsoft Production ©2025
No dependencies beyond Python's built-in tkinter.
Introspection snapshot in a layout mimicking Ryujinx's dark-themed WPF UI:
- Top menu bar (File, Tools, Help)
- Left sidebar navigation (like game panel)
- Central table/list for details (like game info)
- Bottom console/status bar
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Listbox
from tkinter.ttk import Treeview

APP_NAME = "EmuNX"
APP_VERSION = "1.x"

def snapshot():
    """Collect basic interpreter info without using external modules."""
    return {
        "python_version": sys.version,
        "executable": sys.executable,
        "platform": sys.platform,
        "byteorder": sys.byteorder,
        "maxsize": sys.maxsize,
        "recursion_limit": sys.getrecursionlimit(),
        "path": sys.path[:10],  # Limit for display
        "modules_loaded": len(sys.modules),
        "flags": {n: getattr(sys.flags, n) for n in dir(sys.flags) if not n.startswith('_')},
        "modules_preview": list(sys.modules.keys())[:20],  # Mock "games" list
    }

class EmuNXGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        self.snap = snapshot()
        self.current_view = tk.StringVar(value="info")
        self.make_ui()

    def make_ui(self):
        # Dark theme configuration (Ryujinx-inspired: black/gray, white text)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("TButton", background="#333", foreground="white", borderwidth=0)
        style.map("TButton", background=[("active", "#555")])
        style.configure("Sidebar.TButton", font=("Consolas", 10), padding=(10, 5))
        style.configure("Header.TLabel", font=("Consolas", 12, "bold"), foreground="#4a90e2")  # Blue accent like Ryujinx logo
        style.configure("TNotebook.Tab", background="#444", foreground="white")
        style.map("TNotebook.Tab", background=[("selected", "#111")])
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading", background="#444", foreground="white")

        # Top menu bar (mimics Ryujinx: File, Options/Tools, Help)
        menubar = tk.Menu(self.root, bg="#2b2b2b", fg="white", activebackground="#444", activeforeground="white")
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.destroy)

        tools_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Snapshot", command=lambda: self.update_snapshot())

        help_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", f"{APP_NAME} {APP_VERSION}\nRyujinx-Inspired Introspector"))

        # Title bar
        title_frame = tk.Frame(self.root, bg="#1e1e1e", height=30)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        title = ttk.Label(title_frame, text=f"{APP_NAME} {APP_VERSION} — Runtime Introspector | FPS: N/A | Sync: Off", style="Header.TLabel")
        title.pack(side="left", padx=10, pady=5)

        # Main container: Left sidebar + Central content
        main_container = tk.Frame(self.root, bg="#1e1e1e")
        main_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Left sidebar (mimics Ryujinx game panel: narrow, with nav items)
        sidebar = tk.Frame(main_container, width=200, bg="#2b2b2b")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ttk.Label(sidebar, text="Navigation", font=("Consolas", 11, "bold")).pack(pady=10)
        nav_items = [("Info", "info"), ("Modules", "modules"), ("Settings", "settings")]
        for text, var in nav_items:
            btn = ttk.Button(sidebar, text=text, style="Sidebar.TButton",
                             command=lambda v=var: self.show_view(v))
            btn.pack(fill="x", pady=2, padx=10)

        # Central content area (mimics Ryujinx game details table/panel)
        self.content_frame = tk.Frame(main_container, bg="#1e1e1e")
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Bottom console/status bar (mimics Ryujinx log viewer)
        console_frame = tk.Frame(self.root, bg="#000", height=100)
        console_frame.pack(fill="x")
        console_frame.pack_propagate(False)
        self.console = scrolledtext.ScrolledText(console_frame, bg="#000", fg="#0f0", insertbackground="green", font=("Consolas", 8), state="disabled")
        self.console.pack(fill="both", expand=True, padx=5, pady=2)
        self.log("EmuNX initialized. Welcome to Ryujinx-inspired mode.")

        # Initial view
        self.show_view("info")

    def update_snapshot(self):
        self.snap = snapshot()
        self.log("Snapshot updated.")
        self.show_view(self.current_view.get())

    def log(self, msg):
        self.console.config(state="normal")
        self.console.insert("end", f"[INFO] {msg}\n")
        self.console.see("end")
        self.console.config(state="disabled")

    def show_view(self, view):
        self.current_view.set(view)
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if view == "info":
            # Info as text (like Ryujinx about panel)
            text = scrolledtext.ScrolledText(self.content_frame, bg="#2b2b2b", fg="white",
                                             insertbackground="white", font=("Consolas", 9), wrap=tk.WORD)
            text.pack(fill="both", expand=True, padx=10, pady=10)
            for k, v in self.snap.items():
                text.insert("end", f"{k}: {v}\n")
            text.config(state="disabled")

        elif view == "modules":
            # Modules as list/table (mimics Ryujinx game list)
            frame = tk.Frame(self.content_frame)
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            columns = ("Name", "Status")  # Mock like Developer/Version
            tree = Treeview(frame, columns=columns, show="headings", height=15)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=200)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            scrollbar.pack(side="right", fill="y")
            tree.config(yscrollcommand=scrollbar.set)
            for mod in self.snap["modules_preview"]:
                tree.insert("", "end", values=(mod, "Loaded"))

        elif view == "settings":
            # Settings panel (like Ryujinx options)
            pad_frame = tk.Frame(self.content_frame, bg="#1e1e1e")
            pad_frame.pack(fill="both", expand=True, padx=10, pady=10)

            ttk.Label(pad_frame, text="Recursion Limit:", font=("Consolas", 10)).pack(anchor="w", pady=5)
            entry = ttk.Entry(pad_frame, font=("Consolas", 9))
            entry.insert(0, str(sys.getrecursionlimit()))
            entry.pack(fill="x", pady=2)

            def set_recursion():
                try:
                    val = int(entry.get())
                    old = sys.getrecursionlimit()
                    sys.setrecursionlimit(val)
                    messagebox.showinfo("Updated", f"Recursion limit {old} → {val}")
                    self.log(f"Recursion limit set to {val}")
                except ValueError:
                    messagebox.showerror("Error", "Invalid integer")

            ttk.Button(pad_frame, text="Apply", command=set_recursion).pack(pady=10)

            def demo_exception():
                try:
                    1 / 0
                except Exception as e:
                    self.log(f"Exception: {type(e).__name__}: {e}")
                    messagebox.showwarning("Caught Exception", f"{type(e).__name__}: {e}")

            ttk.Button(pad_frame, text="Trigger Exception", command=demo_exception).pack(pady=5)

        self.log(f"Switched to {view} view.")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmuNXGUI(root)
    root.mainloop()
