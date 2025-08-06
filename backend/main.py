"""
Persian File Copier Pro - Enhanced FastAPI Backend
🚀 Professional file management with real-time updates
شرکت فناوری نوآوران مثبت سبز
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import asyncio
import json
import os
import sys
import shutil
import psutil
import sqlite3
import threading
import time
import hashlib
from pathlib import Path
from datetime import datetime
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
import mimetypes
import stat
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Persian File Copier Pro",
    description="مدیریت فایل‌های حرفه‌ای با رابط کاربری مدرن و real-time updates",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
active_connections: List[WebSocket] = []
config_data: Dict = {}
db_path = "file_cache.db"

# Enhanced Pydantic Models
class FileInfo(BaseModel):
    path: str
    name: str
    size: int
    modified: float
    is_directory: bool
    extension: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None
    permissions: Optional[str] = None
    owner: Optional[str] = None

class DriveInfo(BaseModel):
    path: str
    name: str
    total_space: int
    free_space: int
    used_space: int
    filesystem: str
    drive_type: str
    label: Optional[str] = None

class CopyRequest(BaseModel):
    source_files: List[str]
    destination: str
    options: Optional[Dict[str, Any]] = {}

class TaskUpdate(BaseModel):
    task_id: str
    status: str
    progress: int
    current_file: str
    speed: float
    eta: int
    error: Optional[str] = None

class SearchRequest(BaseModel):
    path: str = "all"
    search: str = ""
    format_filter: str = "همه فرمت‌ها"
    limit: int = 1000
    offset: int = 0
    sort_by: str = "name"
    sort_order: str = "asc"

class SettingsBatch(BaseModel):
    settings: Dict[str, Any]

# Enhanced Database Manager
class DatabaseManager:
    def __init__(self, db_file: str = "file_cache.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize enhanced database tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Files table with more metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                size INTEGER NOT NULL,
                modified INTEGER NOT NULL,
                drive TEXT NOT NULL,
                extension TEXT,
                type TEXT,
                is_directory BOOLEAN DEFAULT 0,
                indexed_at INTEGER DEFAULT (strftime('%s', 'now')),
                hash TEXT,
                permissions TEXT,
                owner TEXT,
                mime_type TEXT,
                icon TEXT
            )
        ''')
        
        # Enhanced settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                updated_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # Tasks history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                completed_at INTEGER,
                source_files TEXT,
                destination TEXT,
                total_files INTEGER,
                copied_files INTEGER,
                total_size INTEGER,
                copied_size INTEGER,
                error_message TEXT
            )
        ''')
        
        # Create comprehensive indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_drive ON files(drive)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_name ON files(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_size ON files(size)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_type ON files(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_history_status ON task_history(status)')
        
        conn.commit()
        conn.close()
    
    def get_file_icon(self, file_path: str, is_directory: bool = False) -> str:
        """Get appropriate icon for file type"""
        if is_directory:
            return "📁"
        
        ext = Path(file_path).suffix.lower()
        icon_map = {
            '.pdf': '📄', '.doc': '📄', '.docx': '📄', '.txt': '📄',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.bmp': '🖼️',
            '.mp4': '🎬', '.avi': '🎬', '.mkv': '🎬', '.mov': '🎬',
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.m4a': '🎵',
            '.zip': '🗂️', '.rar': '🗂️', '.7z': '🗂️', '.tar': '🗂️',
            '.exe': '⚙️', '.msi': '⚙️', '.deb': '⚙️', '.rpm': '⚙️',
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
            '.iso': '💿', '.img': '💿'
        }
        return icon_map.get(ext, '📄')
    
    def index_directory(self, directory: str, drive_name: str) -> int:
        """Index a directory with enhanced metadata"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        indexed_count = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                for name in dirs + files:
                    full_path = os.path.join(root, name)
                    try:
                        stat_info = os.stat(full_path)
                        is_dir = os.path.isdir(full_path)
                        
                        # Get file metadata
                        size = stat_info.st_size if not is_dir else 0
                        modified = int(stat_info.st_mtime)
                        extension = Path(name).suffix.lower() if not is_dir else ""
                        mime_type = mimetypes.guess_type(full_path)[0] if not is_dir else "folder"
                        icon = self.get_file_icon(full_path, is_dir)
                        
                        # Get permissions (simplified)
                        permissions = oct(stat_info.st_mode)[-3:]
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO files 
                            (path, name, size, modified, drive, extension, type, is_directory, 
                             indexed_at, permissions, mime_type, icon)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            full_path, name, size, modified, drive_name, extension,
                            mime_type, is_dir, int(time.time()), permissions, mime_type, icon
                        ))
                        indexed_count += 1
                        
                        if indexed_count % 100 == 0:
                            conn.commit()
                            
                    except (OSError, PermissionError):
                        continue
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error indexing directory {directory}: {e}")
        finally:
            conn.close()
        
        return indexed_count
    
    def search_files_advanced(self, search_term: str = "", **filters) -> List[Dict]:
        """Advanced file search with multiple filters"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT path, name, size, modified, is_directory, extension, 
                       type, icon, permissions, mime_type
                FROM files WHERE 1=1
            """
            params = []
            
            if search_term:
                query += " AND name LIKE ?"
                params.append(f"%{search_term}%")
            
            if filters.get('format_filter') and filters['format_filter'] != "همه فرمت‌ها":
                query += " AND extension = ?"
                params.append(filters['format_filter'].lower())
            
            if filters.get('size_min'):
                query += " AND size >= ?"
                params.append(filters['size_min'])
                
            if filters.get('size_max'):
                query += " AND size <= ?"
                params.append(filters['size_max'])
            
            if filters.get('drive'):
                query += " AND drive = ?"
                params.append(filters['drive'])
            
            # Sorting
            sort_by = filters.get('sort_by', 'name')
            sort_order = filters.get('sort_order', 'asc')
            valid_sorts = ['name', 'size', 'modified', 'extension']
            if sort_by in valid_sorts:
                query += f" ORDER BY {sort_by} {sort_order.upper()}"
            
            # Pagination
            limit = filters.get('limit', 1000)
            offset = filters.get('offset', 0)
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            files = []
            for row in results:
                files.append({
                    "path": row[0],
                    "name": row[1],
                    "size": row[2],
                    "modified": row[3],
                    "is_directory": bool(row[4]),
                    "extension": row[5] or "",
                    "type": row[6] or "",
                    "icon": row[7] or "📄",
                    "permissions": row[8] or "",
                    "mime_type": row[9] or "",
                    "size_formatted": self.format_file_size(row[2]),
                    "modified_formatted": datetime.fromtimestamp(row[3]).strftime("%Y/%m/%d %H:%M")
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return []
        finally:
            conn.close()
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def save_setting(self, key: str, value: Any, category: str = "general"):
        """Save setting with category"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value, category, updated_at) VALUES (?, ?, ?, ?)",
                (key, json.dumps(value), category, int(time.time()))
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving setting {key}: {e}")
            return False
        finally:
            conn.close()
    
    def load_setting(self, key: str, default=None):
        """Load setting from database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return default
        except Exception as e:
            logger.error(f"Error loading setting {key}: {e}")
            return default
        finally:
            conn.close()

# Initialize database
db_manager = DatabaseManager()

# Enhanced WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_data: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None):
        await websocket.accept()
        if not client_id:
            client_id = str(uuid.uuid4())
        
        self.active_connections[client_id] = websocket
        self.connection_data[client_id] = {
            "connected_at": time.time(),
            "last_ping": time.time()
        }
        
        logger.info(f"WebSocket connected: {client_id}. Total: {len(self.active_connections)}")
        return client_id

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.connection_data[client_id]
            logger.info(f"WebSocket disconnected: {client_id}. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict, exclude: List[str] = None):
        if exclude is None:
            exclude = []
        
        disconnected = []
        for client_id, connection in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect(client_id)

manager = ConnectionManager()

# Enhanced File Operations Manager
class FileOperationsManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.active_tasks: Dict[str, Dict] = {}
        self.task_history = []

    def start_copy_task(self, source_files: List[str], destination: str, options: Dict = None) -> str:
        """Start enhanced copy task with options"""
        task_id = str(uuid.uuid4())
        
        if options is None:
            options = {}
        
        # Calculate total size
        total_size = 0
        valid_files = []
        for file_path in source_files:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                valid_files.append(file_path)
        
        task_info = {
            "id": task_id,
            "type": "copy",
            "source_files": valid_files,
            "destination": destination,
            "options": options,
            "status": "running",
            "progress": 0,
            "total_files": len(valid_files),
            "copied_files": 0,
            "total_size": total_size,
            "copied_size": 0,
            "current_file": "",
            "speed": 0,
            "eta": 0,
            "start_time": time.time(),
            "errors": [],
            "paused": False,
            "cancelled": False
        }
        
        self.active_tasks[task_id] = task_info
        
        # Submit task to executor
        future = self.executor.submit(self._copy_files_enhanced, task_id)
        task_info["future"] = future
        
        return task_id

    def _copy_files_enhanced(self, task_id: str):
        """Enhanced copy files with advanced features"""
        task = self.active_tasks.get(task_id)
        if not task:
            return

        try:
            os.makedirs(task["destination"], exist_ok=True)
            start_time = time.time()
            
            for i, source_file in enumerate(task["source_files"]):
                # Check for pause/cancel
                while task.get("paused") and not task.get("cancelled"):
                    time.sleep(0.1)
                
                if task.get("cancelled"):
                    break
                
                if not os.path.exists(source_file):
                    task["errors"].append(f"File not found: {source_file}")
                    continue
                
                filename = os.path.basename(source_file)
                dest_path = os.path.join(task["destination"], filename)
                
                # Update current file
                task["current_file"] = filename
                task["copied_files"] = i
                task["progress"] = int((i / len(task["source_files"])) * 100)
                
                # Calculate speed and ETA
                elapsed = time.time() - start_time
                if elapsed > 0:
                    speed = task["copied_size"] / elapsed  # bytes per second
                    task["speed"] = speed
                    
                    remaining_size = task["total_size"] - task["copied_size"]
                    if speed > 0:
                        task["eta"] = int(remaining_size / speed)
                
                # Broadcast progress
                asyncio.create_task(self._broadcast_task_update(task_id))
                
                # Copy file with options
                try:
                    if os.path.isdir(source_file):
                        if task["options"].get("copy_subdirectories", True):
                            shutil.copytree(source_file, dest_path, dirs_exist_ok=True)
                    else:
                        # Copy with options
                        if task["options"].get("skip_existing", False) and os.path.exists(dest_path):
                            continue
                        
                        shutil.copy2(source_file, dest_path)
                        
                        # Verify copy if requested
                        if task["options"].get("verify_copy", False):
                            if not self._verify_file_copy(source_file, dest_path):
                                task["errors"].append(f"Verification failed: {filename}")
                        
                        # Update copied size
                        if os.path.isfile(source_file):
                            task["copied_size"] += os.path.getsize(source_file)
                        
                except Exception as e:
                    error_msg = f"Error copying {filename}: {str(e)}"
                    task["errors"].append(error_msg)
                    logger.error(error_msg)
                    continue
            
            if task.get("cancelled"):
                task["status"] = "cancelled"
            elif task["errors"]:
                task["status"] = "completed_with_errors"
            else:
                task["status"] = "completed"
            
            task["progress"] = 100
            task["copied_files"] = len(task["source_files"])
            task["end_time"] = time.time()
            
        except Exception as e:
            logger.error(f"Error in copy task {task_id}: {e}")
            task["status"] = "error"
            task["errors"].append(str(e))
        
        # Save to history
        self._save_task_to_history(task)
        
        # Final broadcast
        asyncio.create_task(self._broadcast_task_update(task_id))

    def _verify_file_copy(self, source: str, destination: str) -> bool:
        """Verify file copy by comparing checksums"""
        try:
            def get_file_hash(filepath):
                hash_sha256 = hashlib.sha256()
                with open(filepath, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_sha256.update(chunk)
                return hash_sha256.hexdigest()
            
            return get_file_hash(source) == get_file_hash(destination)
        except Exception:
            return False

    def _save_task_to_history(self, task: Dict):
        """Save completed task to database history"""
        conn = sqlite3.connect(db_manager.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO task_history 
                (id, type, status, created_at, completed_at, source_files, destination,
                 total_files, copied_files, total_size, copied_size, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task["id"], task["type"], task["status"],
                int(task["start_time"]), int(task.get("end_time", time.time())),
                json.dumps(task["source_files"]), task["destination"],
                task["total_files"], task["copied_files"],
                task["total_size"], task["copied_size"],
                json.dumps(task.get("errors", []))
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving task history: {e}")
        finally:
            conn.close()

    async def _broadcast_task_update(self, task_id: str):
        """Broadcast task update to all connected clients"""
        task = self.active_tasks.get(task_id)
        if task:
            # Remove non-serializable items
            broadcast_task = {k: v for k, v in task.items() if k not in ["future"]}
            await manager.broadcast({
                "type": "task_update",
                "data": broadcast_task
            })

    def control_task(self, task_id: str, action: str) -> bool:
        """Control task (pause/resume/cancel)"""
        task = self.active_tasks.get(task_id)
        if not task:
            return False
        
        if action == "pause":
            task["paused"] = True
            task["status"] = "paused"
        elif action == "resume":
            task["paused"] = False
            task["status"] = "running"
        elif action == "cancel":
            task["cancelled"] = True
            task["status"] = "cancelled"
        
        # Broadcast update
        asyncio.create_task(self._broadcast_task_update(task_id))
        return True

file_ops = FileOperationsManager()

# API Routes
@app.get("/")
async def serve_index():
    """Serve the main index_pro.html"""
    index_path = Path("web/index_pro.html")
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    else:
        return HTMLResponse("<h1>Persian File Copier Pro</h1><p>UI file not found</p>")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "active_connections": len(manager.active_connections),
        "active_tasks": len(file_ops.active_tasks)
    }

@app.get("/api/drives")
async def get_drives() -> List[DriveInfo]:
    """Get enhanced system drives information"""
    drives = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            drive_info = DriveInfo(
                path=partition.mountpoint,
                name=partition.device,
                total_space=usage.total,
                free_space=usage.free,
                used_space=usage.used,
                filesystem=partition.fstype,
                drive_type="local",  # Could be enhanced to detect network drives
                label=getattr(partition, 'label', None)
            )
            drives.append(drive_info)
        except Exception as e:
            logger.error(f"Error getting drive info for {partition.mountpoint}: {e}")
    
    return drives

@app.post("/api/search")
async def search_files(request: SearchRequest):
    """Enhanced file search with real-time capability"""
    try:
        if request.path == "all":
            # Search in database
            files = db_manager.search_files_advanced(
                search_term=request.search,
                format_filter=request.format_filter,
                limit=request.limit,
                offset=request.offset,
                sort_by=request.sort_by,
                sort_order=request.sort_order
            )
        else:
            # Direct filesystem search with enhanced metadata
            files = []
            if os.path.exists(request.path) and os.path.isdir(request.path):
                try:
                    items = list(os.listdir(request.path))
                    
                    # Apply search filter
                    if request.search:
                        items = [item for item in items if request.search.lower() in item.lower()]
                    
                    # Limit results
                    items = items[request.offset:request.offset + request.limit]
                    
                    for item in items:
                        item_path = os.path.join(request.path, item)
                        try:
                            stat_info = os.stat(item_path)
                            is_dir = os.path.isdir(item_path)
                            
                            files.append({
                                "path": item_path,
                                "name": item,
                                "size": stat_info.st_size if not is_dir else 0,
                                "modified": stat_info.st_mtime,
                                "is_directory": is_dir,
                                "extension": Path(item).suffix.lower() if not is_dir else "",
                                "type": mimetypes.guess_type(item_path)[0] if not is_dir else "folder",
                                "icon": db_manager.get_file_icon(item_path, is_dir),
                                "permissions": oct(stat_info.st_mode)[-3:],
                                "size_formatted": db_manager.format_file_size(stat_info.st_size),
                                "modified_formatted": datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y/%m/%d %H:%M")
                            })
                        except Exception as e:
                            logger.error(f"Error getting file info for {item_path}: {e}")
                            continue
                    
                    # Sort results
                    if request.sort_by in ['name', 'size', 'modified']:
                        reverse = request.sort_order.lower() == 'desc'
                        files.sort(key=lambda x: x[request.sort_by], reverse=reverse)
                        
                except Exception as e:
                    logger.error(f"Error listing directory {request.path}: {e}")
        
        return {
            "files": files, 
            "total": len(files),
            "query": request.search,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/copy")
async def start_copy(request: CopyRequest, background_tasks: BackgroundTasks):
    """Start enhanced copy operation"""
    try:
        task_id = file_ops.start_copy_task(
            request.source_files, 
            request.destination,
            request.options or {}
        )
        
        # Broadcast task start
        await manager.broadcast({
            "type": "task_started",
            "data": {"task_id": task_id, "type": "copy"}
        })
        
        return {
            "success": True, 
            "task_id": task_id,
            "message": "Copy operation started successfully"
        }
    except Exception as e:
        logger.error(f"Error starting copy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def get_tasks():
    """Get all active tasks with enhanced info"""
    # Remove non-serializable items
    serializable_tasks = {}
    for task_id, task in file_ops.active_tasks.items():
        serializable_tasks[task_id] = {k: v for k, v in task.items() if k != "future"}
    
    return {
        "active_tasks": serializable_tasks,
        "total_active": len(serializable_tasks),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/tasks/{task_id}/control")
async def control_task(task_id: str, action: str):
    """Enhanced task control"""
    success = file_ops.control_task(task_id, action)
    
    if success:
        # Broadcast task control
        await manager.broadcast({
            "type": "task_controlled",
            "data": {"task_id": task_id, "action": action}
        })
        
        return {"success": True, "message": f"Task {action} successful"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.post("/api/settings")
async def save_settings(settings: SettingsBatch):
    """Save multiple settings at once"""
    try:
        saved_count = 0
        for key, value in settings.settings.items():
            if db_manager.save_setting(key, value):
                saved_count += 1
        
        # Broadcast settings update
        await manager.broadcast({
            "type": "settings_updated",
            "data": settings.settings
        })
        
        return {
            "success": True, 
            "saved_count": saved_count,
            "total_settings": len(settings.settings)
        }
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings")
async def get_all_settings():
    """Get all settings with enhanced structure"""
    try:
        return {
            "ui_settings": {
                "theme": db_manager.load_setting("ui.theme", "dark"),
                "language": db_manager.load_setting("ui.language", "fa"),
                "notifications": db_manager.load_setting("ui.notifications", True),
                "show_hidden_files": db_manager.load_setting("ui.show_hidden_files", False),
                "compact_view": db_manager.load_setting("ui.compact_view", False),
                "auto_refresh": db_manager.load_setting("ui.auto_refresh", True),
                "refresh_interval": db_manager.load_setting("ui.refresh_interval", 5000)
            },
            "file_operation_settings": {
                "auto_resume": db_manager.load_setting("file_operations.auto_resume", True),
                "verify_copy": db_manager.load_setting("file_operations.verify_copy", True),
                "preserve_timestamps": db_manager.load_setting("file_operations.preserve_timestamps", True),
                "skip_existing": db_manager.load_setting("file_operations.skip_existing", False),
                "create_log": db_manager.load_setting("file_operations.create_log", True),
                "copy_subdirectories": db_manager.load_setting("file_operations.copy_subdirectories", True),
                "show_progress": db_manager.load_setting("file_operations.show_progress", True)
            },
            "advanced_settings": {
                "max_parallel_copies": db_manager.load_setting("advanced.max_parallel_copies", 3),
                "auto_index": db_manager.load_setting("advanced.auto_index", True),
                "cache_enabled": db_manager.load_setting("advanced.cache_enabled", True),
                "log_level": db_manager.load_setting("advanced.log_level", "INFO"),
                "websocket_enabled": db_manager.load_setting("advanced.websocket_enabled", True)
            },
            "notification_settings": {
                "enabled": db_manager.load_setting("notifications.enabled", True),
                "sound": db_manager.load_setting("notifications.sound", True),
                "desktop": db_manager.load_setting("notifications.desktop", False),
                "task_completion": db_manager.load_setting("notifications.task_completion", True),
                "errors": db_manager.load_setting("notifications.errors", True)
            }
        }
    except Exception as e:
        logger.error(f"Error getting all settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/index/{drive_path:path}")
async def index_drive(drive_path: str, background_tasks: BackgroundTasks):
    """Index a drive in background"""
    def index_task():
        try:
            if not os.path.exists(drive_path):
                return {"error": "Drive not found"}
            
            indexed_count = db_manager.index_directory(drive_path, drive_path)
            
            # Broadcast indexing complete
            asyncio.create_task(manager.broadcast({
                "type": "indexing_complete",
                "data": {"drive": drive_path, "indexed_files": indexed_count}
            }))
            
        except Exception as e:
            logger.error(f"Error indexing drive {drive_path}: {e}")
    
    background_tasks.add_task(index_task)
    return {"message": "Indexing started", "drive": drive_path}

# Enhanced WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, client_id)
                
                elif message.get("type") == "subscribe":
                    # Subscribe to specific updates
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "data": message.get("data", {})
                    }, client_id)
                
                elif message.get("type") == "get_status":
                    # Send current status
                    await manager.send_personal_message({
                        "type": "status",
                        "data": {
                            "active_tasks": len(file_ops.active_tasks),
                            "connected_clients": len(manager.active_connections)
                        }
                    }, client_id)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON"
                }, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# Serve static files
app.mount("/static", StaticFiles(directory="web"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)