#!/usr/bin/env python3
"""
RyujinxNX - Nintendo Switch Emulator Launcher (Version 0.0.1)
Simulated GUI inspired by Ryujinx
(C) Flames Co. Labs 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import os
import random
import platform
import json
from datetime import datetime
try:
    import psutil
except ImportError:
    psutil = None

# =========================================================
# 🧠 CORE EMULATOR SIMULATION
# =========================================================
class RyujinxEmulator:
    def __init__(self):
        self.is_running = False
        self.current_game = None
        self.performance_stats = {
            "fps": 0,
            "cpu_usage": 0,
            "ram_usage": 0,
            "frame_time": 0.0,
        }
        self._lock = threading.Lock()

    def start_emulation(self, game_path):
        if not os.path.exists(game_path):
            raise FileNotFoundError(f"Game not found: {game_path}")
        self.is_running = True
        self.current_game = game_path
        threading.Thread(target=self._monitor, daemon=True).start()

    def stop_emulation(self):
        self.is_running = False
        self.current_game = None

    def _monitor(self):
        while self.is_running:
            with self._lock:
                self.performance_stats["fps"] = random.randint(25, 60)
                self.performance_stats["frame_time"] = round(random.uniform(8, 25), 2)
                self.performance_stats["cpu_usage"] = round(random.uniform(15, 80), 1)
                self.performance_stats["ram_usage"] = round(random.uniform(512, 4096), 1)
            time.sleep(1)

# =========================================================
# 🎮 GAME LIBRARY
# =========================================================
class GameLibrary:
    def __init__(self):
        self.games = []
        self.load_games()

    def load_games(self):
        """Load games from a JSON file if it exists."""
        try:
            if os.path.exists("games.json"):
                with open("games.json", "r") as f:
                    loaded_games = json.load(f)
                    for game in loaded_games:
                        # Validate path and supported file types
                        if os.path.exists(game["path"]) and game["path"].lower().endswith(('.nsp', '.xci')):
                            self.games.append(game)
                        else:
                            game["path"] = ""  # Placeholder for missing/invalid files
                            self.games.append(game)
        except json.JSONDecodeError:
            pass  # Silently ignore invalid JSON

    def save_games(self):
        """Save games to a JSON file."""
        with open("games.json", "w") as f:
            json.dump(self.games, f, indent=4)

    def add_game(self, game_path):
        if not game_path.lower().endswith(('.nsp', '.xci')):
            raise ValueError("Invalid file type. Only .nsp and .xci files are supported.")
        if not os.path.exists(game_path):
            raise FileNotFoundError(f"Game file not found: {game_path}")
        name = os.path.splitext(os.path.basename(game_path))[0]
        game = {
            "title": name,
            "path": game_path,
            "icon": "🎮",
            "developer": "Unknown",
            "version": "1.0.0",
            "size": f"{random.randint(2, 16)}.{random.randint(0, 9)} GB",
            "last_played": "Never",
            "play_time": "00:00:00",
        }
        self.games.append(game)
        self.save_games()
        return game

    def remove_game(self, title):
        """Remove a game by title."""
        self.games = [g for g in self.games if g["title"] != title]
        self.save_games()

# =========================================================
# 🖥️ RYUJINX GUI
# =========================================================
class RyujinxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RyujinxNX Simulator 0.0.1")
        self.root.geometry("1200x800")
        self.colors = {
            "bg": "#1a1a1a", "fg": "#ffffff", "accent": "#6d4cff",
            "list": "#2d2d2d", "header": "#141414", "hover": "#3d3d3d"
        }
        self.root.configure(bg=self.colors["bg"])
        self.emu = RyujinxEmulator()
        self.lib = GameLibrary()
        self.selected_game = None
        self.settings = self.load_settings()
        self._setup_style()
        self._layout()
        self._status("Ready - RyujinxNX 0.0.1 initialized")

    def load_settings(self):
        """Load settings from a JSON file."""
        default_settings = {
            "graphics_backend": "OpenGL",
            "vsync": False,
            "fullscreen": False
        }
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    return json.load(f)
        except json.JSONDecodeError:
            pass
        return default_settings

    def save_settings(self):
        """Save settings to a JSON file."""
        with open("settings.json", "w") as f:
            json.dump(self.settings, f, indent=4)

    def _setup_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview", background=self.colors["list"], fieldbackground=self.colors["list"],
                    foreground=self.colors["fg"], rowheight=28, borderwidth=0)
        s.map("Treeview", background=[('selected', self.colors["accent"])])
        s.configure("Accent.TButton", background=self.colors["accent"], foreground="white")
        s.map("Accent.TButton", background=[('active', "#4a3d99")])

    def _layout(self):
        container = tk.Frame(self.root, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True)
        sidebar = tk.Frame(container, bg=self.colors["header"], width=180)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        content = tk.Frame(container, bg=self.colors["bg"])
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(sidebar, text="RyujinxNX 0.0.1", font=("Segoe UI", 18, "bold"),
                 bg=self.colors["header"], fg=self.colors["accent"]).pack(pady=20)
        for text, cmd in [("🎮 Games", self._tab_games),
                          ("⚙️ Settings", self._tab_settings),
                          ("📊 Logs", self._tab_logs)]:
            b = tk.Button(sidebar, text=text, anchor="w", bg=self.colors["header"], fg=self.colors["fg"],
                          relief=tk.FLAT, padx=20, pady=10, command=cmd)
            b.pack(fill=tk.X)
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg=self.colors["hover"]))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=self.colors["header"]))
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.games_tab = self._create_games_tab()
        self.settings_tab = self._create_settings_tab()
        self.logs_tab = self._create_logs_tab()
        self.notebook.add(self.games_tab, text="Games")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.logs_tab, text="Logs")
        self._status_bar()

    def _status_bar(self):
        bar = tk.Frame(self.root, bg=self.colors["header"], height=25)
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status = tk.StringVar(value="Ready")
        tk.Label(bar, textvariable=self.status, bg=self.colors["header"], fg=self.colors["fg"],
                 font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=10)
        self.fps = tk.Label(bar, text="FPS: --", bg=self.colors["header"], fg=self.colors["fg"])
        self.fps.pack(side=tk.RIGHT, padx=5)
        self.cpu = tk.Label(bar, text="CPU: --%", bg=self.colors["header"], fg=self.colors["fg"])
        self.cpu.pack(side=tk.RIGHT, padx=5)
        self._update_perf()

    def _update_perf(self):
        if not self.root.winfo_exists():
            return
        if self.emu.is_running:
            with self.emu._lock:
                s = self.emu.performance_stats
                self.fps.config(text=f"FPS: {s['fps']}")
                self.cpu.config(text=f"CPU: {s['cpu_usage']}%")
        else:
            self.fps.config(text="FPS: --")
            self.cpu.config(text="CPU: --%")
        self.root.after(1000, self._update_perf)

    def _status(self, msg):
        self.status.set(msg)
        if self.root.winfo_exists():
            self.root.update_idletasks()

    def _create_games_tab(self):
        f = tk.Frame(self.notebook, bg=self.colors["bg"])
        toolbar = tk.Frame(f, bg=self.colors["header"])
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text="Add Game", style="Accent.TButton",
                   command=self._add_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Remove Game", style="Accent.TButton",
                   command=self._remove_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Start", command=self._start_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Stop", command=self._stop_game).pack(side=tk.LEFT, padx=5)
        cols = ("title", "developer", "version", "size", "last_played")
        self.tree = ttk.Treeview(f, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._select_game)
        self.tree.bind("<Double-1>", lambda e: self._start_game())
        self._refresh_games()
        return f

    def _refresh_games(self):
        selected = self.tree.selection()
        selected_title = self.selected_game["title"] if self.selected_game else None
        for i in self.tree.get_children():
            self.tree.delete(i)
        for g in self.lib.games:
            self.tree.insert("", "end", iid=g["title"], values=(
                f"{g['icon']} {g['title']}", g["developer"], g["version"], g["size"], g["last_played"]))
        if selected_title:
            for g in self.lib.games:
                if g["title"] == selected_title:
                    self.tree.selection_set(g["title"])
                    self.selected_game = g
                    break

    def _add_game(self):
        p = filedialog.askopenfilename(filetypes=[("Nintendo Switch Games", "*.nsp *.xci")])
        if p:
            try:
                g = self.lib.add_game(p)
                self._refresh_games()
                self._status(f"Added {g['title']}")
                self._log(f"Added game: {g['title']}")
            except (ValueError, FileNotFoundError) as e:
                messagebox.showerror("Error", str(e))

    def _remove_game(self):
        if not self.selected_game:
            messagebox.showwarning("No Game", "Please select a game to remove.")
            return
        if messagebox.askyesno("Confirm", f"Remove {self.selected_game['title']} from library?"):
            self.lib.remove_game(self.selected_game["title"])
            self.selected_game = None
            self._refresh_games()
            self._status("Game removed")
            self._log(f"Removed game: {self.selected_game['title']}")

    def _select_game(self, _):
        s = self.tree.selection()
        if s:
            t = s[0]
            self.selected_game = next((g for g in self.lib.games if g["title"] == t), None)
            self._status(f"Selected {t}")

    def _start_game(self):
        if not self.selected_game:
            messagebox.showwarning("No Game", "Please select a game.")
            return
        if not self.selected_game["path"]:
            messagebox.showerror("Error", "No valid game file path for this game.")
            return
        try:
            self.emu.start_emulation(self.selected_game["path"])
            self._status(f"Running {self.selected_game['title']}")
            self._log(f"Started {self.selected_game['title']}")
            self._show_emu_window()
            # Update last_played
            self.selected_game["last_played"] = datetime.now().strftime("%Y-%m-%d")
            self.lib.save_games()
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))

    def _stop_game(self):
        if self.emu.is_running:
            self.emu.stop_emulation()
            self._status("Stopped emulation")
            self._log("Emulation stopped")

    def _show_emu_window(self):
        w = tk.Toplevel(self.root)
        w.title(f"RyujinxNX - {self.selected_game['title']}")
        w.geometry("900x500")
        w.configure(bg="black")
        tk.Label(w, text=f"🎮 {self.selected_game['title']} running...",
                 fg="white", bg="black", font=("Segoe UI", 14)).pack(pady=20)
        ttk.Button(w, text="Stop", command=lambda: [self._stop_game(), w.destroy()],
                   style="Accent.TButton").pack(pady=10)

    def _create_settings_tab(self):
        f = tk.Frame(self.notebook, bg=self.colors["bg"])
        ttk.Label(f, text="Graphics Backend:", foreground=self.colors["fg"], background=self.colors["bg"]).pack(anchor="w", pady=5, padx=10)
        graphics_var = tk.StringVar(value=self.settings["graphics_backend"])
        ttk.Combobox(f, textvariable=graphics_var, values=["OpenGL", "Vulkan", "Software"], state="readonly").pack(padx=10, anchor="w")
        ttk.Checkbutton(f, text="Enable VSync", variable=tk.BooleanVar(value=self.settings["vsync"]),
                        command=lambda: self._update_setting("vsync", not self.settings["vsync"])).pack(anchor="w", padx=10, pady=5)
        ttk.Checkbutton(f, text="Fullscreen Mode", variable=tk.BooleanVar(value=self.settings["fullscreen"]),
                        command=lambda: self._update_setting("fullscreen", not self.settings["fullscreen"])).pack(anchor="w", padx=10)
        ttk.Button(f, text="Save Settings", style="Accent.TButton", command=self.save_settings).pack(anchor="w", padx=10, pady=10)
        graphics_var.trace("w", lambda *args: self._update_setting("graphics_backend", graphics_var.get()))
        return f

    def _update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()
        self._log(f"Updated setting: {key} = {value}")

    def _create_logs_tab(self):
        f = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.log_box = scrolledtext.ScrolledText(f, bg=self.colors["list"], fg=self.colors["fg"], wrap=tk.WORD, state="disabled")
        self.log_box.pack(fill=tk.BOTH, expand=True)
        return f

    def _log(self, msg):
        if self.root.winfo_exists():
            self.log_box.configure(state="normal")
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_box.insert(tk.END, f"[{t}] {msg}\n")
            self.log_box.see(tk.END)
            self.log_box.configure(state="disabled")

    def _tab_games(self):
        self.notebook.select(self.games_tab)

    def _tab_settings(self):
        self.notebook.select(self.settings_tab)

    def _tab_logs(self):
        self.notebook.select(self.logs_tab)

# =========================================================
# 🚀 MAIN ENTRY
# =========================================================
def main():
    root = tk.Tk()
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except (ImportError, AttributeError):
            pass  # Silently ignore DPI awareness errors
    if not os.path.exists("games"):
        os.makedirs("games")
    app = RyujinxGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.save_settings(), root.destroy()])
    root.mainloop()

if __name__ == "__main__":
    main()
