#!/usr/bin/env python3
"""
FlamesNX - Nintendo Switch Homebrew Launcher
Ryujinx-inspired interface for homebrew applications only
(C) Flames Co. Softworks Copyright <2025>

MIT License - Homebrew Edition
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import platform
import os
import importlib

class FlamesNX_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FlamesNX - Switch Homebrew Launcher")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Ryujinx-inspired color scheme (dark theme)
        self.bg_color = "#2c2c3e"
        self.fg_color = "#f0f0f0"
        self.accent_color = "#7b4fff"  # Ryujinx purple
        self.list_bg = "#3a3a50"
        self.hover_color = "#4a4a60"
        self.header_bg = "#1e1e2c"
        
        self.root.configure(bg=self.bg_color)
        
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
        
    def setup_styles(self):
        """Setup ttk styles for Ryujinx-like appearance"""
        style = ttk.Style()
        style.theme_use('clam')

        # General style configurations
        style.configure('.', background=self.bg_color, foreground=self.fg_color, fieldbackground=self.list_bg, borderwidth=0)
        
        # Treeview style
        style.configure("Treeview", 
                        background=self.list_bg, 
                        foreground=self.fg_color, 
                        fieldbackground=self.list_bg,
                        rowheight=25)
        style.map("Treeview", background=[('selected', self.accent_color)])
        style.configure("Treeview.Heading", 
                        background=self.header_bg, 
                        foreground=self.fg_color, 
                        relief="flat",
                        font=('Segoe UI', 9, 'bold'))
        style.map("Treeview.Heading", background=[('active', self.hover_color)])

        # Scrollbar style
        style.configure("Vertical.TScrollbar", background=self.list_bg, troughcolor=self.bg_color, bordercolor=self.bg_color, arrowcolor=self.fg_color)
        style.map("Vertical.TScrollbar", background=[('active', self.hover_color)])

        # Notebook style
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.bg_color, foreground=self.fg_color, padding=[10, 5], borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', self.accent_color)])

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_ui(self):
        """Create Ryujinx-like UI"""
        self.create_toolbar()
        
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_game_list(main_frame)
        
        self.create_status_bar()
        
    def create_toolbar(self):
        """Create top toolbar with Ryujinx-like design"""
        toolbar = tk.Frame(self.root, bg=self.header_bg, height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        # Logo
        logo_label = tk.Label(
            toolbar,
            text="FlamesNX",
            font=("Segoe UI", 16, "bold"),
            bg=self.header_bg,
            fg=self.accent_color
        )
        logo_label.pack(side=tk.LEFT, padx=20)
        
        # Action buttons
        button_frame = tk.Frame(toolbar, bg=self.header_bg)
        button_frame.pack(side=tk.RIGHT, padx=20)
        
        add_btn = tk.Button(
            button_frame, text="Add Homebrew", font=("Segoe UI", 9), bg=self.accent_color,
            fg="white", relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.add_homebrew
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        settings_btn = tk.Button(
            button_frame, text="Settings", font=("Segoe UI", 9), bg=self.list_bg,
            fg=self.fg_color, relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.open_settings
        )
        settings_btn.pack(side=tk.LEFT, padx=5)
        
    def create_game_list(self, parent):
        """Create a list view for homebrew apps like Ryujinx"""
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
            app_instance = app_class(self.root, self.bg_color, self.fg_color, self.list_bg, self.accent_color, self.header_bg)
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
        status_bar = tk.Frame(self.root, bg=self.header_bg, height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready - Homebrew Only Mode")
        status_label = tk.Label(
            status_bar, textvariable=self.status_var, font=("Segoe UI", 8),
            bg=self.header_bg, fg=self.fg_color
        )
        status_label.pack(side=tk.LEFT, padx=10)
        
        version_label = tk.Label(
            status_bar, text="v1.0a", font=("Segoe UI", 8),
            bg=self.header_bg, fg=self.fg_color
        )
        version_label.pack(side=tk.RIGHT, padx=10)
        
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

