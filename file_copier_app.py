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
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging
import re
from typing import Dict, List, Optional

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FileCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Persian File Copier Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
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
        """Initialize thread pool executor"""
        max_workers = self.settings.get("max_threads", 4)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def load_settings(self) -> Dict:
        """Load application settings from file"""
        default_settings = {
            "theme": "dark",
            "buffer_size": 64 * 1024,  # 64KB default
            "max_threads": 4,
            "overwrite_policy": "prompt",
            "window_geometry": "1400x900"
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
        ctk.set_appearance_mode(self.settings["theme"])
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # File Explorer Tab
        self.explorer_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.explorer_frame, text="File Explorer")
        self.setup_explorer_tab()
        
        # Tasks Tab
        self.tasks_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tasks_frame, text="Copy Tasks")
        self.setup_tasks_tab()
        
        # Settings Tab
        self.settings_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self.setup_settings_tab()
        
        # Status bar
        self.setup_status_bar()

    def setup_explorer_tab(self):
        """Setup the file explorer tab"""
        # Search and navigation frame
        nav_frame = ctk.CTkFrame(self.explorer_frame)
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        # Current directory display
        dir_frame = ctk.CTkFrame(nav_frame)
        dir_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(dir_frame, text="Current Directory:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.current_dir_label = ctk.CTkLabel(dir_frame, text=self.current_dir)
        self.current_dir_label.pack(side="left", padx=5)
        
        ctk.CTkButton(dir_frame, text="Browse", command=self.browse_directory, width=80).pack(side="right", padx=5)
        ctk.CTkButton(dir_frame, text="Home", command=self.go_home, width=60).pack(side="right", padx=5)
        
        # Search frame
        search_frame = ctk.CTkFrame(nav_frame)
        search_frame.pack(fill="x")
        
        ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter filename or .extension")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(search_frame, text="Clear", command=self.clear_search, width=60).pack(side="right", padx=5)
        ctk.CTkButton(search_frame, text="Refresh", command=self.refresh_files, width=80).pack(side="right", padx=5)
        
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
        """Setup the tasks management tab"""
        # Control buttons
        control_frame = ctk.CTkFrame(self.tasks_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Main controls
        main_controls = ctk.CTkFrame(control_frame)
        main_controls.pack(fill="x", pady=(0, 5))
        
        self.start_btn = ctk.CTkButton(main_controls, text="▶ Start All", command=self.start_all_tasks,
                                      fg_color="green", hover_color="darkgreen")
        self.start_btn.pack(side="left", padx=5)
        
        self.pause_btn = ctk.CTkButton(main_controls, text="⏸ Pause All", command=self.pause_all_tasks,
                                      fg_color="orange", hover_color="darkorange")
        self.pause_btn.pack(side="left", padx=5)
        
        self.cancel_btn = ctk.CTkButton(main_controls, text="⏹ Cancel All", command=self.cancel_all_tasks,
                                       fg_color="red", hover_color="darkred")
        self.cancel_btn.pack(side="left", padx=5)
        
        # Task management controls
        task_controls = ctk.CTkFrame(control_frame)
        task_controls.pack(fill="x")
        
        ctk.CTkButton(task_controls, text="↑ Move Up", command=self.move_task_up).pack(side="left", padx=5)
        ctk.CTkButton(task_controls, text="↓ Move Down", command=self.move_task_down).pack(side="left", padx=5)
        ctk.CTkButton(task_controls, text="🗑 Clear Completed", command=self.clear_completed).pack(side="left", padx=5)
        ctk.CTkButton(task_controls, text="📋 Clear All", command=self.clear_all_tasks).pack(side="left", padx=5)
        
        # Progress overview
        progress_frame = ctk.CTkFrame(self.tasks_frame)
        progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.overall_progress = ctk.CTkProgressBar(progress_frame)
        self.overall_progress.pack(fill="x", padx=10, pady=5)
        self.overall_progress.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="No active tasks")
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
            ("File", 200, "File Name"),
            ("Destination", 250, "Destination Path"),
            ("Progress", 80, "Progress %"),
            ("Size", 80, "Total Size"),
            ("Copied", 80, "Copied"),
            ("Speed", 100, "Speed (MB/s)"),
            ("Status", 100, "Status")
        ]
        
        for col, width, heading in columns_config:
            self.task_tree.heading(col, text=heading)
            self.task_tree.column(col, width=width, minwidth=60)
        
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
        # Create scrollable frame
        settings_scroll = ctk.CTkScrollableFrame(self.settings_frame)
        settings_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Performance Settings
        perf_frame = ctk.CTkFrame(settings_scroll)
        perf_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(perf_frame, text="Performance Settings", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Buffer size
        buffer_frame = ctk.CTkFrame(perf_frame)
        buffer_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(buffer_frame, text="Buffer Size (KB):").pack(side="left", padx=5)
        self.buffer_var = tk.StringVar(value=str(self.settings.get("buffer_size", 64 * 1024) // 1024))
        buffer_entry = ctk.CTkEntry(buffer_frame, textvariable=self.buffer_var, width=100)
        buffer_entry.pack(side="right", padx=5)
        
        # Max threads
        threads_frame = ctk.CTkFrame(perf_frame)
        threads_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(threads_frame, text="Max Threads (1-8):").pack(side="left", padx=5)
        self.threads_var = tk.StringVar(value=str(self.settings.get("max_threads", 4)))
        threads_entry = ctk.CTkEntry(threads_frame, textvariable=self.threads_var, width=100)
        threads_entry.pack(side="right", padx=5)
        
        # Behavior Settings
        behavior_frame = ctk.CTkFrame(settings_scroll)
        behavior_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(behavior_frame, text="Behavior Settings", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Overwrite policy
        overwrite_frame = ctk.CTkFrame(behavior_frame)
        overwrite_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(overwrite_frame, text="File Exists Policy:").pack(side="left", padx=5)
        self.overwrite_var = tk.StringVar(value=self.settings.get("overwrite_policy", "prompt"))
        overwrite_combo = ctk.CTkComboBox(overwrite_frame, values=["prompt", "overwrite", "skip"],
                                         variable=self.overwrite_var, width=120)
        overwrite_combo.pack(side="right", padx=5)
        
        # Appearance Settings
        appearance_frame = ctk.CTkFrame(settings_scroll)
        appearance_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(appearance_frame, text="Appearance Settings", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Theme
        theme_frame = ctk.CTkFrame(appearance_frame)
        theme_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left", padx=5)
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))
        theme_combo = ctk.CTkComboBox(theme_frame, values=["dark", "light", "system"],
                                     variable=self.theme_var, width=120)
        theme_combo.pack(side="right", padx=5)
        
        # Save button
        save_frame = ctk.CTkFrame(settings_scroll)
        save_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(save_frame, text="💾 Save Settings", command=self.save_settings_from_gui,
                     font=ctk.CTkFont(weight="bold"), height=40).pack(pady=10)

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
            "status": "Pending",
            "paused": False,
            "cancelled": False,
            "start_time": 0,
            "last_update": 0
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
            "Pending"
        ))
        
        self.update_overall_progress()

    def start_all_tasks(self):
        """Start all pending tasks"""
        if self.is_copying:
            messagebox.showwarning("Warning", "Copy operations are already in progress!")
            return
        
        pending_tasks = [task for task in self.copy_tasks 
                        if task["status"] == "Pending" and not task["cancelled"]]
        
        if not pending_tasks:
            messagebox.showinfo("Info", "No pending tasks to start!")
            return
        
        self.is_copying = True
        self.update_status(f"Starting {len(pending_tasks)} tasks...")
        
        # Update button states
        self.start_btn.configure(state="disabled")
        
        # Start tasks in thread pool
        for task in pending_tasks:
            self.executor.submit(self.copy_task, task)

    def copy_task(self, task: Dict):
        """Copy a single file/directory"""
        try:
            task["status"] = "Running"
            task["start_time"] = time.time()
            task["last_update"] = time.time()
            
            self.root.after(0, lambda: self.update_task_display(task))
            
            source = task["source"]
            destination = task["destination"]
            
            # Check if destination exists
            if os.path.exists(destination):
                policy = self.settings.get("overwrite_policy", "prompt")
                if policy == "skip":
                    task["status"] = "Skipped"
                    self.root.after(0, lambda: self.update_task_display(task))
                    return
                elif policy == "prompt":
                    # For now, just overwrite - in a real app you'd show a dialog
                    pass
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination)
            os.makedirs(dest_dir, exist_ok=True)
            
            if os.path.isfile(source):
                self.copy_file(task)
            elif os.path.isdir(source):
                self.copy_directory(task)
            
            if not task["cancelled"]:
                task["status"] = "Completed"
                task["progress"] = 100.0
                task["copied"] = task["size"]
                self.root.after(0, lambda: self.update_task_display(task))
                self.logger.info(f"Successfully copied {source} to {destination}")
            
        except Exception as e:
            task["status"] = f"Error: {str(e)}"
            self.root.after(0, lambda: self.update_task_display(task))
            self.logger.error(f"Failed to copy {task['source']}: {e}")
        
        finally:
            self.root.after(0, self.check_all_tasks_complete)

    def copy_file(self, task: Dict):
        """Copy a single file with progress tracking"""
        source = task["source"]
        destination = task["destination"]
        buffer_size = self.settings.get("buffer_size", 64 * 1024)
        
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
                task["copied"] += len(chunk)
                
                # Update progress every 0.5 seconds
                current_time = time.time()
                if current_time - task["last_update"] >= 0.5:
                    elapsed = current_time - task["last_update"]
                    task["speed"] = len(chunk) / (1024 * 1024) / elapsed  # MB/s
                    task["progress"] = (task["copied"] / task["size"]) * 100 if task["size"] > 0 else 0
                    task["last_update"] = current_time
                    
                    self.root.after(0, lambda: self.update_task_display(task))

    def copy_directory(self, task: Dict):
        """Copy a directory with progress tracking"""
        source = task["source"]
        destination = task["destination"]
        
        # Use shutil.copytree with custom copy function for progress
        def copy_with_progress(src, dst, *, follow_symlinks=True):
            if task["cancelled"]:
                return
            
            # Handle pause
            while task["paused"] and not task["cancelled"]:
                time.sleep(0.1)
            
            shutil.copy2(src, dst, follow_symlinks=follow_symlinks)
            
            # Update progress
            file_size = os.path.getsize(src)
            task["copied"] += file_size
            task["progress"] = (task["copied"] / task["size"]) * 100 if task["size"] > 0 else 0
            
            current_time = time.time()
            if current_time - task["last_update"] >= 0.5:
                elapsed = current_time - task["last_update"]
                task["speed"] = file_size / (1024 * 1024) / elapsed if elapsed > 0 else 0
                task["last_update"] = current_time
                self.root.after(0, lambda: self.update_task_display(task))
        
        try:
            shutil.copytree(source, destination, copy_function=copy_with_progress, dirs_exist_ok=True)
        except shutil.Error as e:
            # Handle partial copy errors
            self.logger.warning(f"Partial copy error for {source}: {e}")

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

    def pause_all_tasks(self):
        """Pause/resume all tasks"""
        for task in self.copy_tasks:
            if task["status"] == "Running":
                task["paused"] = not task["paused"]
                task["status"] = "Paused" if task["paused"] else "Running"
                self.update_task_display(task)

    def cancel_all_tasks(self):
        """Cancel all tasks"""
        for task in self.copy_tasks:
            if task["status"] in ["Running", "Paused", "Pending"]:
                task["cancelled"] = True
                task["status"] = "Cancelled"
                self.update_task_display(task)
        
        self.is_copying = False
        self.start_btn.configure(state="normal")
        self.update_status("All tasks cancelled")

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
        completed_statuses = ["Completed", "Cancelled", "Skipped"]
        self.copy_tasks = [task for task in self.copy_tasks 
                          if not any(status in task["status"] for status in completed_statuses)]
        
        # Reassign IDs
        for i, task in enumerate(self.copy_tasks):
            task["id"] = i
        
        self.refresh_task_tree()
        self.update_status(f"Cleared completed tasks. {len(self.copy_tasks)} remaining.")

    def clear_all_tasks(self):
        """Clear all tasks"""
        if messagebox.askyesno("Confirm", "Clear all tasks? This will cancel any running operations."):
            self.cancel_all_tasks()
            self.copy_tasks.clear()
            self.refresh_task_tree()
            self.update_status("All tasks cleared")

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
                       if task["status"] in ["Running", "Pending"]]
        
        if not active_tasks and self.is_copying:
            self.is_copying = False
            self.start_btn.configure(state="normal")
            self.update_status("All tasks completed!")
            
            # Show completion notification
            completed_count = len([task for task in self.copy_tasks if task["status"] == "Completed"])
            messagebox.showinfo("Tasks Complete", f"Completed {completed_count} copy operations!")

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
            
            # Save other settings
            self.settings["overwrite_policy"] = self.overwrite_var.get()
            new_theme = self.theme_var.get()
            self.settings["theme"] = new_theme
            
            # Apply theme change
            if new_theme != ctk.get_appearance_mode().lower():
                ctk.set_appearance_mode(new_theme)
            
            # Restart executor with new thread count
            if self.executor:
                self.executor.shutdown(wait=False)
            self.setup_executor()
            
            self.save_settings()
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

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
        item = self.task_tree.selection()[0] if self.task_tree.selection() else None
        if item:
            task_id = int(item)
            if task_id < len(self.copy_tasks):
                task = self.copy_tasks[task_id]
                # Toggle pause/resume for individual task
                if task["status"] == "Running":
                    task["paused"] = not task["paused"]
                    task["status"] = "Paused" if task["paused"] else "Running"
                    self.update_task_display(task)

    def on_closing(self):
        """Handle application closing"""
        if self.is_copying:
            if messagebox.askyesno("Confirm Exit", "Copy operations are in progress. Exit anyway?"):
                self.cancel_all_tasks()
            else:
                return
        
        # Save settings and cleanup
        self.save_settings()
        self.save_cache()
        
        if self.executor:
            self.executor.shutdown(wait=False)
        
        self.root.destroy()

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
        root = ctk.CTk()
        app = FileCopierApp(root)
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()