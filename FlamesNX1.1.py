#!/usr/bin/env python3
"""
EmuNX 1.x — Ryujinx-Inspired Tkinter GUI Edition
------------------------------------------------
A Samsoft Production ©2025
No dependencies beyond Python's built-in tkinter.
Displays a safe introspection snapshot (sys.*) in a GUI mimicking Ryujinx's dark-themed sidebar layout.
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Listbox
import platform as _platform_mod
import io
import json
from types import FrameType
from typing import Any, Dict, List

APP_NAME = "EmuNX"
APP_VERSION = "1.x"

def _callable_name(obj: Any) -> str:
    try:
        if hasattr(obj, "__qualname__"):
            qn = getattr(obj, "__qualname__", None) or ""
            mod = getattr(obj, "__module__", None) or ""
            if mod:
                return f"{mod}.{qn}"
            return qn or repr(obj)
        return repr(obj)
    except Exception:
        return repr(obj)

def _flags_as_dict(flags: Any) -> Dict[str, Any]:
    names = [
        "debug", "inspect", "interactive", "optimize", "dont_write_bytecode",
        "no_user_site", "no_site", "ignore_environment", "verbose",
        "bytes_warning", "quiet", "hash_randomization", "isolated",
        "dev_mode", "utf8_mode", "warn_default_encoding", "safe_path",
        "int_max_str_digits",
    ]
    out: Dict[str, Any] = {}
    for n in names:
        if hasattr(flags, n):
            try:
                out[n] = getattr(flags, n)
            except Exception:
                pass
    return out

def _stream_info(s: Any) -> Dict[str, Any]:
    d: Dict[str, Any] = {"type": type(s).__name__}
    for attr in ("encoding", "errors", "closed"):
        if hasattr(s, attr):
            try:
                d[attr] = getattr(s, attr)
            except Exception:
                d[attr] = None
    for m in ("isatty", "readable", "writable"):
        if hasattr(s, m):
            try:
                d[m] = getattr(s, m)()
            except Exception:
                d[m] = None
    return d

def _impl_info() -> Dict[str, Any]:
    impl = getattr(sys, "implementation", None)
    if impl is None:
        return {}
    out: Dict[str, Any] = {}
    for n in ("name", "hexversion", "cache_tag"):
        if hasattr(impl, n):
            out[n] = getattr(impl, n)
    if hasattr(impl, "version"):
        ver = getattr(impl, "version")
        try:
            out["version"] = {
                "major": getattr(ver, "major", None),
                "minor": getattr(ver, "minor", None),
                "micro": getattr(ver, "micro", None),
                "releaselevel": getattr(ver, "releaselevel", None),
                "serial": getattr(ver, "serial", None),
            }
        except Exception:
            out["version"] = str(ver)
    return out

def _float_info() -> Dict[str, Any]:
    fi = getattr(sys, "float_info", None)
    if fi is None:
        return {}
    names = ["max", "max_exp", "max_10_exp", "min", "min_exp", "min_10_exp", "dig", "mant_dig", "epsilon", "radix", "rounds"]
    out = {n: getattr(fi, n, None) for n in names}
    return out

def _hash_info() -> Dict[str, Any]:
    hi = getattr(sys, "hash_info", None)
    if hi is None:
        return {}
    names = ["width", "modulus", "inf", "nan", "imag", "algorithm", "hash_bits", "seed_bits", "cutoff"]
    out = {n: getattr(hi, n, None) for n in names}
    return out

def _int_info() -> Dict[str, Any]:
    ii = getattr(sys, "int_info", None)
    if ii is None:
        return {}
    names = ["bits_per_digit", "sizeof_digit", "default_max_str_digits", "str_digits_check_threshold"]
    out = {n: getattr(ii, n, None) for n in names}
    return out

def _thread_info() -> Dict[str, Any]:
    ti = getattr(sys, "thread_info", None)
    if ti is None:
        return {}
    names = ["name", "lock", "version"]
    out = {n: getattr(ti, n, None) for n in names}
    return out

def _try_call(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

def snapshot() -> Dict[str, Any]:
    """Collect a safe snapshot of interpreter/sys state."""
    modules_list = list(sys.modules.keys())[:50]
    meta_path = [type(f).__name__ for f in getattr(sys, "meta_path", [])]
    path_hooks = [_callable_name(h) for h in getattr(sys, "path_hooks", [])]
    streams = {
        "stdin": _stream_info(sys.stdin),
        "stdout": _stream_info(sys.stdout),
        "stderr": _stream_info(sys.stderr),
    }
    last_exc = None
    if hasattr(sys, "last_exc"):
        try:
            last_exc = f"{type(sys.last_exc).__name__}: {sys.last_exc}"
        except Exception:
            last_exc = str(getattr(sys, "last_exc", None))
    info: Dict[str, Any] = {
        "python": {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
                "releaselevel": sys.version_info.releaselevel,
                "serial": sys.version_info.serial,
            },
            "hexversion": sys.hexversion,
            "api_version": getattr(sys, "api_version", None),
            "implementation": _impl_info(),
            "executable": sys.executable,
            "platform": sys.platform,
            "platform_uname": dict(
                system=_platform_mod.system(),
                release=_platform_mod.release(),
                version=_platform_mod.version(),
                machine=_platform_mod.machine(),
                processor=_platform_mod.processor(),
            ),
            "byteorder": sys.byteorder,
            "maxsize": sys.maxsize,
            "maxunicode": sys.maxunicode,
            "float_info": _float_info(),
            "hash_info": _hash_info(),
            "int_info": _int_info(),
            "thread_info": _thread_info(),
        },
        "sys_paths": {
            "prefix": getattr(sys, "prefix", None),
            "base_prefix": getattr(sys, "base_prefix", None),
            "exec_prefix": getattr(sys, "exec_prefix", None),
            "base_exec_prefix": getattr(sys, "base_exec_prefix", None),
            "platlibdir": getattr(sys, "platlibdir", None),
            "pycache_prefix": getattr(sys, "pycache_prefix", None),
            "path": list(sys.path),
        },
        "argv": list(sys.argv),
        "builtins": list(getattr(sys, "builtin_module_names", [])),
        "stdout_stderr_stdin": streams,
        "encodings": {
            "default": _try_call(sys.getdefaultencoding),
            "filesystem": _try_call(sys.getfilesystemencoding),
            "filesystem_errors": _try_call(getattr, sys, "getfilesystemencodeerrors"),
        },
        "limits": {
            "recursion_limit": _try_call(sys.getrecursionlimit),
            "switch_interval": _try_call(sys.getswitchinterval),
            "int_max_str_digits": getattr(sys.flags, "int_max_str_digits", None),
        },
        "import_system": {
            "meta_path": meta_path,
            "path_hooks": path_hooks,
        },
        "flags": _flags_as_dict(sys.flags),
        "warnoptions": getattr(sys, "warnoptions", []),
        "xoptions": dict(getattr(sys, "_xoptions", {})),
        "modules": {
            "count": len(sys.modules),
            "preview": modules_list,
        },
        "last_exception_summary": last_exc,
        "hooks": {
            "displayhook": _callable_name(getattr(sys, "displayhook", None)),
            "excepthook": _callable_name(getattr(sys, "excepthook", None)),
            "unraisablehook": _callable_name(getattr(sys, "unraisablehook", None)),
            "breakpointhook": _callable_name(getattr(sys, "breakpointhook", None)),
        },
    }
    return info

def format_human(snap: Dict[str, Any]) -> str:
    """Format snapshot as human-readable string."""
    output = io.StringIO()
    py = snap.get("python", {})
    sys_paths = snap.get("sys_paths", {})
    enc = snap.get("encodings", {})
    limits = snap.get("limits", {})
    flags = snap.get("flags", {})
    modules = snap.get("modules", {})
    hooks = snap.get("hooks", {})
    streams = snap.get("stdout_stderr_stdin", {})
    imp = snap.get("import_system", {})

    print(f"{APP_NAME} {APP_VERSION}", file=output)
    print("=" * 50, file=output)
    print(f"Python: {py.get('version')}", file=output)
    impl = py.get("implementation", {})
    impl_ver = impl.get("version", {})
    print(f"Implementation: {impl.get('name')} {impl_ver.get('major')}.{impl_ver.get('minor')}.{impl_ver.get('micro')} ({impl.get('cache_tag')})", file=output)
    print(f"Executable: {py.get('executable')}", file=output)
    print(f"Platform: {py.get('platform')} | Byteorder: {py.get('byteorder')} | Max Unicode: {py.get('maxunicode')}", file=output)
    print("\nPaths", file=output)
    print("-" * 20, file=output)
    for i, p in enumerate(sys_paths.get("path", [])[:10]):  # Limit for brevity
        print(f"[{i:02}] {p}", file=output)
    print(f"\nEncodings:", file=output)
    print(f"Default: {enc.get('default')}", file=output)
    print(f"Filesystem: {enc.get('filesystem')}", file=output)
    print(f"\nLimits:", file=output)
    print(f"Recursion: {limits.get('recursion_limit')}", file=output)
    print(f"Switch Interval: {limits.get('switch_interval')}", file=output)
    print("\nFlags", file=output)
    print("-" * 20, file=output)
    for k in sorted(flags):
        print(f"{k}: {flags[k]}", file=output)
    print("\nModules: {modules.get('count')} loaded (preview: {len(modules.get('preview', []))})", file=output)
    print("\nHooks", file=output)
    print("-" * 20, file=output)
    for k, v in hooks.items():
        print(f"{k}: {v}", file=output)
    print("\nStreams", file=output)
    print("-" * 20, file=output)
    for name, info in streams.items():
        print(f"{name}: {info.get('type')}, encoding={info.get('encoding')}, isatty={info.get('isatty')}", file=output)
    return output.getvalue()

class EmuNXGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("900x600")
        self.root.configure(bg="#0f0f0f")
        self.snap = snapshot()
        self.current_frame = None
        self.make_ui()

    def make_ui(self):
        # Style for dark theme like Ryujinx
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#0f0f0f")
        style.configure("TLabel", background="#0f0f0f", foreground="#ffffff")
        style.configure("TButton", background="#2a2a2a", foreground="#ffffff", borderwidth=0)
        style.map("TButton", background=[("active", "#404040")])
        style.configure("Sidebar.TButton", font=("Segoe UI", 10), padding=(10, 5))
        style.configure("Vertical.TScrollbar", background="#2a2a2a", troughcolor="#0f0f0f", borderwidth=0)
        style.configure("Vertical.TScrollbar", arrowcolor="#ffffff")

        # Top bar like Ryujinx header
        top_frame = tk.Frame(self.root, bg="#0f0f0f", height=50)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)
        logo_label = tk.Label(top_frame, text=f"{APP_NAME} {APP_VERSION}", font=("Segoe UI", 16, "bold"), bg="#0f0f0f", fg="#4a90e2")
        logo_label.pack(side="left", padx=15, pady=10)
        # Settings icon/button
        settings_btn = tk.Button(top_frame, text="⚙", font=("Segoe UI", 16), bg="#0f0f0f", fg="#ffffff", relief="flat", command=self.show_settings)
        settings_btn.pack(side="right", padx=15, pady=10)

        # Main container
        main_container = tk.Frame(self.root, bg="#0f0f0f")
        main_container.pack(fill="both", expand=True)

        # Left sidebar like Ryujinx navigation
        sidebar = tk.Frame(main_container, width=200, bg="#1a1a1a")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        nav_items = [
            ("Info", self.show_info),
            ("Paths", self.show_paths),
            ("Modules", self.show_modules),
            ("Flags", self.show_flags),
            ("Streams", self.show_streams),
            ("Hooks", self.show_hooks),
            ("Settings", self.show_settings)
        ]

        for text, command in nav_items:
            btn = ttk.Button(sidebar, text=text, style="Sidebar.TButton", command=command)
            btn.pack(fill="x", pady=2, padx=10)

        # Main content area
        self.content_frame = tk.Frame(main_container, bg="#0f0f0f")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Initial view
        self.show_info()

    def clear_content(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = tk.Frame(self.content_frame, bg="#0f0f0f")
        self.current_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def show_info(self):
        self.clear_content()
        text = scrolledtext.ScrolledText(self.current_frame, bg="#1a1a1a", fg="#ffffff", insertbackground="white", font=("Consolas", 10), wrap=tk.WORD)
        text.pack(fill="both", expand=True)
        text.insert("1.0", format_human(self.snap))
        text.configure(state="disabled")

    def show_paths(self):
        self.clear_content()
        frame = tk.Frame(self.current_frame)
        frame.pack(fill="both", expand=True)
        listbox = Listbox(frame, bg="#1a1a1a", fg="#ffffff", font=("Consolas", 10), selectbackground="#4a90e2")
        listbox.pack(fill="both", expand=True, side="left")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview, style="Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        listbox.configure(yscrollcommand=scrollbar.set)
        for i, p in enumerate(self.snap["sys_paths"]["path"]):
            listbox.insert(tk.END, f"[{i:02d}] {p}")

    def show_modules(self):
        self.clear_content()
        frame = tk.Frame(self.current_frame)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=f"Loaded Modules: {self.snap['modules']['count']} (Preview: {len(self.snap['modules']['preview'])})", 
                  font=("Consolas", 10)).pack(anchor="w")
        listbox = Listbox(frame, bg="#1a1a1a", fg="#ffffff", font=("Consolas", 9), selectbackground="#4a90e2")
        listbox.pack(fill="both", expand=True, pady=(5, 0))
        for m in self.snap["modules"]["preview"]:
            listbox.insert(tk.END, m)

    def show_flags(self):
        self.clear_content()
        text = scrolledtext.ScrolledText(self.current_frame, bg="#1a1a1a", fg="#ffffff", insertbackground="white", font=("Consolas", 10), wrap=tk.WORD)
        text.pack(fill="both", expand=True)
        flags_str = "\n".join([f"{k:>20}: {v}" for k, v in sorted(self.snap["flags"].items())])
        text.insert("1.0", flags_str)
        text.configure(state="disabled")

    def show_streams(self):
        self.clear_content()
        text = scrolledtext.ScrolledText(self.current_frame, bg="#1a1a1a", fg="#ffffff", insertbackground="white", font=("Consolas", 10), wrap=tk.WORD)
        text.pack(fill="both", expand=True)
        streams_str = "\n".join([f"{name}: type={info.get('type')}, encoding={info.get('encoding')}, isatty={info.get('isatty')}"
                                 for name, info in self.snap["stdout_stderr_stdin"].items()])
        text.insert("1.0", streams_str)
        text.configure(state="disabled")

    def show_hooks(self):
        self.clear_content()
        text = scrolledtext.ScrolledText(self.current_frame, bg="#1a1a1a", fg="#ffffff", insertbackground="white", font=("Consolas", 10), wrap=tk.WORD)
        text.pack(fill="both", expand=True)
        hooks_str = "\n".join([f"{k:>16}: {v}" for k, v in self.snap["hooks"].items()])
        text.insert("1.0", hooks_str)
        text.configure(state="disabled")

    def show_settings(self):
        self.clear_content()
        pad_frame = tk.Frame(self.current_frame, bg="#0f0f0f")
        pad_frame.pack(fill="both", expand=True, pady=20)

        # Recursion limit
        rec_frame = tk.LabelFrame(pad_frame, text="Recursion Limit", bg="#1a1a1a", fg="#ffffff", font=("Consolas", 10), padx=10, pady=10)
        rec_frame.pack(fill="x", pady=10)
        tk.Label(rec_frame, text=f"Current: {sys.getrecursionlimit()}", bg="#1a1a1a", fg="#ffffff").pack(anchor="w")
        rec_entry = tk.Entry(rec_frame, bg="#2a2a2a", fg="#ffffff", insertbackground="white", font=("Consolas", 9))
        rec_entry.pack(fill="x", pady=(5, 0))
        rec_entry.insert(0, str(sys.getrecursionlimit()))

        def set_recursion():
            try:
                val = int(rec_entry.get())
                old = sys.getrecursionlimit()
                sys.setrecursionlimit(val)
                messagebox.showinfo("Updated", f"Recursion limit {old} → {val}")
                rec_entry.delete(0, tk.END)
                rec_entry.insert(0, str(val))
            except ValueError:
                messagebox.showerror("Error", "Invalid integer")

        tk.Button(rec_frame, text="Apply", bg="#2a2a2a", fg="#ffffff", relief="flat", command=set_recursion, font=("Consolas", 9)).pack(pady=5)

        # Demo exception
        demo_frame = tk.LabelFrame(pad_frame, text="Demo Exception", bg="#1a1a1a", fg="#ffffff", font=("Consolas", 10), padx=10, pady=10)
        demo_frame.pack(fill="x", pady=10)

        def demo_exception():
            try:
                1 / 0
            except Exception as e:
                etype, evalue, tb = sys.exc_info()
                exc_msg = f"Type: {etype.__name__ if etype else None}\nValue: {evalue}"
                if tb:
                    frames = []
                    while tb and len(frames) < 3:
                        f = tb.tb_frame
                        frames.append(f"{f.f_code.co_filename}:{tb.tb_lineno} in {f.f_code.co_name}")
                        tb = tb.tb_next
                    exc_msg += f"\nFrames:\n" + "\n".join(frames)
                messagebox.showwarning("Caught Exception", exc_msg)

        tk.Button(demo_frame, text="Trigger Demo", bg="#2a2a2a", fg="#ffffff", relief="flat", command=demo_exception, font=("Consolas", 9)).pack(pady=5)

        # Export JSON
        export_frame = tk.LabelFrame(pad_frame, text="Export Snapshot", bg="#1a1a1a", fg="#ffffff", font=("Consolas", 10), padx=10, pady=10)
        export_frame.pack(fill="x", pady=10)

        def export_json():
            try:
                with open("emunx_snapshot.json", "w") as f:
                    json.dump(self.snap, f, indent=2)
                messagebox.showinfo("Exported", "Snapshot saved to emunx_snapshot.json")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

        tk.Button(export_frame, text="Export JSON", bg="#2a2a2a", fg="#ffffff", relief="flat", command=export_json, font=("Consolas", 9)).pack(pady=5)

        # Exit button
        tk.Button(pad_frame, text="Exit", bg="#ff4444", fg="#ffffff", relief="flat", command=self.root.destroy, font=("Consolas", 10)).pack(pady=20)

def main():
    root = tk.Tk()
    app = EmuNXGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
