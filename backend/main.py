"""
Persian File Copier Pro - Modern FastAPI Backend
🚀 Modern, efficient, and scalable backend
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import os
import sys
import shutil
import psutil
import sqlite3
import threading
import time
from pathlib import Path
from datetime import datetime
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Persian File Copier Pro",
    description="مدیریت فایل‌های حرفه‌ای با رابط کاربری مدرن",
    version="2.0.0"
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
active_tasks: Dict[str, Dict] = {}
config_data: Dict = {}
db_path = "file_cache.db"

# Pydantic Models
class FileInfo(BaseModel):
    path: str
    name: str
    size: int
    modified: float
    is_directory: bool
    extension: Optional[str] = None

class CopyRequest(BaseModel):
    source_files: List[str]
    destination: str

class SettingsUpdate(BaseModel):
    key: str
    value: Any

class SearchRequest(BaseModel):
    path: str = "all"
    search: str = ""
    format_filter: str = "همه فرمت‌ها"
    limit: int = 100
    offset: int = 0

# Database Manager
class DatabaseManager:
    def __init__(self, db_file: str = "file_cache.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
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
                indexed_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_drive ON files(drive)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_name ON files(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension)')
        
        conn.commit()
        conn.close()
    
    def save_setting(self, key: str, value: Any):
        """Save setting to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, json.dumps(value))
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

    def search_files(self, search_term: str = "", format_filter: str = "همه فرمت‌ها", limit: int = 100, offset: int = 0):
        """Search files in database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            query = "SELECT path, name, size, modified, is_directory, extension FROM files WHERE 1=1"
            params = []
            
            if search_term:
                query += " AND name LIKE ?"
                params.append(f"%{search_term}%")
            
            if format_filter != "همه فرمت‌ها":
                query += " AND extension = ?"
                params.append(format_filter.lower())
            
            query += " ORDER BY name LIMIT ? OFFSET ?"
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
                    "extension": row[5] or ""
                })
            
            return files
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []
        finally:
            conn.close()

# Initialize database
db_manager = DatabaseManager()

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# File Operations Manager
class FileOperationsManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.active_tasks = {}

    def start_copy_task(self, source_files: List[str], destination: str) -> str:
        """Start a copy task"""
        task_id = str(uuid.uuid4())
        
        task_info = {
            "id": task_id,
            "type": "copy",
            "source_files": source_files,
            "destination": destination,
            "status": "running",
            "progress": 0,
            "total_files": len(source_files),
            "copied_files": 0,
            "current_file": "",
            "speed": 0,
            "eta": 0,
            "created_at": time.time()
        }
        
        self.active_tasks[task_id] = task_info
        
        # Submit task to executor
        future = self.executor.submit(self._copy_files, task_id, source_files, destination)
        task_info["future"] = future
        
        return task_id

    def _copy_files(self, task_id: str, source_files: List[str], destination: str):
        """Copy files with progress tracking"""
        task = self.active_tasks.get(task_id)
        if not task:
            return

        try:
            os.makedirs(destination, exist_ok=True)
            
            for i, source_file in enumerate(source_files):
                if task.get("cancelled"):
                    break
                
                if not os.path.exists(source_file):
                    continue
                
                filename = os.path.basename(source_file)
                dest_path = os.path.join(destination, filename)
                
                task["current_file"] = filename
                task["copied_files"] = i
                task["progress"] = int((i / len(source_files)) * 100)
                
                # Broadcast progress
                asyncio.create_task(self._broadcast_task_update(task_id))
                
                # Copy file
                try:
                    if os.path.isdir(source_file):
                        shutil.copytree(source_file, dest_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_file, dest_path)
                except Exception as e:
                    logger.error(f"Error copying {source_file}: {e}")
                    continue
            
            task["status"] = "completed"
            task["progress"] = 100
            task["copied_files"] = len(source_files)
            
        except Exception as e:
            logger.error(f"Error in copy task {task_id}: {e}")
            task["status"] = "error"
            task["error"] = str(e)
        
        # Final broadcast
        asyncio.create_task(self._broadcast_task_update(task_id))

    async def _broadcast_task_update(self, task_id: str):
        """Broadcast task update to all connected clients"""
        task = self.active_tasks.get(task_id)
        if task:
            # Remove non-serializable items
            broadcast_task = {k: v for k, v in task.items() if k != "future"}
            await manager.broadcast({
                "type": "task_update",
                "data": broadcast_task
            })

file_ops = FileOperationsManager()

# API Routes
@app.get("/")
async def read_root():
    return {"message": "Persian File Copier Pro API", "version": "2.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/drives")
async def get_drives():
    """Get available drives"""
    drives = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            drives.append({
                "path": partition.mountpoint,
                "name": partition.device,
                "total_space": usage.total,
                "free_space": usage.free,
                "used_space": usage.used,
                "filesystem": partition.fstype
            })
        except Exception as e:
            logger.error(f"Error getting drive info for {partition.mountpoint}: {e}")
    
    return drives

@app.post("/api/search")
async def search_files(request: SearchRequest):
    """Search files"""
    try:
        if request.path == "all":
            # Search in database
            files = db_manager.search_files(
                search_term=request.search,
                format_filter=request.format_filter,
                limit=request.limit,
                offset=request.offset
            )
        else:
            # Direct filesystem search
            files = []
            if os.path.exists(request.path) and os.path.isdir(request.path):
                try:
                    for item in os.listdir(request.path)[:request.limit]:
                        item_path = os.path.join(request.path, item)
                        if request.search and request.search.lower() not in item.lower():
                            continue
                        
                        try:
                            stat = os.stat(item_path)
                            files.append({
                                "path": item_path,
                                "name": item,
                                "size": stat.st_size,
                                "modified": stat.st_mtime,
                                "is_directory": os.path.isdir(item_path),
                                "extension": Path(item).suffix.lower() if not os.path.isdir(item_path) else ""
                            })
                        except Exception as e:
                            logger.error(f"Error getting file info for {item_path}: {e}")
                            continue
                except Exception as e:
                    logger.error(f"Error listing directory {request.path}: {e}")
        
        return {"files": files, "total": len(files)}
        
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/copy")
async def start_copy(request: CopyRequest, background_tasks: BackgroundTasks):
    """Start copy operation"""
    try:
        task_id = file_ops.start_copy_task(request.source_files, request.destination)
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"Error starting copy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def get_tasks():
    """Get all active tasks"""
    # Remove non-serializable items
    serializable_tasks = {}
    for task_id, task in file_ops.active_tasks.items():
        serializable_tasks[task_id] = {k: v for k, v in task.items() if k != "future"}
    
    return serializable_tasks

@app.post("/api/tasks/{task_id}/control")
async def control_task(task_id: str, action: str):
    """Control a task (pause/resume/cancel)"""
    task = file_ops.active_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if action == "cancel":
        task["cancelled"] = True
        task["status"] = "cancelled"
        return {"success": True}
    
    # For pause/resume, we'd need more complex implementation
    return {"success": False, "message": "Action not implemented yet"}

@app.post("/api/settings")
async def save_setting(setting: SettingsUpdate):
    """Save a setting"""
    try:
        success = db_manager.save_setting(setting.key, setting.value)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error saving setting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings/{key}")
async def get_setting(key: str, default: Optional[str] = None):
    """Get a setting"""
    try:
        value = db_manager.load_setting(key, default)
        return {"key": key, "value": value}
    except Exception as e:
        logger.error(f"Error getting setting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings")
async def get_all_settings():
    """Get all settings"""
    try:
        # Return default settings structure
        return {
            "ui_settings": {
                "theme": db_manager.load_setting("ui.theme", "dark"),
                "language": db_manager.load_setting("ui.language", "fa"),
                "notifications": db_manager.load_setting("ui.notifications", True),
                "show_hidden_files": db_manager.load_setting("ui.show_hidden_files", False),
                "compact_view": db_manager.load_setting("ui.compact_view", False)
            },
            "file_operation_settings": {
                "auto_resume": db_manager.load_setting("file_operations.auto_resume", True),
                "verify_copy": db_manager.load_setting("file_operations.verify_copy", True),
                "preserve_timestamps": db_manager.load_setting("file_operations.preserve_timestamps", True),
                "skip_existing": db_manager.load_setting("file_operations.skip_existing", False),
                "create_log": db_manager.load_setting("file_operations.create_log", True)
            },
            "advanced_settings": {
                "max_parallel_copies": db_manager.load_setting("advanced.max_parallel_copies", 3),
                "auto_index": db_manager.load_setting("advanced.auto_index", True),
                "cache_enabled": db_manager.load_setting("advanced.cache_enabled", True)
            }
        }
    except Exception as e:
        logger.error(f"Error getting all settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle incoming WebSocket messages
                await manager.send_personal_message({
                    "type": "response",
                    "data": f"Received: {message}"
                }, websocket)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "data": "Invalid JSON"
                }, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)