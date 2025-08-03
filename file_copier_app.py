import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import threading
import queue
import time
import json
import sys
import psutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    print("tkinterdnd2 not available, using click-to-select instead")
    DND_FILES = None
    TkinterDnD = None

# Enhanced drag & drop functionality with tkinterdnd2

# Enhanced theme configurations
THEMES = {
    "dark_blue": {"mode": "dark", "color": "blue"},
    "dark_green": {"mode": "dark", "color": "green"},
    "dark_red": {"mode": "dark", "color": "dark-blue"},
    "light_blue": {"mode": "light", "color": "blue"},
    "light_green": {"mode": "light", "color": "green"},
    "cyberpunk": {"mode": "dark", "color": "blue"},
    "sunset": {"mode": "dark", "color": "green"},
    "ocean": {"mode": "light", "color": "blue"},
    "forest": {"mode": "dark", "color": "green"},
    "system": {"mode": "system", "color": "blue"}
}

# Set initial appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FileCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مدیریت فایل ایرانی پیشرفته - Persian File Copier Pro")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
        # Initialize variables
        self.copy_tasks = []
        self.task_queue = queue.Queue()
        self.executor = None
        self.is_copying = False
        self.clipboard_files = []
        self.current_dir = os.getcwd()
        self.settings = self.load_settings()
        self.file_cache = self.load_cache()
        
        # Setup components
        self.setup_logging()
        self.setup_executor()
        self.setup_gui()
        self.setup_bindings()
        
        # Initial display
        self.display_cache()
        self.update_status("Ready")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename="copy_log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8"
        )
        self.logger = logging.getLogger(__name__)

    def setup_executor(self):
        """Initialize thread pool executor with optimized settings"""
        # Calculate optimal number of threads based on CPU cores
        import os
        cpu_count = os.cpu_count() or 4
        optimal_threads = min(max(cpu_count, 2), 8)  # Between 2 and 8 threads
        
        max_workers = self.settings.get("max_threads", optimal_threads)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def load_settings(self) -> Dict:
        """Load application settings from file"""
        default_settings = {
            "theme": "dark_blue",
            "buffer_size": 64 * 1024,  # 64KB default
            "max_threads": 4,
            "overwrite_policy": "prompt",
            "window_geometry": "1100x700",
            "verify_copy": True,
            "show_hidden_files": False,
            "auto_retry": True,
            "retry_count": 3,
            "progress_update_interval": 0.5,
            "use_compression": False,
            "preserve_permissions": True,
            "create_backup": False,
            "notification_sound": True,
            "minimize_to_tray": False,
            "auto_clear_completed": False,
            "show_speed_graph": True,
            "language": "en"
        }
        
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                # Merge with defaults
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            return default_settings

    def save_settings(self):
        """Save current settings to file"""
        try:
            self.settings["window_geometry"] = self.root.geometry()
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")

    def load_cache(self) -> Dict:
        """Load file cache from disk"""
        try:
            with open("file_cache.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"files": {}, "last_scan": 0}

    def save_cache(self):
        """Save file cache to disk"""
        try:
            with open("file_cache.json", "w", encoding="utf-8") as f:
                json.dump(self.file_cache, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")

    def setup_gui(self):
        """Setup the main GUI"""
        # Apply theme
        theme_config = THEMES.get(self.settings["theme"], THEMES["dark_blue"])
        ctk.set_appearance_mode(theme_config["mode"])
        ctk.set_default_color_theme(theme_config["color"])
        
        # Configure window
        self.root.configure(fg_color=("gray95", "gray10"))
        
        # Set default font for the entire application
        try:
            # Try to use B Nazanin font
            default_font = ctk.CTkFont(family="B Nazanin", size=12)
            self.default_font = default_font
        except:
            # Fallback to system default if B Nazanin is not available
            default_font = ctk.CTkFont(size=12)
            self.default_font = default_font
            print("B Nazanin font not found, using system default")
        
        # Main container with gradient effect
        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=15,
            fg_color=("white", "gray15"),
            border_width=2,
            border_color=("gray70", "gray25")
        )
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Create notebook for tabs with custom styling
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Configure tab colors with simplified approach
        try:
            style = ttk.Style()
            
            # Try to configure basic styling - use valid color names
            style.configure("TNotebook", 
                          background="#f0f0f0",
                          borderwidth=0)
            style.configure("TNotebook.Tab",
                          padding=[15, 8],
                          font=('TkDefaultFont', 10, 'bold'))
            
            print("✓ Basic tab styling applied")
        except Exception as e:
            print(f"Could not configure tab styling: {e}")
        
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # تب مرورگر فایل - تم آبی
        self.explorer_frame = ctk.CTkFrame(self.notebook, fg_color=("#e3f2fd", "#1a237e"))
        self.notebook.add(self.explorer_frame, text="📁 مرورگر فایل")
        self.setup_explorer_tab()
        
        # تب کارهای کپی - تم سبز
        self.tasks_frame = ctk.CTkFrame(self.notebook, fg_color=("#e0f2f1", "#1b5e20"))
        self.notebook.add(self.tasks_frame, text="📋 کارهای کپی")
        self.setup_tasks_tab()
        
        # تب کپی سریع - تم صورتی
        self.dragdrop_frame = ctk.CTkFrame(self.notebook, fg_color=("#fce4ec", "#880e4f"))
        self.notebook.add(self.dragdrop_frame, text="🎯 کپی سریع")
        self.setup_dragdrop_tab()
        
        # تب تنظیمات - تم نارنجی
        self.settings_frame = ctk.CTkFrame(self.notebook, fg_color=("#fff3e0", "#e65100"))
        self.notebook.add(self.settings_frame, text="⚙️ تنظیمات")
        self.setup_settings_tab()
        
        # Tab colors are now implemented through frame colors
        print("✓ Tab colors implemented through frame backgrounds")
        
        # Status bar
        self.setup_status_bar()

    def setup_dragdrop_tab(self):
        """Setup the drag & drop quick copy tab"""
        # Title and instructions
        title_frame = ctk.CTkFrame(self.dragdrop_frame)
        title_frame.pack(fill="x", padx=20, pady=20)
        
        try:
            title_font = ctk.CTkFont(family="B Nazanin", size=24, weight="bold")
        except:
            title_font = ctk.CTkFont(size=24, weight="bold")
            
        title_label = ctk.CTkLabel(
            title_frame,
            text="🚀 کپی سریع - بکشید و رها کنید",
            font=title_font
        )
        title_label.pack(pady=10)
        
        try:
            instruction_font = ctk.CTkFont(family="B Nazanin", size=14)
        except:
            instruction_font = ctk.CTkFont(size=14)
            
        instruction_label = ctk.CTkLabel(
            title_frame,
            text="فایل‌ها را از Explorer بکشید و روی پوشه‌های مقصد رها کنید\nاگر کار نکرد، روی پوشه‌ها کلیک کنید تا فایل انتخاب کنید",
            font=instruction_font,
            wraplength=600
        )
        instruction_label.pack(pady=5)
        
        # Destination folders management
        dest_mgmt_frame = ctk.CTkFrame(self.dragdrop_frame)
        dest_mgmt_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        dest_title = ctk.CTkLabel(
            dest_mgmt_frame,
            text="📁 پوشه‌های مقصد",
            font=ctk.CTkFont(family="B Nazanin", size=18, weight="bold")
        )
        dest_title.pack(pady=10)
        
        # Add destination folder controls
        add_dest_frame = ctk.CTkFrame(dest_mgmt_frame)
        add_dest_frame.pack(fill="x", padx=10, pady=5)
        
        self.new_dest_entry = ctk.CTkEntry(
            add_dest_frame,
            placeholder_text="انتخاب پوشه مقصد جدید...",
            font=ctk.CTkFont(family="B Nazanin", size=12),
            justify="right"
        )
        self.new_dest_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(
            add_dest_frame,
            text="📂 انتخاب پوشه",
            command=self.add_destination_folder,
            width=120,
            font=ctk.CTkFont(family="B Nazanin", size=12)
        ).pack(side="right", padx=5)
        
        # Destination folders display
        self.dest_folders_frame = ctk.CTkScrollableFrame(
            self.dragdrop_frame,
            label_text="🎯 نواحی کپی سریع - فایل بکشید یا کلیک کنید",
            height=400,
            label_font=ctk.CTkFont(family="B Nazanin", size=14, weight="bold")
        )
        self.dest_folders_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Load saved destination folders
        self.destination_folders = self.settings.get("destination_folders", [])
        self.update_destination_folders_display()

    def setup_explorer_tab(self):
        """Setup the file explorer tab"""
        # Search and navigation frame
        nav_frame = ctk.CTkFrame(self.explorer_frame)
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        # Current directory display
        dir_frame = ctk.CTkFrame(nav_frame)
        dir_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(dir_frame, text="پوشه فعلی:", font=ctk.CTkFont(family="B Nazanin", weight="bold")).pack(side="right", padx=5)
        self.current_dir_label = ctk.CTkLabel(dir_frame, text=self.current_dir, font=ctk.CTkFont(family="B Nazanin"))
        self.current_dir_label.pack(side="left", padx=5)
        
        ctk.CTkButton(dir_frame, text="🏠 خانه", command=self.go_home, width=80, font=ctk.CTkFont(family="B Nazanin")).pack(side="left", padx=5)
        ctk.CTkButton(dir_frame, text="📂 انتخاب پوشه", command=self.browse_directory, width=120, font=ctk.CTkFont(family="B Nazanin")).pack(side="left", padx=5)
        
        # Search frame
        search_frame = ctk.CTkFrame(nav_frame)
        search_frame.pack(fill="x")
        
        ctk.CTkLabel(search_frame, text="جستجو:", font=ctk.CTkFont(family="B Nazanin", weight="bold")).pack(side="right", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="نام فایل یا پسوند وارد کنید", font=ctk.CTkFont(family="B Nazanin"), justify="right")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(search_frame, text="🔄 بروزرسانی", command=self.refresh_files, width=100, font=ctk.CTkFont(family="B Nazanin")).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="🗑️ پاک کردن", command=self.clear_search, width=90, font=ctk.CTkFont(family="B Nazanin")).pack(side="left", padx=5)
        
        # File tree with improved styling
        tree_frame = ctk.CTkFrame(self.explorer_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create treeview with scrollbars
        tree_container = tk.Frame(tree_frame, bg=tree_frame.cget("fg_color")[1])
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.file_tree = ttk.Treeview(
            tree_container,
            columns=("Name", "Path", "Type", "Size"),
            show="headings",
            height=15
        )
        
        # Configure columns
        self.file_tree.heading("Name", text="Name")
        self.file_tree.heading("Path", text="Full Path")
        self.file_tree.heading("Type", text="Type")
        self.file_tree.heading("Size", text="Size")
        
        self.file_tree.column("Name", width=250, minwidth=150)
        self.file_tree.column("Path", width=400, minwidth=200)
        self.file_tree.column("Type", width=80, minwidth=60)
        self.file_tree.column("Size", width=100, minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.file_tree.xview)
        
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for tree and scrollbars
        self.file_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Action buttons
        action_frame = ctk.CTkFrame(self.explorer_frame)
        action_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(action_frame, text="Add Selected to Queue", command=self.add_to_queue,
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Select All", command=self.select_all_files).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="Clear Selection", command=self.clear_selection).pack(side="left", padx=5)
        
        # Destination frame
        dest_frame = ctk.CTkFrame(self.explorer_frame)
        dest_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(dest_frame, text="Destination:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.dest_entry = ctk.CTkEntry(dest_frame, placeholder_text="Select destination folder")
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(dest_frame, text="Browse", command=self.browse_dest, width=80).pack(side="right", padx=5)

    def setup_tasks_tab(self):
        """راه‌اندازی تب مدیریت کارها"""
        # دکمه‌های کنترل
        control_frame = ctk.CTkFrame(self.tasks_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # کنترل‌های اصلی
        main_controls = ctk.CTkFrame(control_frame)
        main_controls.pack(fill="x", pady=(0, 5))
        
        self.start_btn = ctk.CTkButton(main_controls, text="▶ شروع انتخاب شده", command=self.start_selected_task,
                                      fg_color="green", hover_color="darkgreen", font=ctk.CTkFont(family="B Nazanin"))
        self.start_btn.pack(side="right", padx=5)
        
        self.pause_btn = ctk.CTkButton(main_controls, text="⏸ توقف انتخاب شده", command=self.pause_selected_task,
                                      fg_color="orange", hover_color="darkorange", font=ctk.CTkFont(family="B Nazanin"))
        self.pause_btn.pack(side="right", padx=5)
        
        self.cancel_btn = ctk.CTkButton(main_controls, text="⏹ لغو انتخاب شده", command=self.cancel_selected_task,
                                       fg_color="red", hover_color="darkred", font=ctk.CTkFont(family="B Nazanin"))
        self.cancel_btn.pack(side="right", padx=5)
        
        self.restart_btn = ctk.CTkButton(main_controls, text="🔄 شروع مجدد", command=self.restart_selected_task,
                                        fg_color="blue", hover_color="darkblue", font=ctk.CTkFont(family="B Nazanin"))
        self.restart_btn.pack(side="right", padx=5)
        
        # کنترل‌های مدیریت کار
        task_controls = ctk.CTkFrame(control_frame)
        task_controls.pack(fill="x")
        
        ctk.CTkButton(task_controls, text="📋 پاک کردن همه", command=self.clear_all_tasks, font=ctk.CTkFont(family="B Nazanin")).pack(side="right", padx=5)
        ctk.CTkButton(task_controls, text="🗑 پاک کردن تکمیل شده", command=self.clear_completed, font=ctk.CTkFont(family="B Nazanin")).pack(side="right", padx=5)
        ctk.CTkButton(task_controls, text="↓ پایین بردن", command=self.move_task_down, font=ctk.CTkFont(family="B Nazanin")).pack(side="right", padx=5)
        ctk.CTkButton(task_controls, text="↑ بالا بردن", command=self.move_task_up, font=ctk.CTkFont(family="B Nazanin")).pack(side="right", padx=5)
        
        # Progress overview
        progress_frame = ctk.CTkFrame(self.tasks_frame)
        progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.overall_progress = ctk.CTkProgressBar(progress_frame)
        self.overall_progress.pack(fill="x", padx=10, pady=5)
        self.overall_progress.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="هیچ کار فعالی موجود نیست", font=ctk.CTkFont(family="B Nazanin"))
        self.progress_label.pack(pady=5)
        
        # Tasks tree
        tasks_tree_frame = ctk.CTkFrame(self.tasks_frame)
        tasks_tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        tasks_container = tk.Frame(tasks_tree_frame, bg=tasks_tree_frame.cget("fg_color")[1])
        tasks_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.task_tree = ttk.Treeview(
            tasks_container,
            columns=("File", "Destination", "Progress", "Size", "Copied", "Speed", "Status"),
            show="headings",
            height=15
        )
        
        # Configure task tree columns
        columns_config = [
            ("File", 250, "📁 File Name", 150),
            ("Destination", 300, "📂 Destination Path", 200),
            ("Progress", 100, "📊 Progress %", 80),
            ("Size", 100, "💾 Total Size", 80),
            ("Copied", 100, "✅ Copied", 80),
            ("Speed", 120, "⚡ Speed (MB/s)", 100),
            ("Status", 150, "🔄 Status", 120)
        ]
        
        for col, width, heading, minwidth in columns_config:
            self.task_tree.heading(col, text=heading)
            self.task_tree.column(col, width=width, minwidth=minwidth, anchor="center")
        
        # Task tree scrollbars
        task_v_scrollbar = ttk.Scrollbar(tasks_container, orient="vertical", command=self.task_tree.yview)
        task_h_scrollbar = ttk.Scrollbar(tasks_container, orient="horizontal", command=self.task_tree.xview)
        
        self.task_tree.configure(yscrollcommand=task_v_scrollbar.set, xscrollcommand=task_h_scrollbar.set)
        
        self.task_tree.grid(row=0, column=0, sticky="nsew")
        task_v_scrollbar.grid(row=0, column=1, sticky="ns")
        task_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tasks_container.grid_rowconfigure(0, weight=1)
        tasks_container.grid_columnconfigure(0, weight=1)

    def setup_settings_tab(self):
        """Setup the settings tab"""
        # Create scrollable frame with beautiful styling
        settings_scroll = ctk.CTkScrollableFrame(
            self.settings_frame,
            corner_radius=10,
            fg_color=("gray95", "gray20"),
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        settings_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Performance Settings
        perf_frame = ctk.CTkFrame(
            settings_scroll,
            corner_radius=12,
            fg_color=("white", "gray25"),
            border_width=1,
            border_color=("gray80", "gray35")
        )
        perf_frame.pack(fill="x", pady=10)
        
        perf_header = ctk.CTkFrame(perf_frame, fg_color="transparent")
        perf_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            perf_header, 
            text="⚡ Performance Settings", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "white")
        ).pack(side="left")
        
        # Performance help button
        perf_help = ctk.CTkButton(
            perf_header,
            text="❓",
            width=30,
            height=30,
            corner_radius=15,
            command=lambda: self.show_help("performance")
        )
        perf_help.pack(side="right")
        
        # Buffer size with slider
        buffer_frame = ctk.CTkFrame(perf_frame, fg_color="transparent")
        buffer_frame.pack(fill="x", padx=15, pady=8)
        
        buffer_header = ctk.CTkFrame(buffer_frame, fg_color="transparent")
        buffer_header.pack(fill="x")
        
        ctk.CTkLabel(
            buffer_header, 
            text="🔧 Buffer Size:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")
        
        self.buffer_var = tk.StringVar(value=str(self.settings.get("buffer_size", 64 * 1024) // 1024))
        buffer_entry = ctk.CTkEntry(
            buffer_header, 
            textvariable=self.buffer_var, 
            width=80,
            placeholder_text="KB"
        )
        buffer_entry.pack(side="right", padx=5)
        
        ctk.CTkLabel(buffer_header, text="KB").pack(side="right")
        
        # Buffer slider
        self.buffer_slider = ctk.CTkSlider(
            buffer_frame,
            from_=16,
            to=1024,
            number_of_steps=32,
            command=self.update_buffer_from_slider
        )
        self.buffer_slider.pack(fill="x", pady=(5, 0))
        self.buffer_slider.set(int(self.buffer_var.get()))
        
        # Buffer recommendation
        buffer_rec = ctk.CTkLabel(
            buffer_frame,
            text="💡 Recommended: SSD=256KB, HDD=64KB, Network=32KB",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        )
        buffer_rec.pack(pady=(2, 0))
        
        # Max threads with slider
        threads_frame = ctk.CTkFrame(perf_frame, fg_color="transparent")
        threads_frame.pack(fill="x", padx=15, pady=8)
        
        threads_header = ctk.CTkFrame(threads_frame, fg_color="transparent")
        threads_header.pack(fill="x")
        
        ctk.CTkLabel(
            threads_header, 
            text="👥 Max Threads:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")
        
        self.threads_var = tk.StringVar(value=str(self.settings.get("max_threads", 4)))
        threads_entry = ctk.CTkEntry(
            threads_header, 
            textvariable=self.threads_var, 
            width=60
        )
        threads_entry.pack(side="right", padx=5)
        
        # Threads slider
        self.threads_slider = ctk.CTkSlider(
            threads_frame,
            from_=1,
            to=8,
            number_of_steps=7,
            command=self.update_threads_from_slider
        )
        self.threads_slider.pack(fill="x", pady=(5, 0))
        self.threads_slider.set(int(self.threads_var.get()))
        
        # Threads recommendation
        threads_rec = ctk.CTkLabel(
            threads_frame,
            text="💡 Recommended: Large files=1-2, Small files=4-6, Network=2-3",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        )
        threads_rec.pack(pady=(2, 0))
        
        # Progress update interval
        progress_frame = ctk.CTkFrame(perf_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=8)
        
        progress_header = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_header.pack(fill="x")
        
        ctk.CTkLabel(
            progress_header, 
            text="⏱ Update Interval:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")
        
        self.progress_interval_var = tk.StringVar(value=str(self.settings.get("progress_update_interval", 0.5)))
        progress_entry = ctk.CTkEntry(
            progress_header, 
            textvariable=self.progress_interval_var, 
            width=60,
            placeholder_text="sec"
        )
        progress_entry.pack(side="right", padx=5)
        
        ctk.CTkLabel(progress_header, text="seconds").pack(side="right")
        
        # Progress slider  
        self.progress_slider = ctk.CTkSlider(
            progress_frame,
            from_=0.1,
            to=2.0,
            number_of_steps=19,
            command=self.update_progress_from_slider
        )
        self.progress_slider.pack(fill="x", pady=(5, 0))
        self.progress_slider.set(float(self.progress_interval_var.get()))
        
        # Behavior Settings
        behavior_frame = ctk.CTkFrame(
            settings_scroll,
            corner_radius=12,
            fg_color=("white", "gray25"),
            border_width=1,
            border_color=("gray80", "gray35")
        )
        behavior_frame.pack(fill="x", pady=10)
        
        behavior_header = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        behavior_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            behavior_header, 
            text="🎯 Behavior Settings", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "white")
        ).pack(side="left")
        
        ctk.CTkButton(
            behavior_header,
            text="❓",
            width=30,
            height=30,
            corner_radius=15,
            command=lambda: self.show_help("behavior")
        ).pack(side="right")
        
        # Overwrite policy
        overwrite_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        overwrite_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            overwrite_frame, 
            text="📁 File Exists Policy:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        self.overwrite_var = tk.StringVar(value=self.settings.get("overwrite_policy", "prompt"))
        overwrite_combo = ctk.CTkComboBox(
            overwrite_frame, 
            values=["prompt", "overwrite", "skip"],
            variable=self.overwrite_var, 
            width=120
        )
        overwrite_combo.pack(side="right", padx=5)
        
        # Additional behavior settings
        # Auto retry
        retry_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        retry_frame.pack(fill="x", padx=15, pady=5)
        
        self.auto_retry_var = tk.BooleanVar(value=self.settings.get("auto_retry", True))
        retry_checkbox = ctk.CTkCheckBox(
            retry_frame,
            text="🔄 Auto Retry Failed Operations",
            variable=self.auto_retry_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        retry_checkbox.pack(side="left")
        
        self.retry_count_var = tk.StringVar(value=str(self.settings.get("retry_count", 3)))
        retry_spinbox = ctk.CTkEntry(retry_frame, textvariable=self.retry_count_var, width=50)
        retry_spinbox.pack(side="right", padx=(5, 0))
        ctk.CTkLabel(retry_frame, text="times").pack(side="right")
        
        # Verify copy
        verify_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        verify_frame.pack(fill="x", padx=15, pady=5)
        
        self.verify_copy_var = tk.BooleanVar(value=self.settings.get("verify_copy", True))
        verify_checkbox = ctk.CTkCheckBox(
            verify_frame,
            text="✅ Verify Copy Integrity (slower but safer)",
            variable=self.verify_copy_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        verify_checkbox.pack(side="left")
        
        # Show hidden files
        hidden_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        hidden_frame.pack(fill="x", padx=15, pady=5)
        
        self.show_hidden_var = tk.BooleanVar(value=self.settings.get("show_hidden_files", False))
        hidden_checkbox = ctk.CTkCheckBox(
            hidden_frame,
            text="🗂 Show Hidden Files and Folders",
            variable=self.show_hidden_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        hidden_checkbox.pack(side="left")
        
        # Create backup
        backup_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        backup_frame.pack(fill="x", padx=15, pady=5)
        
        self.create_backup_var = tk.BooleanVar(value=self.settings.get("create_backup", False))
        backup_checkbox = ctk.CTkCheckBox(
            backup_frame,
            text="💾 Create Backup Before Overwriting",
            variable=self.create_backup_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        backup_checkbox.pack(side="left")
        
        # Preserve permissions
        perm_frame = ctk.CTkFrame(behavior_frame, fg_color="transparent")
        perm_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        self.preserve_permissions_var = tk.BooleanVar(value=self.settings.get("preserve_permissions", True))
        perm_checkbox = ctk.CTkCheckBox(
            perm_frame,
            text="🔐 Preserve File Permissions",
            variable=self.preserve_permissions_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        perm_checkbox.pack(side="left")
        
        # Appearance Settings
        appearance_frame = ctk.CTkFrame(
            settings_scroll,
            corner_radius=12,
            fg_color=("white", "gray25"),
            border_width=1,
            border_color=("gray80", "gray35")
        )
        appearance_frame.pack(fill="x", pady=10)
        
        appearance_header = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        appearance_header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            appearance_header, 
            text="🎨 Appearance Settings", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray10", "white")
        ).pack(side="left")
        
        ctk.CTkButton(
            appearance_header,
            text="❓",
            width=30,
            height=30,
            corner_radius=15,
            command=lambda: self.show_help("appearance")
        ).pack(side="right")
        
        # Theme section with preview
        theme_section = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        theme_section.pack(fill="x", padx=15, pady=10)
        
        theme_header = ctk.CTkFrame(theme_section, fg_color="transparent")
        theme_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            theme_header, 
            text="🎨 Theme:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5)
        
        # Theme help button
        ctk.CTkButton(
            theme_header,
            text="❓",
            width=25,
            height=25,
            corner_radius=12,
            command=lambda: self.show_help("appearance")
        ).pack(side="right")
        
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "dark_blue"))
        theme_combo = ctk.CTkComboBox(
            theme_section, 
            values=list(THEMES.keys()),
            variable=self.theme_var, 
            width=200,
            command=self.preview_theme
        )
        theme_combo.pack(fill="x", padx=5, pady=5)
        
        # Theme preview
        self.theme_preview = ctk.CTkFrame(
            theme_section,
            height=60,
            corner_radius=8,
            fg_color=("gray90", "gray20")
        )
        self.theme_preview.pack(fill="x", padx=5, pady=5)
        self.theme_preview.pack_propagate(False)
        
        ctk.CTkLabel(
            self.theme_preview,
            text="🎨 Theme Preview",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=20)
        
        # Additional appearance settings
        # Notification settings
        notification_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        notification_frame.pack(fill="x", padx=15, pady=5)
        
        self.notification_sound_var = tk.BooleanVar(value=self.settings.get("notification_sound", True))
        notification_checkbox = ctk.CTkCheckBox(
            notification_frame,
            text="🔔 Play Completion Sound",
            variable=self.notification_sound_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        notification_checkbox.pack(side="left")
        
        # Show speed graph
        graph_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        graph_frame.pack(fill="x", padx=15, pady=5)
        
        self.show_speed_graph_var = tk.BooleanVar(value=self.settings.get("show_speed_graph", True))
        graph_checkbox = ctk.CTkCheckBox(
            graph_frame,
            text="📊 Show Speed Graph",
            variable=self.show_speed_graph_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        graph_checkbox.pack(side="left")
        
        # Auto clear completed
        auto_clear_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        auto_clear_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        self.auto_clear_completed_var = tk.BooleanVar(value=self.settings.get("auto_clear_completed", False))
        auto_clear_checkbox = ctk.CTkCheckBox(
            auto_clear_frame,
            text="🗑 Auto Clear Completed Tasks",
            variable=self.auto_clear_completed_var,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        auto_clear_checkbox.pack(side="left")
        
        # Save button with enhanced styling
        save_frame = ctk.CTkFrame(
            settings_scroll,
            fg_color="transparent"
        )
        save_frame.pack(fill="x", pady=20)
        
        save_button = ctk.CTkButton(
            save_frame, 
            text="💾 Save All Settings", 
            command=self.save_settings_from_gui,
            font=ctk.CTkFont(size=16, weight="bold"), 
            height=50,
            corner_radius=25,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
        )
        save_button.pack(pady=10)
        
        # Reset to defaults button
        reset_button = ctk.CTkButton(
            save_frame,
            text="🔄 Reset to Defaults",
            command=self.reset_settings_to_defaults,
            font=ctk.CTkFont(size=12),
            height=35,
            corner_radius=17,
            fg_color=("orange", "darkorange"),
            hover_color=("darkorange", "orange")
        )
        reset_button.pack(pady=(0, 10))

    def setup_status_bar(self):
        """Setup the status bar"""
        status_frame = ctk.CTkFrame(self.main_frame, height=30)
        status_frame.pack(fill="x", side="bottom")
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Ready", anchor="w")
        self.status_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        self.file_count_label = ctk.CTkLabel(status_frame, text="Files: 0")
        self.file_count_label.pack(side="right", padx=10, pady=5)

    def setup_bindings(self):
        """Setup event bindings"""
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        self.file_tree.bind("<Double-1>", self.on_file_double_click)
        self.task_tree.bind("<Double-1>", self.on_task_double_click)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Configure>", self.on_window_resize)

    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.configure(text=message)
        self.root.update_idletasks()

    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

    def get_file_size(self, path: str) -> int:
        """Get size of file or directory"""
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            elif os.path.isdir(path):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(file_path)
                        except (OSError, IOError):
                            continue
                return total_size
            return 0
        except (OSError, IOError):
            return 0

    def browse_directory(self):
        """Browse for a directory"""
        directory = filedialog.askdirectory(initialdir=self.current_dir)
        if directory:
            self.current_dir = directory
            self.current_dir_label.configure(text=directory)
            self.refresh_files()

    def go_home(self):
        """Go to home directory"""
        self.current_dir = os.path.expanduser("~")
        self.current_dir_label.configure(text=self.current_dir)
        self.refresh_files()

    def browse_dest(self):
        """Browse for destination directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, directory)

    def refresh_files(self):
        """Refresh file list"""
        self.update_status("Refreshing files...")
        threading.Thread(target=self._refresh_files_thread, daemon=True).start()

    def _refresh_files_thread(self):
        """Thread function to refresh files"""
        try:
            if not os.path.exists(self.current_dir):
                self.root.after(0, lambda: self.update_status("Directory not found"))
                return
            
            files_data = []
            file_count = 0
            
            for item in os.listdir(self.current_dir):
                item_path = os.path.join(self.current_dir, item)
                try:
                    if os.path.isfile(item_path):
                        size = self.get_file_size(item_path)
                        files_data.append((item, item_path, "File", self.format_size(size)))
                    elif os.path.isdir(item_path):
                        files_data.append((item, item_path, "Directory", ""))
                    file_count += 1
                except (OSError, IOError):
                    continue
            
            # Update cache
            self.file_cache["files"] = {
                item_path: {"name": name, "type": file_type, "size": size_str}
                for name, item_path, file_type, size_str in files_data
            }
            self.file_cache["last_scan"] = time.time()
            self.save_cache()
            
            # Update GUI
            self.root.after(0, lambda: self._update_file_tree(files_data, file_count))
            
        except Exception as e:
            self.logger.error(f"Error refreshing files: {e}")
            self.root.after(0, lambda: self.update_status(f"Error: {e}"))

    def _update_file_tree(self, files_data: List, file_count: int):
        """Update file tree with new data"""
        self.file_tree.delete(*self.file_tree.get_children())
        
        for name, path, file_type, size in files_data:
            self.file_tree.insert("", "end", values=(name, path, file_type, size))
        
        self.file_count_label.configure(text=f"Files: {file_count}")
        self.update_status("Ready")

    def display_cache(self):
        """Display cached files"""
        self.file_tree.delete(*self.file_tree.get_children())
        file_count = 0
        
        for item_path, data in self.file_cache.get("files", {}).items():
            if os.path.exists(item_path):
                size_str = data.get("size", "")
                self.file_tree.insert("", "end", values=(
                    data["name"], item_path, data["type"], size_str
                ))
                file_count += 1
        
        self.file_count_label.configure(text=f"Files: {file_count}")

    def on_search_change(self, event):
        """Handle search entry changes"""
        search_term = self.search_entry.get().lower().strip()
        if not search_term:
            self.display_cache()
            return
        
        self.update_status("Searching...")
        threading.Thread(target=self._search_files_thread, args=(search_term,), daemon=True).start()

    def _search_files_thread(self, search_term: str):
        """Thread function to search files"""
        try:
            filtered_files = []
            file_count = 0
            
            for item_path, data in self.file_cache.get("files", {}).items():
                if not os.path.exists(item_path):
                    continue
                
                name = data["name"].lower()
                
                # Check if search term matches name or extension
                if (search_term in name or 
                    (search_term.startswith(".") and name.endswith(search_term))):
                    size_str = data.get("size", "")
                    filtered_files.append((data["name"], item_path, data["type"], size_str))
                    file_count += 1
            
            self.root.after(0, lambda: self._update_file_tree(filtered_files, file_count))
            
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            self.root.after(0, lambda: self.update_status("Search error"))

    def clear_search(self):
        """Clear search and show all files"""
        self.search_entry.delete(0, tk.END)
        self.display_cache()

    def select_all_files(self):
        """Select all files in the tree"""
        for item in self.file_tree.get_children():
            self.file_tree.selection_add(item)

    def clear_selection(self):
        """Clear file selection"""
        self.file_tree.selection_remove(*self.file_tree.selection())

    def add_to_queue(self):
        """Add selected files to copy queue"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select files to add to queue!")
            return
        
        destination = self.dest_entry.get().strip()
        if not destination:
            messagebox.showerror("Error", "Please select a destination directory!")
            return
        
        if not os.path.exists(destination):
            messagebox.showerror("Error", "Destination directory does not exist!")
            return
        
        added_count = 0
        for item in selected_items:
            values = self.file_tree.item(item, "values")
            if len(values) >= 2:
                source_path = values[1]  # Full path
                if source_path not in [task["source"] for task in self.copy_tasks]:
                    self.add_task(source_path, destination)
                    added_count += 1
        
        if added_count > 0:
            self.update_status(f"Added {added_count} files to queue")
            # Switch to tasks tab
            self.notebook.select(1)
        else:
            messagebox.showinfo("Info", "Selected files are already in the queue!")

    def add_task(self, source: str, destination: str):
        """Add a copy task to the queue"""
        if not os.path.exists(source):
            return
        
        task_id = len(self.copy_tasks)
        filename = os.path.basename(source)
        dest_path = os.path.join(destination, filename)
        file_size = self.get_file_size(source)
        
        task = {
            "id": task_id,
            "source": source,
            "destination": dest_path,
            "filename": filename,
            "size": file_size,
            "copied": 0,
            "progress": 0.0,
            "speed": 0.0,
            "status": "⏳ Pending",
            "paused": False,
            "cancelled": False,
            "completed": False,
            "start_time": 0,
            "last_update": 0,
            "retry_count": 0,
            "error_message": "",
            "future": None
        }
        
        self.copy_tasks.append(task)
        
        # Add to task tree
        self.task_tree.insert("", "end", iid=str(task_id), values=(
            filename,
            dest_path,
            "0%",
            self.format_size(file_size),
            "0 B",
            "0.0",
            "⏳ Pending"
        ))
        
        self.update_overall_progress()

    def get_selected_task(self):
        """Get the currently selected task"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showinfo("انتخاب تسک", "لطفاً یک تسک را انتخاب کنید!")
            return None
        
        task_id = int(selected[0])
        if task_id >= len(self.copy_tasks):
            return None
        
        return self.copy_tasks[task_id]
    
    def start_selected_task(self):
        """Start the selected task"""
        task = self.get_selected_task()
        if not task:
            return
        
        if task["status"] in ["⏳ Pending", "❌ Cancelled", "❌ Error", "⏸ Paused"]:
            task["status"] = "🔄 Running"
            task["cancelled"] = False
            task["paused"] = False
            task["start_time"] = time.time()
            task["last_update"] = time.time()
            task["future"] = self.executor.submit(self.copy_task, task)
            self.update_task_display(task)
            self.update_status(f"شروع کپی: {task['filename']}")
            
            # Update copying state but keep buttons enabled for individual control
            self.is_copying = True
        else:
            messagebox.showinfo("خطا", f"این تسک قابل شروع نیست! وضعیت فعلی: {task['status']}")

    def preview_theme(self, theme_name: str):
        """Preview selected theme"""
        try:
            theme_config = THEMES.get(theme_name, THEMES["dark_blue"])
            
            # Update preview colors based on theme
            if "dark" in theme_name.lower():
                preview_color = ("gray20", "gray30")
                text_color = ("white", "gray90")
            else:
                preview_color = ("gray90", "gray80")
                text_color = ("gray10", "gray20")
            
            self.theme_preview.configure(fg_color=preview_color)
            
            # Update preview text
            for widget in self.theme_preview.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=text_color)
                    
        except Exception as e:
            self.logger.error(f"Error previewing theme: {e}")

    def copy_task(self, task: Dict):
        """Copy a single file/directory with enhanced error handling"""
        try:
            task["status"] = "🔄 Running"
            task["start_time"] = time.time()
            task["last_update"] = time.time()
            
            self.root.after(0, lambda: self.update_task_display(task))
            
            source = task["source"]
            destination = task["destination"]
            
            # Check disk space first
            if not self.check_disk_space(os.path.dirname(destination), task["size"]):
                raise Exception("Insufficient disk space")
            
            # Check if destination exists
            if os.path.exists(destination):
                policy = self.settings.get("overwrite_policy", "prompt")
                if policy == "skip":
                    task["status"] = "⏭ Skipped"
                    self.root.after(0, lambda: self.update_task_display(task))
                    return
                elif policy == "prompt":
                    # For now, just overwrite - in a real app you'd show a dialog
                    pass
                elif policy == "overwrite":
                    if self.settings.get("create_backup", False):
                        backup_path = destination + ".bak"
                        shutil.copy2(destination, backup_path)
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy the file/directory
            if os.path.isfile(source):
                self.copy_file(task)
            elif os.path.isdir(source):
                self.copy_directory(task)
            
            # Verify copy if enabled
            if self.settings.get("verify_copy", False) and not task["cancelled"]:
                if not self.verify_copy(source, destination):
                    raise Exception("Copy verification failed")
            
            if not task["cancelled"]:
                task["status"] = "✅ Completed"
                task["progress"] = 100.0
                task["copied"] = task["size"]
                task["completed"] = True
                self.root.after(0, lambda: self.update_task_display(task))
                self.logger.info(f"Successfully copied {source} to {destination}")
                
                # Play notification sound if enabled
                if self.settings.get("notification_sound", False):
                    self.play_notification_sound()
            
        except Exception as e:
            error_msg = str(e)
            task["error_message"] = error_msg
            
            # Auto retry if enabled
            if (self.settings.get("auto_retry", False) and 
                task["retry_count"] < self.settings.get("retry_count", 3) and
                "space" not in error_msg.lower()):
                
                task["retry_count"] += 1
                task["status"] = f"🔄 Retry {task['retry_count']}"
                self.root.after(2000, lambda: self.copy_task(task))  # Retry after 2 seconds
            else:
                task["status"] = f"❌ Error: {error_msg}"
                self.root.after(0, lambda: self.update_task_display(task))
                self.logger.error(f"Failed to copy {task['source']}: {e}")
        
        finally:
            self.root.after(0, self.check_all_tasks_complete)
    
    def verify_copy(self, source: str, destination: str) -> bool:
        """Verify that the copy was successful"""
        try:
            if os.path.isfile(source) and os.path.isfile(destination):
                return os.path.getsize(source) == os.path.getsize(destination)
            elif os.path.isdir(source) and os.path.isdir(destination):
                # Simple verification - check if all files exist
                for root, dirs, files in os.walk(source):
                    for file in files:
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, source)
                        dst_file = os.path.join(destination, rel_path)
                        if not os.path.exists(dst_file):
                            return False
                return True
            return False
        except:
            return False
    
    def play_notification_sound(self):
        """Play a notification sound"""
        try:
            # Simple system beep - can be enhanced with actual sound files
            import winsound
            winsound.Beep(1000, 200)
        except:
            # On non-Windows systems, try system bell
            try:
                print('\a')  # ASCII bell character
            except:
                pass

    def copy_file(self, task: Dict):
        """Copy a single file with optimized speed and progress tracking"""
        source = task["source"]
        destination = task["destination"]
        
        # Dynamic buffer size based on file size for optimal speed
        file_size = task["size"]
        if file_size < 1024 * 1024:  # < 1MB
            buffer_size = 32 * 1024  # 32KB
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            buffer_size = 512 * 1024  # 512KB
        elif file_size < 1024 * 1024 * 1024:  # < 1GB
            buffer_size = 2 * 1024 * 1024  # 2MB
        else:  # >= 1GB
            buffer_size = 8 * 1024 * 1024  # 8MB
            
        copied_since_update = 0
        update_interval = 0.25  # Update every 0.25 seconds for smoother UI
        
        try:
            with open(source, 'rb') as src, open(destination, 'wb') as dst:
                while not task["cancelled"]:
                    # Handle pause
                    while task["paused"] and not task["cancelled"]:
                        time.sleep(0.1)
                    
                    if task["cancelled"]:
                        break
                    
                    chunk = src.read(buffer_size)
                    if not chunk:
                        break
                    
                    dst.write(chunk)
                    dst.flush()  # Force write to disk for better reliability
                    chunk_size = len(chunk)
                    task["copied"] += chunk_size
                    copied_since_update += chunk_size
                    
                    # Update progress periodically
                    current_time = time.time()
                    if current_time - task["last_update"] >= update_interval:
                        elapsed = current_time - task["last_update"]
                        if elapsed > 0:
                            task["speed"] = (copied_since_update / (1024 * 1024)) / elapsed  # MB/s
                        task["progress"] = (task["copied"] / task["size"]) * 100 if task["size"] > 0 else 0
                        task["last_update"] = current_time
                        copied_since_update = 0
                        
                        self.root.after(0, lambda: self.update_task_display(task))
                        
        except PermissionError:
            raise Exception("دسترسی به فایل مقصد امکان‌پذیر نیست")
        except IOError as e:
            raise Exception(f"خطا در خواندن/نوشتن فایل: {str(e)}")
        except Exception as e:
            raise Exception(f"خطای غیرمنتظره: {str(e)}")

    def copy_directory(self, task: Dict):
        """Copy a directory with optimized progress tracking"""
        source = task["source"]
        destination = task["destination"]
        
        copied_since_update = 0
        update_interval = 0.5  # Update every 0.5 seconds for directories
        
        # Use shutil.copytree with custom copy function for progress
        def copy_with_progress(src, dst, *, follow_symlinks=True):
            nonlocal copied_since_update
            
            if task["cancelled"]:
                return
            
            # Handle pause
            while task["paused"] and not task["cancelled"]:
                time.sleep(0.1)
            
            if task["cancelled"]:
                return
            
            try:
                shutil.copy2(src, dst, follow_symlinks=follow_symlinks)
                
                # Update progress
                file_size = os.path.getsize(dst)  # Use destination size after copy
                task["copied"] += file_size
                copied_since_update += file_size
                task["progress"] = (task["copied"] / task["size"]) * 100 if task["size"] > 0 else 0
                
                current_time = time.time()
                if current_time - task["last_update"] >= update_interval:
                    elapsed = current_time - task["last_update"]
                    if elapsed > 0:
                        task["speed"] = (copied_since_update / (1024 * 1024)) / elapsed
                    task["last_update"] = current_time
                    copied_since_update = 0
                    self.root.after(0, lambda: self.update_task_display(task))
                    
            except PermissionError:
                self.logger.warning(f"Permission denied copying {src} to {dst}")
            except Exception as e:
                self.logger.warning(f"Error copying file {src}: {e}")
        
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(source, destination, copy_function=copy_with_progress, dirs_exist_ok=True)
        except shutil.Error as e:
            # Handle partial copy errors - continue with what we can copy
            self.logger.warning(f"Partial copy error for {source}: {e}")
        except PermissionError:
            raise Exception("دسترسی به پوشه مقصد امکان‌پذیر نیست")
        except Exception as e:
            raise Exception(f"خطا در کپی پوشه: {str(e)}")

    def update_task_display(self, task: Dict):
        """Update task display in the tree"""
        try:
            task_id = str(task["id"])
            if self.task_tree.exists(task_id):
                self.task_tree.set(task_id, "Progress", f"{task['progress']:.1f}%")
                self.task_tree.set(task_id, "Copied", self.format_size(task["copied"]))
                self.task_tree.set(task_id, "Speed", f"{task['speed']:.1f}")
                self.task_tree.set(task_id, "Status", task["status"])
            
            self.update_overall_progress()
        except Exception as e:
            self.logger.error(f"Error updating task display: {e}")

    def update_overall_progress(self):
        """Update overall progress bar and label"""
        if not self.copy_tasks:
            self.overall_progress.set(0)
            self.progress_label.configure(text="No tasks")
            return
        
        total_size = sum(task["size"] for task in self.copy_tasks)
        total_copied = sum(task["copied"] for task in self.copy_tasks)
        
        if total_size > 0:
            progress = total_copied / total_size
            self.overall_progress.set(progress)
        else:
            self.overall_progress.set(0)
        
        # Count tasks by status
        status_counts = {}
        for task in self.copy_tasks:
            status = task["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        status_text = ", ".join([f"{status}: {count}" for status, count in status_counts.items()])
        self.progress_label.configure(text=status_text)

    def pause_selected_task(self):
        """Pause/resume the selected task"""
        task = self.get_selected_task()
        if not task:
            return
        
        if task["status"] == "🔄 Running":
            task["paused"] = True
            task["status"] = "⏸ Paused"
            self.update_task_display(task)
            self.update_status(f"توقف: {task['filename']}")
        elif task["status"] == "⏸ Paused":
            task["paused"] = False
            task["status"] = "🔄 Running"
            self.update_task_display(task)
            self.update_status(f"ادامه: {task['filename']}")
        else:
            messagebox.showinfo("خطا", "این تسک قابل توقف/ادامه نیست!")

    def cancel_selected_task(self):
        """Cancel the selected task"""
        task = self.get_selected_task()
        if not task:
            return
        
        if task["status"] in ["🔄 Running", "⏸ Paused", "⏳ Pending"]:
            if messagebox.askyesno("تأیید", f"آیا می‌خواهید تسک '{task['filename']}' را لغو کنید؟"):
                task["cancelled"] = True
                task["status"] = "❌ Cancelled"
                if task.get("future"):
                    task["future"].cancel()
                self.update_task_display(task)
                self.update_status(f"لغو شد: {task['filename']}")
        else:
            messagebox.showinfo("خطا", "این تسک قابل لغو نیست!")
    
    def restart_selected_task(self):
        """Restart the selected task"""
        task = self.get_selected_task()
        if not task:
            return
        
        if task["status"] in ["✅ Completed", "❌ Cancelled", "❌ Error"]:
            # Reset task
            task["copied"] = 0
            task["progress"] = 0.0
            task["speed"] = 0.0
            task["cancelled"] = False
            task["paused"] = False
            task["retry_count"] = 0
            task["error_message"] = ""
            
            # Start the task
            task["status"] = "🔄 Running"
            task["start_time"] = time.time()
            task["future"] = self.executor.submit(self.copy_task, task)
            self.update_task_display(task)
            self.update_status(f"شروع مجدد: {task['filename']}")
        else:
            messagebox.showinfo("خطا", "این تسک قابل شروع مجدد نیست!")

    def move_task_up(self):
        """Move selected task up in the queue"""
        selected = self.task_tree.selection()
        if not selected:
            return
        
        task_id = int(selected[0])
        if task_id > 0:
            # Swap tasks
            self.copy_tasks[task_id], self.copy_tasks[task_id - 1] = \
                self.copy_tasks[task_id - 1], self.copy_tasks[task_id]
            
            # Update IDs
            self.copy_tasks[task_id]["id"] = task_id
            self.copy_tasks[task_id - 1]["id"] = task_id - 1
            
            self.refresh_task_tree()
            self.task_tree.selection_set(str(task_id - 1))

    def move_task_down(self):
        """Move selected task down in the queue"""
        selected = self.task_tree.selection()
        if not selected:
            return
        
        task_id = int(selected[0])
        if task_id < len(self.copy_tasks) - 1:
            # Swap tasks
            self.copy_tasks[task_id], self.copy_tasks[task_id + 1] = \
                self.copy_tasks[task_id + 1], self.copy_tasks[task_id]
            
            # Update IDs
            self.copy_tasks[task_id]["id"] = task_id
            self.copy_tasks[task_id + 1]["id"] = task_id + 1
            
            self.refresh_task_tree()
            self.task_tree.selection_set(str(task_id + 1))

    def clear_completed(self):
        """Clear completed tasks"""
        completed_statuses = ["✅ Completed", "❌ Cancelled", "⏭ Skipped"]
        initial_count = len(self.copy_tasks)
        self.copy_tasks = [task for task in self.copy_tasks 
                          if not any(status in task["status"] for status in completed_statuses)]
        
        # Reassign IDs
        for i, task in enumerate(self.copy_tasks):
            task["id"] = i
        
        self.refresh_task_tree()
        cleared_count = initial_count - len(self.copy_tasks)
        self.update_status(f"پاک شد: {cleared_count} تسک تکمیل شده. باقی‌مانده: {len(self.copy_tasks)}")

    def clear_all_tasks(self):
        """Clear all tasks"""
        if messagebox.askyesno("تأیید", "همه تسک‌ها پاک شوند؟ این عمل تسک‌های در حال اجرا را لغو می‌کند."):
            # Cancel all active tasks first
            for task in self.copy_tasks:
                if task["status"] in ["🔄 Running", "⏸ Paused", "⏳ Pending"]:
                    task["cancelled"] = True
                    task["status"] = "❌ Cancelled"
                    if task.get("future"):
                        task["future"].cancel()
            
            self.copy_tasks.clear()
            self.refresh_task_tree()
            self.update_status("همه تسک‌ها پاک شدند")

    def refresh_task_tree(self):
        """Refresh the task tree display"""
        self.task_tree.delete(*self.task_tree.get_children())
        
        for task in self.copy_tasks:
            self.task_tree.insert("", "end", iid=str(task["id"]), values=(
                task["filename"],
                task["destination"],
                f"{task['progress']:.1f}%",
                self.format_size(task["size"]),
                self.format_size(task["copied"]),
                f"{task['speed']:.1f}",
                task["status"]
            ))
        
        self.update_overall_progress()

    def check_all_tasks_complete(self):
        """Check if all tasks are complete"""
        active_tasks = [task for task in self.copy_tasks 
                       if task["status"] in ["🔄 Running", "⏳ Pending"]]
        
        if not active_tasks and self.is_copying:
            self.is_copying = False
            self.start_btn.configure(state="normal")
            self.update_status("همه تسک‌ها تکمیل شدند!")
            
            # Show completion notification
            completed_count = len([task for task in self.copy_tasks if task["status"] == "✅ Completed"])
            if completed_count > 0:
                messagebox.showinfo("اتمام کار", f"{completed_count} عملیات کپی با موفقیت تکمیل شد!")

    def save_settings_from_gui(self):
        """Save settings from GUI controls"""
        try:
            # Validate and save buffer size
            buffer_kb = int(self.buffer_var.get())
            if buffer_kb < 1 or buffer_kb > 1024:
                raise ValueError("Buffer size must be between 1 and 1024 KB")
            self.settings["buffer_size"] = buffer_kb * 1024
            
            # Validate and save max threads
            max_threads = int(self.threads_var.get())
            if max_threads < 1 or max_threads > 8:
                raise ValueError("Max threads must be between 1 and 8")
            self.settings["max_threads"] = max_threads
            
            # Validate and save progress interval
            progress_interval = float(self.progress_interval_var.get())
            if progress_interval < 0.1 or progress_interval > 2.0:
                raise ValueError("Progress update interval must be between 0.1 and 2.0 seconds")
            self.settings["progress_update_interval"] = progress_interval
            
            # Validate retry count
            retry_count = int(self.retry_count_var.get())
            if retry_count < 1 or retry_count > 10:
                raise ValueError("Retry count must be between 1 and 10")
            self.settings["retry_count"] = retry_count
            
            # Save behavior settings
            self.settings["overwrite_policy"] = self.overwrite_var.get()
            self.settings["auto_retry"] = self.auto_retry_var.get()
            self.settings["verify_copy"] = self.verify_copy_var.get()
            self.settings["show_hidden_files"] = self.show_hidden_var.get()
            self.settings["create_backup"] = self.create_backup_var.get()
            self.settings["preserve_permissions"] = self.preserve_permissions_var.get()
            
            # Save appearance settings
            new_theme = self.theme_var.get()
            self.settings["theme"] = new_theme
            self.settings["notification_sound"] = self.notification_sound_var.get()
            self.settings["show_speed_graph"] = self.show_speed_graph_var.get()
            self.settings["auto_clear_completed"] = self.auto_clear_completed_var.get()
            
            # Apply theme change
            theme_config = THEMES.get(new_theme, THEMES["dark_blue"])
            ctk.set_appearance_mode(theme_config["mode"])
            ctk.set_default_color_theme(theme_config["color"])
            
            # Restart executor with new thread count
            if self.executor:
                self.executor.shutdown(wait=False)
            self.setup_executor()
            
            self.save_settings()
            
            # Success notification
            success_window = ctk.CTkToplevel(self.root)
            success_window.title("Settings Saved")
            success_window.geometry("300x150")
            success_window.transient(self.root)
            success_window.grab_set()
            
            # Center the window
            success_window.update_idletasks()
            x = (success_window.winfo_screenwidth() // 2) - (300 // 2)
            y = (success_window.winfo_screenheight() // 2) - (150 // 2)
            success_window.geometry(f"300x150+{x}+{y}")
            
            ctk.CTkLabel(
                success_window,
                text="✅ Settings Saved Successfully!",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=30)
            
            ctk.CTkButton(
                success_window,
                text="OK",
                command=success_window.destroy,
                width=100
            ).pack(pady=10)
            
            # Auto close after 2 seconds
            success_window.after(2000, success_window.destroy)
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings_to_defaults(self):
        """Reset all settings to default values"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            try:
                # Reset to default values
                self.buffer_var.set("64")
                self.buffer_slider.set(64)
                
                self.threads_var.set("4")
                self.threads_slider.set(4)
                
                self.progress_interval_var.set("0.5")
                self.progress_slider.set(0.5)
                
                self.retry_count_var.set("3")
                
                # Reset checkboxes
                self.auto_retry_var.set(True)
                self.verify_copy_var.set(True)
                self.show_hidden_var.set(False)
                self.create_backup_var.set(False)
                self.preserve_permissions_var.set(True)
                self.notification_sound_var.set(True)
                self.show_speed_graph_var.set(True)
                self.auto_clear_completed_var.set(False)
                
                # Reset comboboxes
                self.overwrite_var.set("prompt")
                self.theme_var.set("dark_blue")
                
                # Update preview
                self.preview_theme("dark_blue")
                
                messagebox.showinfo("Settings Reset", "All settings have been reset to defaults!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")

    def on_file_double_click(self, event):
        """Handle double-click on file tree"""
        item = self.file_tree.selection()[0] if self.file_tree.selection() else None
        if item:
            values = self.file_tree.item(item, "values")
            if len(values) >= 3 and values[2] == "Directory":
                # Navigate to directory
                self.current_dir = values[1]
                self.current_dir_label.configure(text=self.current_dir)
                self.refresh_files()

    def on_task_double_click(self, event):
        """Handle double-click on task tree"""
        task = self.get_selected_task()
        if task:
            if task["status"] in ["🔄 Running"]:
                self.pause_selected_task()
            elif task["status"] in ["⏸ Paused", "⏳ Pending"]:
                self.start_selected_task()

    
    
    def start_individual_task(self, task_id: int):
        """Start an individual task"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        if task["status"] in ["⏳ Pending", "❌ Cancelled", "❌ Error", "⏸ Paused"]:
            task["status"] = "🔄 Running"
            task["cancelled"] = False
            task["paused"] = False
            task["start_time"] = time.time()
            task["future"] = self.executor.submit(self.copy_task, task)
            self.update_task_display(task)
    
    def pause_individual_task(self, task_id: int):
        """Pause/resume an individual task"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        if task["status"] == "🔄 Running":
            task["paused"] = True
            task["status"] = "⏸ Paused"
            self.update_task_display(task)
    
    def cancel_individual_task(self, task_id: int):
        """Cancel an individual task"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        if task["status"] in ["🔄 Running", "⏸ Paused", "⏳ Pending"]:
            task["cancelled"] = True
            task["status"] = "❌ Cancelled"
            if task.get("future"):
                task["future"].cancel()
            self.update_task_display(task)
    
    def restart_individual_task(self, task_id: int):
        """Restart a cancelled or failed task"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        task["copied"] = 0
        task["progress"] = 0.0
        task["speed"] = 0.0
        task["cancelled"] = False
        task["paused"] = False
        task["retry_count"] = 0
        task["error_message"] = ""
        self.start_individual_task(task_id)
    
    def remove_individual_task(self, task_id: int):
        """Remove a completed task from the list"""
        if task_id >= len(self.copy_tasks):
            return
        
        task = self.copy_tasks[task_id]
        if task["status"] in ["✅ Completed", "❌ Cancelled", "❌ Error"]:
            # Remove the task
            del self.copy_tasks[task_id]
            
            # Reassign IDs to remaining tasks
            for i, remaining_task in enumerate(self.copy_tasks):
                remaining_task["id"] = i
            
            # Refresh the tree view
            self.refresh_task_tree()
            self.update_status(f"Removed task. {len(self.copy_tasks)} remaining.")
    
    def show_help(self, section: str):
        """Show help information for settings sections"""
        help_texts = {
            "performance": """⚡ Performance Settings Help:

🔧 Buffer Size (1-1024 KB):
• Small files (< 1MB): 32-64 KB - Faster for many small files
• Large files (> 100MB): 256-512 KB - Better for big files  
• SSD storage: 256-512 KB - Take advantage of fast storage
• Network drives: 32-128 KB - Avoid network congestion
• Default: 64 KB - Good balance for most scenarios

👥 Max Threads (1-8):
• Single large file: 1-2 threads - Avoid overhead
• Many small files: 4-6 threads - Parallel processing
• Network operations: 1-3 threads - Prevent timeout
• Local SSD: 4-8 threads - Utilize full speed
• Default: 4 threads - Optimal for most systems

⏱ Progress Update (0.1-2.0 seconds):
• Faster updates: 0.1-0.3s - Real-time feedback
• Balanced: 0.5s - Good performance + responsiveness  
• Slower updates: 1.0-2.0s - Better for slow systems""",
            
            "behavior": """🎯 Behavior Settings Help:

📁 File Exists Policy:
• Prompt: Ask user what to do (safest)
• Overwrite: Replace existing files automatically
• Skip: Keep existing files, skip duplicates

🔄 Auto Retry:
• Enabled: Automatically retry failed operations
• Retry Count: How many times to retry (1-10)

✅ Verify Copy:
• Enabled: Check file integrity after copying (slower but safer)
• Disabled: Skip verification (faster but less safe)

🗂 Show Hidden Files:
• Show system and hidden files in explorer

💾 Create Backup:
• Create .bak files before overwriting""",
            
            "appearance": """🎨 Appearance Settings Help:

🌈 Themes:
• Dark Blue: Professional dark theme (best for eyes)
• Dark Green: Nature-inspired dark theme
• Cyberpunk: Futuristic neon theme
• Ocean: Calm blue light theme
• Forest: Natural green theme
• System: Follow your OS theme

🔔 Notifications:
• Sound: Play completion sounds
• Minimize to Tray: Hide to system tray

📊 Visual Features:
• Speed Graph: Show real-time speed charts
• Auto Clear: Remove completed tasks automatically"""
        }
        
        help_window = ctk.CTkToplevel(self.root)
        help_window.title(f"Help - {section.title()}")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (help_window.winfo_screenheight() // 2) - (500 // 2)
        help_window.geometry(f"600x500+{x}+{y}")
        
        # Help content
        help_frame = ctk.CTkScrollableFrame(help_window)
        help_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        help_text = help_texts.get(section, "No help available for this section.")
        
        ctk.CTkLabel(
            help_frame,
            text=help_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=550
        ).pack(pady=10, padx=10, anchor="w")
        
        # Close button
        ctk.CTkButton(
            help_window,
            text="✅ Got it!",
            command=help_window.destroy,
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=10)
    
    def update_buffer_from_slider(self, value):
        """Update buffer size from slider"""
        self.buffer_var.set(str(int(value)))
    
    def update_threads_from_slider(self, value):
        """Update thread count from slider"""
        self.threads_var.set(str(int(value)))
    
    def update_progress_from_slider(self, value):
        """Update progress interval from slider"""
        self.progress_interval_var.set(f"{value:.1f}")
    
    def check_disk_space(self, path: str, required_size: int) -> bool:
        """Check if there's enough disk space"""
        try:
            free_space = psutil.disk_usage(path).free
            # Add 10% buffer to required size
            required_with_buffer = required_size * 1.1
            return free_space > required_with_buffer
        except:
            return True  # If we can't check, assume it's okay
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_copying:
            if messagebox.askyesno("Confirm Exit", "Copy operations are in progress. Exit anyway?"):
                self.cancel_all_tasks()
            else:
                return
        
        # Save current window geometry
        self.settings["window_geometry"] = self.root.geometry()
        
        # Save settings and cleanup
        self.save_settings()
        self.save_cache()
        
        if self.executor:
            self.executor.shutdown(wait=False)
        
        self.root.destroy()

    def on_window_resize(self, event):
        """Handle window resize events for responsive design"""
        if event.widget == self.root:
            try:
                # Get current window size
                window_width = self.root.winfo_width()
                window_height = self.root.winfo_height()
                
                # Only adjust if window is visible and has reasonable size
                if window_width > 100 and window_height > 100:
                    # Adjust column widths based on window size
                    if hasattr(self, 'task_tree'):
                        self.adjust_column_widths(window_width)
                        
            except Exception as e:
                self.logger.error(f"Error handling window resize: {e}")

    def adjust_column_widths(self, window_width):
        """Adjust tree column widths based on window size"""
        try:
            # Calculate available width (minus scrollbar and padding)
            available_width = max(800, window_width - 100)
            
            # Define column weight ratios (flexible sizing)
            column_weights = {
                "File": 0.25,        # 25% - File name
                "Destination": 0.30, # 30% - Destination path  
                "Progress": 0.10,    # 10% - Progress
                "Size": 0.10,        # 10% - Size
                "Copied": 0.10,      # 10% - Copied
                "Speed": 0.10,       # 10% - Speed
                "Status": 0.05       # 5% - Status
            }
            
            # Calculate and set new widths
            for col, weight in column_weights.items():
                new_width = max(60, int(available_width * weight))
                self.task_tree.column(col, width=new_width)
                
        except Exception as e:
            self.logger.error(f"Error adjusting column widths: {e}")

    def add_destination_folder(self):
        """Add a new destination folder"""
        folder = filedialog.askdirectory(title="انتخاب پوشه مقصد")
        if folder and folder not in self.destination_folders:
            self.destination_folders.append(folder)
            self.settings["destination_folders"] = self.destination_folders
            self.save_settings()
            self.update_destination_folders_display()
            self.new_dest_entry.delete(0, 'end')
            self.new_dest_entry.insert(0, folder)

    def remove_destination_folder(self, folder_path):
        """Remove a destination folder"""
        if folder_path in self.destination_folders:
            self.destination_folders.remove(folder_path)
            self.settings["destination_folders"] = self.destination_folders
            self.save_settings()
            self.update_destination_folders_display()

    def update_destination_folders_display(self):
        """Update the display of destination folders"""
        # Clear existing widgets
        for widget in self.dest_folders_frame.winfo_children():
            widget.destroy()
        
        if not self.destination_folders:
            # Show message when no folders
            no_folders_label = ctk.CTkLabel(
                self.dest_folders_frame,
                text="📂 هیچ پوشه مقصدی اضافه نشده است\n\nبرای اضافه کردن پوشه جدید از دکمه Browse استفاده کنید",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_folders_label.pack(pady=50)
            return
        
        # Create drop zones for each destination folder
        for i, folder_path in enumerate(self.destination_folders):
            self.create_drop_zone(folder_path, i)

    def create_drop_zone(self, folder_path, index):
        """Create a drop zone for a destination folder"""
        # Main drop zone frame
        drop_frame = ctk.CTkFrame(
            self.dest_folders_frame,
            height=120,
            border_width=3,
            border_color=("blue", "lightblue"),
            corner_radius=15
        )
        drop_frame.pack(fill="x", padx=10, pady=10)
        drop_frame.pack_propagate(False)
        
        # Folder info frame
        info_frame = ctk.CTkFrame(drop_frame, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Folder name and path
        folder_name = os.path.basename(folder_path) or folder_path
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"📁 {folder_name}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        name_label.pack(anchor="w")
        
        path_label = ctk.CTkLabel(
            info_frame,
            text=folder_path,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        path_label.pack(anchor="w", pady=(0, 10))
        
        # Controls frame
        controls_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        controls_frame.pack(fill="x")
        
        # Click instruction
        click_label = ctk.CTkLabel(
            controls_frame,
            text="🎯 فایل بکشید اینجا یا کلیک کنید",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("blue", "lightblue")
        )
        click_label.pack(side="left")
        
        # Remove button
        remove_btn = ctk.CTkButton(
            controls_frame,
            text="🗑️",
            width=30,
            height=30,
            command=lambda: self.remove_destination_folder(folder_path),
            fg_color="red",
            hover_color="darkred"
        )
        remove_btn.pack(side="right")
        
        # Enable drag & drop on all elements of the drop zone
        self.enable_drop_on_widget(drop_frame, folder_path)
        self.enable_drop_on_widget(info_frame, folder_path) 
        self.enable_drop_on_widget(name_label, folder_path)
        self.enable_drop_on_widget(path_label, folder_path)
        self.enable_drop_on_widget(click_label, folder_path)

    def enable_drop_on_widget(self, widget, destination_path):
        """فعال کردن قابلیت درگ اند دراپ روی ویجت"""
        drag_drop_enabled = False
        
        if DND_FILES and TkinterDnD:
            try:
                # تبدیل widget به tkinter widget اصلی
                tk_widget = widget
                
                # برای CustomTkinter widgets، widget اصلی tkinter را پیدا کن
                if hasattr(widget, '_canvas') and widget._canvas:
                    tk_widget = widget._canvas
                elif hasattr(widget, 'winfo_children'):
                    children = widget.winfo_children()
                    if children:
                        tk_widget = children[0]
                
                # روش مستقیم tkinter برای drag & drop
                def handle_drop(event):
                    """مدیریت drop event"""
                    try:
                        # دریافت فایل‌ها از event
                        files_data = event.data if hasattr(event, 'data') else str(event)
                        if files_data:
                            # پارس کردن مسیر فایل‌ها
                            files = []
                            if '{' in files_data and '}' in files_data:
                                # فایل‌های با space در نام
                                import re
                                files = re.findall(r'\{[^}]+\}', files_data)
                                files = [f.strip('{}') for f in files]
                            else:
                                # فایل‌های عادی
                                files = files_data.split()
                            
                            if files:
                                print(f"📁 فایل‌های دریافتی: {files}")
                                self.handle_dropped_files(files, destination_path)
                            return 'copy'
                    except Exception as e:
                        print(f"❌ خطا در پردازش فایل: {e}")
                    return 'none'
                
                def handle_enter(event):
                    """ورود drag به منطقه"""
                    print("🎯 فایل وارد منطقه درگ شد")
                    self.on_drag_enter(widget)
                    return 'copy'
                
                def handle_leave(event):
                    """خروج drag از منطقه"""
                    print("↩ فایل از منطقه درگ خارج شد")
                    self.on_drag_leave(widget)
                
                # ثبت widget برای drop
                tk_widget.drop_target_register(DND_FILES)
                tk_widget.dnd_bind('<<Drop>>', handle_drop)
                tk_widget.dnd_bind('<<DragEnter>>', handle_enter)
                tk_widget.dnd_bind('<<DragLeave>>', handle_leave)
                
                # ثبت widget اصلی هم
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind('<<Drop>>', handle_drop)
                widget.dnd_bind('<<DragEnter>>', handle_enter)
                widget.dnd_bind('<<DragLeave>>', handle_leave)
                
                drag_drop_enabled = True
                print(f"✓ درگ اند دراپ فعال شد برای: {os.path.basename(destination_path)}")
                
            except Exception as e:
                print(f"⚠ نتوانست درگ اند دراپ را فعال کند: {e}")
        
        # همیشه کلیک برای انتخاب فعال است
        self.setup_manual_file_selection(widget, destination_path)
        
        if not drag_drop_enabled:
            print(f"→ استفاده از کلیک برای انتخاب: {os.path.basename(destination_path)}")
    
    def handle_drop_event(self, event, destination_path):
        """Handle drop events from tkinterdnd2"""
        try:
            # Get the dropped files - handle different formats
            files_data = getattr(event, 'data', '')
            if not files_data:
                files_data = str(event)
            
            print(f"🎯 Drop event received: {files_data}")
            
            # Parse the file paths - handle different possible formats
            files = []
            if isinstance(files_data, str):
                # Handle space-separated paths with potential {} wrapping
                import re
                # Split by space but keep paths with spaces together if wrapped in {}
                pattern = r'\{[^}]+\}|\S+'
                raw_files = re.findall(pattern, files_data)
                files = [f.strip('{}').strip() for f in raw_files if f.strip()]
            else:
                files = [str(files_data)]
            
            print(f"📁 Parsed files: {files}")
            
            if files:
                self.handle_dropped_files(files, destination_path)
            else:
                messagebox.showinfo("اطلاعات", "هیچ فایل معتبری دریافت نشد")
                
        except Exception as e:
            self.logger.error(f"Error handling drop event: {e}")
            print(f"❌ Drop error: {e}")
            messagebox.showerror("خطا", f"خطا در پردازش فایل‌های انداخته شده: {e}")
    
    def on_drag_enter(self, widget):
        """Visual feedback when dragging over drop zone"""
        try:
            widget.configure(fg_color=("#c8e6c9", "#2e7d32"))  # Light green highlight
            widget.configure(border_color="#4caf50", border_width=3)
            print("🎯 Drag entered drop zone")
        except:
            pass
    
    def on_drag_leave(self, widget):
        """Reset visual feedback when leaving drop zone"""
        try:
            widget.configure(fg_color=("#f5f5f5", "#424242"))  # Reset to default
            widget.configure(border_color=("gray70", "gray25"), border_width=2)
            print("↩ Drag left drop zone")
        except:
            pass

    def setup_manual_file_selection(self, widget, destination_path):
        """Setup manual file selection"""
        def manual_select(event=None):
            # Create a simple dialog to choose between files or folders
            choice_window = ctk.CTkToplevel(self.root)
            choice_window.title("انتخاب نوع فایل")
            choice_window.geometry("300x200")
            choice_window.transient(self.root)
            choice_window.grab_set()
            
            # Center the window
            choice_window.update_idletasks()
            x = (choice_window.winfo_screenwidth() // 2) - (300 // 2)
            y = (choice_window.winfo_screenheight() // 2) - (200 // 2)
            choice_window.geometry(f"300x200+{x}+{y}")
            
            ctk.CTkLabel(
                choice_window,
                text="چه چیزی می‌خواهید کپی کنید؟",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=20)
            
            def select_files():
                choice_window.destroy()
                files = filedialog.askopenfilenames(title="انتخاب فایل‌ها برای کپی")
                if files:
                    self.handle_dropped_files(files, destination_path)
            
            def select_folders():
                choice_window.destroy()
                folders = []
                while True:
                    folder = filedialog.askdirectory(title="انتخاب پوشه برای کپی (Cancel برای پایان)")
                    if folder:
                        folders.append(folder)
                        if not messagebox.askyesno("ادامه", "آیا می‌خواهید پوشه دیگری نیز اضافه کنید؟"):
                            break
                    else:
                        break
                if folders:
                    self.handle_dropped_files(folders, destination_path)
            
            ctk.CTkButton(
                choice_window,
                text="📄 انتخاب فایل‌ها",
                command=select_files,
                width=200,
                height=40
            ).pack(pady=10)
            
            ctk.CTkButton(
                choice_window,
                text="📁 انتخاب پوشه‌ها",
                command=select_folders,
                width=200,
                height=40
            ).pack(pady=10)
        
        widget.bind("<Button-1>", manual_select)

    def handle_dropped_files(self, files, destination_path):
        """Handle files dropped on a destination folder"""
        try:
            valid_files = []
            for file_path in files:
                if os.path.exists(file_path):
                    valid_files.append(file_path)
            
            if not valid_files:
                messagebox.showwarning("خطا", "فایل‌های انتخابی معتبر نیستند!")
                return
            
            # Add files to copy queue and start immediately
            added_count = 0
            for file_path in valid_files:
                if os.path.isfile(file_path):
                    filename = os.path.basename(file_path)
                    dest_file = os.path.join(destination_path, filename)
                    
                    # Check if already exists
                    if any(task["source"] == file_path and task["destination"] == dest_file 
                           for task in self.copy_tasks):
                        continue
                    
                    # Add to queue
                    file_size = self.get_file_size(file_path)
                    task_id = len(self.copy_tasks)
                    
                    task = {
                        "id": task_id,
                        "source": file_path,
                        "destination": dest_file,
                        "filename": filename,
                        "size": file_size,
                        "copied": 0,
                        "progress": 0.0,
                        "speed": 0.0,
                        "status": "🚀 Auto-Starting",
                        "paused": False,
                        "cancelled": False,
                        "completed": False,
                        "start_time": time.time(),
                        "last_update": time.time(),
                        "retry_count": 0,
                        "error_message": "",
                        "future": None
                    }
                    
                    self.copy_tasks.append(task)
                    
                    # Add to tree display
                    self.task_tree.insert("", "end", iid=str(task_id), values=(
                        filename,
                        dest_file,
                        "0%",
                        self.format_size(file_size),
                        "0 B",
                        "0.0",
                        "🚀 Auto-Starting"
                    ))
                    
                    # Start immediately
                    task["status"] = "🔄 Running"
                    task["future"] = self.executor.submit(self.copy_task, task)
                    self.update_task_display(task)
                    added_count += 1
                    
                elif os.path.isdir(file_path):
                    # Handle directories
                    dirname = os.path.basename(file_path)
                    dest_dir = os.path.join(destination_path, dirname)
                    
                    # Check if already exists
                    if any(task["source"] == file_path and task["destination"] == dest_dir 
                           for task in self.copy_tasks):
                        continue
                    
                    # Calculate directory size
                    dir_size = self.get_directory_size(file_path)
                    task_id = len(self.copy_tasks)
                    
                    task = {
                        "id": task_id,
                        "source": file_path,
                        "destination": dest_dir,
                        "filename": dirname,
                        "size": dir_size,
                        "copied": 0,
                        "progress": 0.0,
                        "speed": 0.0,
                        "status": "🚀 Auto-Starting",
                        "paused": False,
                        "cancelled": False,
                        "completed": False,
                        "start_time": time.time(),
                        "last_update": time.time(),
                        "retry_count": 0,
                        "error_message": "",
                        "future": None
                    }
                    
                    self.copy_tasks.append(task)
                    
                    # Add to tree display
                    self.task_tree.insert("", "end", iid=str(task_id), values=(
                        dirname,
                        dest_dir,
                        "0%",
                        self.format_size(dir_size),
                        "0 B",
                        "0.0",
                        "🚀 Auto-Starting"
                    ))
                    
                    # Start immediately
                    task["status"] = "🔄 Running"
                    task["future"] = self.executor.submit(self.copy_task, task)
                    self.update_task_display(task)
                    added_count += 1
            
            self.update_overall_progress()
            
            # Switch to tasks tab to show progress
            self.notebook.select(1)  # Tasks tab
            
            if added_count > 0:
                self.update_status(f"🚀 شروع خودکار: {added_count} فایل/پوشه")
                messagebox.showinfo("شروع کپی", f"{added_count} فایل/پوشه به صورت خودکار شروع به کپی شدند!")
            else:
                messagebox.showinfo("هشدار", "همه فایل‌ها قبلاً در صف کپی موجود هستند!")
                
        except Exception as e:
            self.logger.error(f"Error handling dropped files: {e}")
            messagebox.showerror("خطا", f"خطا در پردازش فایل‌ها: {str(e)}")

    def get_directory_size(self, directory_path):
        """Calculate total size of a directory"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            self.logger.warning(f"Error calculating directory size: {e}")
        return total_size
 
    def run(self):
        """Run the application"""
        try:
            # Handle command line arguments for context menu integration
            if len(sys.argv) > 1:
                if sys.argv[1] == "copy" and len(sys.argv) > 2:
                    # Add file to clipboard (for future implementation)
                    pass
                elif sys.argv[1] == "paste" and len(sys.argv) > 2:
                    # Set destination and paste (for future implementation)
                    self.dest_entry.insert(0, sys.argv[2])
            
            # Restore window geometry
            if "window_geometry" in self.settings:
                self.root.geometry(self.settings["window_geometry"])
            
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")

def main():
    """Main entry point"""
    try:
        # Use CTk for full CustomTkinter compatibility
        root = ctk.CTk()
        
        # Apply drag and drop wrapper if available
        if TkinterDnD:
            try:
                # Initialize tkdnd package
                root.tk.call('package', 'require', 'tkdnd')
                # Enable DnD for the root window
                root.tk.call('tkdnd::drag_source', 'register', root, 'DND_Files')
                root.tk.call('tkdnd::drop_target', 'register', root, 'DND_Files')
                root._dnd_init = True
                print("✓ سیستم درگ اند دراپ با موفقیت فعال شد")
            except Exception as e:
                print(f"⚠ نتوانست درگ اند دراپ را فعال کند: {e}, از روش کلیک استفاده می‌شود")
        
        app = FileCopierApp(root)
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()