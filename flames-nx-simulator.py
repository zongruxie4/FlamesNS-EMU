#!/usr/bin/env python3
"""
FlamesNX - Nintendo Switch Homebrew Launcher
Yuzu-inspired interface with theme toggle for homebrew applications only
(C) Flames Co. Softworks Copyright <2025>

MIT License - Homebrew Edition
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import platform
import os
import importlib
import subprocess

# Optional imports for system theme detection
try:
    import winreg
except ImportError:
    winreg = None

class FlamesNX_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FlamesNX - Switch Homebrew Launcher")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Theme settings
        self.theme = "system"
        self.colors_dark = {
            "bg_color": "#212121",
            "fg_color": "#FFFFFF",
            "accent_color": "#4FC3F7",
            "list_bg": "#424242",
            "hover_color": "#616161",
            "header_bg": "#1a1a1a"
        }
        self.colors_light = {
            "bg_color": "#FAFAFA",
            "fg_color": "#212121",
            "accent_color": "#4FC3F7",
            "list_bg": "#FFFFFF",
            "hover_color": "#E0E0E0",
            "header_bg": "#F5F5F5"
        }
        self.colors = self.get_colors()
        self.root.configure(bg=self.colors["bg_color"])
        
        # Homebrew library
        self.homebrew_apps = []
        self.selected_app = None
        
        # Mapping for app simulations
        self.app_modules = {
            "Atmosphere": ("apps.atmosphere", "AtmosphereApp"),
            "Homebrew Menu": ("apps.hb_menu", "HBMenuApp"),
            "Checkpoint": ("apps.checkpoint", "CheckpointApp"),
            "JKSV": ("apps.jksv", "JKSVApp"),
            "GoldLeaf": ("apps.goldleaf", "GoldleafApp"),
            "RetroArch": ("apps.retroarch", "RetroArchApp"),
        }
        
        # Configure styles
        self.setup_styles()
        
        # Create UI
        self.create_ui()
        
        # Load default homebrew apps
        self.load_default_homebrew()
        
        # Center window
        self.center_window()
        
    def detect_system_theme(self):
        """Detect OS system theme"""
        sys_platform = platform.system()
        if sys_platform == "Windows" and winreg:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return "light" if value == 1 else "dark"
            except:
                return "dark"
        elif sys_platform == "Darwin":  # macOS
            try:
                result = subprocess.run(["defaults", "read", "-g", "AppleInterfaceStyle"], capture_output=True, text=True)
                return "dark" if "Dark" in result.stdout.strip() else "light"
            except:
                return "light"
        else:
            # Linux/other: default to dark
            return "dark"
    
    def get_colors(self):
        """Get colors based on current theme"""
        if self.theme == "system":
            sys_theme = self.detect_system_theme()
            return self.colors_dark if sys_theme == "dark" else self.colors_light
        elif self.theme == "dark":
            return self.colors_dark
        else:
            return self.colors_light
    
    def apply_theme(self):
        """Apply current theme to all UI elements"""
        self.colors = self.get_colors()
        self.root.configure(bg=self.colors["bg_color"])
        
        # Update toolbar and elements
        self.toolbar.configure(bg=self.colors["header_bg"])
        self.logo_label.configure(fg=self.colors["accent_color"])
        self.button_frame.configure(bg=self.colors["header_bg"])
        
        # Update buttons
        accent_fg = "white" if self.colors["bg_color"] == self.colors_dark["bg_color"] else self.colors["fg_color"]
        self.add_btn.configure(
            bg=self.colors["accent_color"],
            fg=accent_fg
        )
        self.settings_btn.configure(
            bg=self.colors["list_bg"],
            fg=self.colors["fg_color"]
        )
        
        # Update theme combo (ttk, handled by style)
        
        # Update main frame
        self.main_frame.configure(bg=self.colors["bg_color"])
        
        # Update status bar
        self.status_bar.configure(bg=self.colors["header_bg"])
        self.status_label.configure(
            bg=self.colors["header_bg"],
            fg=self.colors["fg_color"]
        )
        self.version_label.configure(
            bg=self.colors["header_bg"],
            fg=self.colors["fg_color"]
        )
        
        # Recreate styles for ttk elements
        self.setup_styles()
        
        # Update status
        self.update_status(f"Theme switched to {self.theme.capitalize()}")
        
    def on_theme_change(self, event):
        """Handle theme selection change"""
        new_theme = self.theme_var.get().lower()
        if new_theme != self.theme:
            self.theme = new_theme
            self.apply_theme()
    
    def setup_styles(self):
        """Setup ttk styles for Yuzu-like appearance"""
        style = ttk.Style()
        style.theme_use('clam')

        # General style configurations
        style.configure('.', background=self.colors["bg_color"], foreground=self.colors["fg_color"], fieldbackground=self.colors["list_bg"], borderwidth=0)
        
        # Treeview style
        style.configure("Treeview", 
                        background=self.colors["list_bg"], 
                        foreground=self.colors["fg_color"], 
                        fieldbackground=self.colors["list_bg"],
                        rowheight=25)
        style.map("Treeview", background=[('selected', self.colors["accent_color"])])
        style.configure("Treeview.Heading", 
                        background=self.colors["header_bg"], 
                        foreground=self.colors["fg_color"], 
                        relief="flat",
                        font=('Segoe UI', 9, 'bold'))
        style.map("Treeview.Heading", background=[('active', self.colors["hover_color"])])

        # Scrollbar style
        style.configure("Vertical.TScrollbar", background=self.colors["list_bg"], troughcolor=self.colors["bg_color"], bordercolor=self.colors["bg_color"], arrowcolor=self.colors["fg_color"])
        style.map("Vertical.TScrollbar", background=[('active', self.colors["hover_color"])])

        # Notebook style (unused but prepared)
        style.configure('TNotebook', background=self.colors["bg_color"], borderwidth=0)
        style.configure('TNotebook.Tab', background=self.colors["bg_color"], foreground=self.colors["fg_color"], padding=[10, 5], borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', self.colors["accent_color"])])

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        """Create Yuzu-like UI"""
        self.create_toolbar()
        
        self.main_frame = tk.Frame(self.root, bg=self.colors["bg_color"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_game_list(self.main_frame)
        
        self.create_status_bar()
        
    def create_toolbar(self):
        """Create top toolbar with Yuzu-like design and theme toggle"""
        self.toolbar = tk.Frame(self.root, bg=self.colors["header_bg"], height=50)
        self.toolbar.pack(fill=tk.X)
        self.toolbar.pack_propagate(False)
        
        # Logo
        self.logo_label = tk.Label(
            self.toolbar,
            text="FlamesNX",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors["header_bg"],
            fg=self.colors["accent_color"]
        )
        self.logo_label.pack(side=tk.LEFT, padx=20)
        
        # Action buttons frame
        self.button_frame = tk.Frame(self.toolbar, bg=self.colors["header_bg"])
        self.button_frame.pack(side=tk.RIGHT, padx=20)
        
        self.add_btn = tk.Button(
            self.button_frame, text="Add Homebrew", font=("Segoe UI", 9), 
            bg=self.colors["accent_color"], fg="white",
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.add_homebrew
        )
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.settings_btn = tk.Button(
            self.button_frame, text="Settings", font=("Segoe UI", 9), 
            bg=self.colors["list_bg"], fg=self.colors["fg_color"],
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.open_settings
        )
        self.settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Theme toggle combobox
        self.theme_var = tk.StringVar(value=self.theme.capitalize())
        self.theme_combo = ttk.Combobox(
            self.button_frame, textvariable=self.theme_var, 
            values=["Dark", "Light", "System"], 
            state="readonly", width=8
        )
        self.theme_combo.pack(side=tk.LEFT, padx=5)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
        
    def create_game_list(self, parent):
        """Create a list view for homebrew apps like Yuzu"""
        columns = ('name', 'author', 'version', 'size')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings')

        # Define headings
        self.tree.heading('name', text='Name')
        self.tree.heading('author', text='Author')
        self.tree.heading('version', text='Version')
        self.tree.heading('size', text='Size')
        
        # Define column widths
        self.tree.column('name', width=250)
        self.tree.column('author', width=150)
        self.tree.column('version', width=100, anchor='center')
        self.tree.column('size', width=100, anchor='center')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_app_select)
        self.tree.bind('<Double-1>', self.launch_selected_homebrew)

    def load_default_homebrew(self):
        """Load default homebrew applications"""
        default_apps = [
            {"name": "Atmosphere", "icon": "🚀", "type": "CFW", "version": "1.5.5", "size": "45 MB", "author": "SciresM"},
            {"name": "Homebrew Menu", "icon": "📱", "type": "Launcher", "version": "3.6.0", "size": "2.8 MB", "author": "DevkitPro"},
            {"name": "Checkpoint", "icon": "💾", "type": "Save Manager", "version": "3.7.4", "size": "5.2 MB", "author": "BernardoGiordano"},
            {"name": "JKSV", "icon": "🗂️", "type": "Save Tool", "version": "2023.10", "size": "3.1 MB", "author": "JK"},
            {"name": "GoldLeaf", "icon": "🍁", "type": "File Manager", "version": "0.10", "size": "8.5 MB", "author": "XorTroll"},
            {"name": "RetroArch", "icon": "🎮", "type": "Emulator", "version": "1.16.0", "size": "125 MB", "author": "LibRetro"},
        ]
        self.homebrew_apps = default_apps
        self.refresh_list()
        
    def refresh_list(self):
        """Refresh the homebrew list display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add new items
        for app in self.homebrew_apps:
            values = (
                f"{app.get('icon', '📦')} {app.get('name', 'Unknown')}",
                app.get('author', 'N/A'),
                app.get('version', 'N/A'),
                app.get('size', 'N/A')
            )
            self.tree.insert('', tk.END, values=values, iid=app['name'])
        
        self.update_status(f"Loaded {len(self.homebrew_apps)} homebrew applications")

    def on_app_select(self, event):
        """Handle app selection in the list"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        selected_id = selected_items[0]
        app_data = next((app for app in self.homebrew_apps if app['name'] == selected_id), None)
        
        if app_data:
            self.selected_app = app_data
            self.update_status(f"Selected: {app_data['name']} v{app_data['version']}")

    def launch_selected_homebrew(self, event):
        """Launch the app selected in the list on double click"""
        if self.selected_app:
            self.launch_homebrew(self.selected_app)

    def launch_homebrew(self, app_data):
        """Launch selected homebrew application simulation"""
        app_name = app_data.get("name")
        if app_name not in self.app_modules:
            messagebox.showwarning(
                "Simulation Not Available",
                f"A simulation for '{app_name}' has not been created yet."
            )
            return

        module_name, class_name = self.app_modules[app_name]

        try:
            self.update_status(f"Launching {app_name}...")
            
            # Dynamically import the module
            app_module = importlib.import_module(module_name)
            
            # Get the class from the module
            app_class = getattr(app_module, class_name)
            
            # Instantiate and run the app simulation
            # Pass colors to maintain the theme
            app_instance = app_class(self.root, self.colors["bg_color"], self.colors["fg_color"], self.colors["list_bg"], self.colors["accent_color"], self.colors["header_bg"])
            app_instance.run()

            self.root.after(500, lambda: self.update_status(f"{app_name} is running"))

        except ImportError:
            messagebox.showerror("Error", f"Could not find the module for '{app_name}'. Make sure 'apps/{module_name.split('.')[1]}.py' exists.")
        except AttributeError:
            messagebox.showerror("Error", f"Could not find the class '{class_name}' in the module for '{app_name}'.")
        except Exception as e:
            messagebox.showerror("Launch Error", f"An error occurred while launching {app_name}:\n{e}")
            
    def add_homebrew(self):
        """Dialog to add a new homebrew application"""
        messagebox.showinfo("Add Homebrew", "This feature is coming soon in a future update!")

    def open_settings(self):
        """Open settings window"""
        messagebox.showinfo("Settings", "This feature is coming soon in a future update!")
        
    def create_status_bar(self):
        """Create status bar at bottom"""
        self.status_bar = tk.Frame(self.root, bg=self.colors["header_bg"], height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready - Homebrew Only Mode")
        self.status_label = tk.Label(
            self.status_bar, textvariable=self.status_var, font=("Segoe UI", 8),
            bg=self.colors["header_bg"], fg=self.colors["fg_color"]
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.version_label = tk.Label(
            self.status_bar, text="v1.0a", font=("Segoe UI", 8),
            bg=self.colors["header_bg"], fg=self.colors["fg_color"]
        )
        self.version_label.pack(side=tk.RIGHT, padx=10)
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Create apps directory if it doesn't exist to avoid import errors
    if not os.path.exists('apps'):
        os.makedirs('apps')
    
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass # Fails on non-Windows or if library is missing
    
    app = FlamesNX_GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
