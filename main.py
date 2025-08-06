"""
Persian File Copier Pro - Enhanced Backend
🚀 Ultimate file management with advanced features
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
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
import hashlib
import re
import platform
import subprocess
import stat
import pwd
import grp

# Windows specific imports - handle gracefully on other platforms
try:
    import win32file
    import win32api
    import win32con
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    # Create dummy constants for non-Windows systems
    class DummyWin32:
        DRIVE_REMOVABLE = 2
        DRIVE_FIXED = 3
        DRIVE_REMOTE = 4
    win32con = DummyWin32()
from pathlib import Path
from datetime import datetime
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
import mimetypes
import stat
import aiofiles
from collections import defaultdict

# Import configuration
from config import *

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_CONFIG['level']),
    format=LOG_CONFIG['format'],
    handlers=[
        logging.FileHandler('persian_file_copier.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_NAME,
    description=f"{COMPANY_NAME} - {APP_EDITION}",
    version=APP_VERSION,
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
active_connections: Dict[str, WebSocket] = {}
db_path = "persian_file_cache.db"

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
    drive_type: Optional[str] = None

class DriveInfo(BaseModel):
    path: str
    name: str
    label: Optional[str] = None
    total_space: int
    free_space: int
    used_space: int
    filesystem: str
    drive_type: str
    device_type: str
    is_ready: bool = True
    speed_class: Optional[str] = None

class CopyRequest(BaseModel):
    source_files: List[str]
    destination: str
    options: Optional[Dict[str, Any]] = {}

class TaskInfo(BaseModel):
    task_id: str
    type: str
    status: str
    progress: int
    current_file: str
    speed: float
    eta: int
    total_files: int
    copied_files: int
    total_size: int
    copied_size: int
    errors: List[str]
    source_device: Optional[str] = None
    dest_device: Optional[str] = None

class ScanSettings(BaseModel):
    max_depth: int = 10
    max_files: int = 50000
    include_hidden: bool = False
    include_system: bool = False
    scan_subdirectories: bool = True
    file_types: Optional[List[str]] = None

# Enhanced Device Detector with better permissions
class DeviceDetector:
    def __init__(self):
        self.platform = platform.system().lower()
    
    def detect_device_type(self, drive_path: str) -> str:
        """Enhanced device detection with proper permissions"""
        try:
            if self.platform == "windows":
                return self._detect_windows_device(drive_path)
            else:
                return self._detect_linux_device(drive_path)
        except Exception as e:
            logger.warning(f"Error detecting device type for {drive_path}: {e}")
            return "unknown"
    
    def _detect_windows_device(self, drive_path: str) -> str:
        """Windows device detection with admin privileges"""
        if not WINDOWS_AVAILABLE:
            return "unknown"
        
        try:
            drive_type = win32file.GetDriveType(drive_path)
            if drive_type == win32con.DRIVE_REMOVABLE:
                return "usb"
            elif drive_type == win32con.DRIVE_FIXED:
                return "hdd"
            elif drive_type == win32con.DRIVE_REMOTE:
                return "network"
            else:
                return "unknown"
        except Exception as e:
            logger.error(f"Windows device detection error: {e}")
            return "unknown"
    
    def _detect_linux_device(self, drive_path: str) -> str:
        """Linux device detection with proper permissions"""
        try:
            # Check if it's a mount point
            if os.path.ismount(drive_path):
                # Get device info
                stat_info = os.stat(drive_path)
                if stat.S_ISBLK(stat_info.st_mode):
                    return "hdd"
                else:
                    # Check if it's USB by looking at /proc/mounts
                    with open('/proc/mounts', 'r') as f:
                        mounts = f.read()
                        if drive_path in mounts and 'usb' in mounts.lower():
                            return "usb"
                        elif 'ssd' in mounts.lower():
                            return "ssd"
                        else:
                            return "hdd"
            else:
                return "unknown"
        except Exception as e:
            logger.error(f"Linux device detection error: {e}")
            return "unknown"
    
    def _is_usb3(self, drive_path: str) -> bool:
        """Enhanced USB 3.0 detection"""
        try:
            if self.platform == "windows":
                return self._is_windows_usb3(drive_path)
            else:
                return self._is_linux_usb3(drive_path)
        except Exception as e:
            logger.warning(f"USB 3.0 detection error: {e}")
            return False
    
    def _is_windows_usb3(self, drive_path: str) -> bool:
        """Windows USB 3.0 detection"""
        if not WINDOWS_AVAILABLE:
            return False
        
        try:
            # Use WMI to check USB version
            import wmi
            c = wmi.WMI()
            for usb in c.Win32_USBHub():
                if drive_path.lower() in usb.DeviceID.lower():
                    return "3.0" in usb.DeviceID or "USB3" in usb.DeviceID
            return False
        except Exception as e:
            logger.warning(f"Windows USB 3.0 detection error: {e}")
            return False
    
    def _is_linux_usb3(self, drive_path: str) -> bool:
        """Linux USB 3.0 detection"""
        try:
            # Check /sys/bus/usb/devices for USB 3.0
            for device in os.listdir('/sys/bus/usb/devices'):
                try:
                    with open(f'/sys/bus/usb/devices/{device}/speed', 'r') as f:
                        speed = f.read().strip()
                        if speed == '480':  # USB 3.0 speed
                            return True
                except:
                    continue
            return False
        except Exception as e:
            logger.warning(f"Linux USB 3.0 detection error: {e}")
            return False
    
    def _is_ssd(self, drive_path: str) -> bool:
        """Enhanced SSD detection"""
        try:
            if self.platform == "windows":
                return self._is_windows_ssd(drive_path)
            else:
                return self._is_linux_ssd(drive_path)
        except Exception as e:
            logger.warning(f"SSD detection error: {e}")
            return False
    
    def _is_windows_ssd(self, drive_path: str) -> bool:
        """Windows SSD detection"""
        if not WINDOWS_AVAILABLE:
            return False
        
        try:
            import wmi
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                if drive_path.lower() in disk.DeviceID.lower():
                    return "SSD" in disk.MediaType or "Solid State" in disk.MediaType
            return False
        except Exception as e:
            logger.warning(f"Windows SSD detection error: {e}")
            return False
    
    def _is_linux_ssd(self, drive_path: str) -> bool:
        """Linux SSD detection"""
        try:
            # Check /sys/block for SSD indicators
            for device in os.listdir('/sys/block'):
                try:
                    with open(f'/sys/block/{device}/queue/rotational', 'r') as f:
                        rotational = f.read().strip()
                        if rotational == '0':  # SSD indicator
                            return True
                except:
                    continue
            return False
        except Exception as e:
            logger.warning(f"Linux SSD detection error: {e}")
            return False
    
    def scan_mtp_devices(self) -> List[Dict]:
        """Enhanced MTP device scanning"""
        devices = []
        try:
            if self.platform == "windows":
                devices = self._scan_windows_mtp()
            else:
                devices = self._scan_linux_mtp()
        except Exception as e:
            logger.error(f"MTP device scanning error: {e}")
        
        return devices
    
    def _scan_windows_mtp(self) -> List[Dict]:
        """Windows MTP device scanning"""
        devices = []
        if not WINDOWS_AVAILABLE:
            return devices
        
        try:
            import wmi
            c = wmi.WMI()
            for device in c.Win32_PnPEntity():
                if "MTP" in device.Name or "Media Transfer Protocol" in device.Name:
                    devices.append({
                        "name": device.Name,
                        "id": device.DeviceID,
                        "status": device.Status
                    })
        except Exception as e:
            logger.error(f"Windows MTP scanning error: {e}")
        
        return devices
    
    def _scan_linux_mtp(self) -> List[Dict]:
        """Linux MTP device scanning"""
        devices = []
        try:
            # Use gvfs-mount to list MTP devices
            result = subprocess.run(['gvfs-mount', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'mtp://' in line:
                        devices.append({
                            "name": line.strip(),
                            "id": line.split()[0] if line.split() else "",
                            "status": "available"
                        })
        except Exception as e:
            logger.error(f"Linux MTP scanning error: {e}")
        
        return devices

# Enhanced Database Manager with better file indexing
class DatabaseManager:
    def __init__(self, db_file: str = "persian_file_cache.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database with enhanced schema"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Enhanced file cache table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS file_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        size INTEGER DEFAULT 0,
                        modified REAL DEFAULT 0,
                        is_directory BOOLEAN DEFAULT 0,
                        extension TEXT,
                        file_type TEXT,
                        permissions TEXT,
                        drive_type TEXT,
                        indexed_at REAL DEFAULT 0,
                        scan_depth INTEGER DEFAULT 0,
                        parent_path TEXT,
                        created_at REAL DEFAULT (strftime('%s', 'now'))
                    )
                ''')
                
                # Enhanced drive info table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS drive_info (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        label TEXT,
                        total_space INTEGER DEFAULT 0,
                        free_space INTEGER DEFAULT 0,
                        used_space INTEGER DEFAULT 0,
                        filesystem TEXT,
                        drive_type TEXT,
                        device_type TEXT,
                        is_ready BOOLEAN DEFAULT 1,
                        speed_class TEXT,
                        last_scan REAL DEFAULT 0,
                        created_at REAL DEFAULT (strftime('%s', 'now'))
                    )
                ''')
                
                # Task history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS task_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id TEXT UNIQUE NOT NULL,
                        task_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        source_files TEXT,
                        destination TEXT,
                        total_files INTEGER DEFAULT 0,
                        copied_files INTEGER DEFAULT 0,
                        total_size INTEGER DEFAULT 0,
                        copied_size INTEGER DEFAULT 0,
                        start_time REAL DEFAULT 0,
                        end_time REAL DEFAULT 0,
                        duration REAL DEFAULT 0,
                        errors TEXT,
                        created_at REAL DEFAULT (strftime('%s', 'now'))
                    )
                ''')
                
                # Settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        value TEXT,
                        description TEXT,
                        updated_at REAL DEFAULT (strftime('%s', 'now'))
                    )
                ''')
                
                # License table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS license (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        license_key TEXT,
                        status TEXT DEFAULT 'trial',
                        activated_at REAL,
                        expires_at REAL,
                        machine_id TEXT,
                        features TEXT,
                        created_at REAL DEFAULT (strftime('%s', 'now'))
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_path ON file_cache(path)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_parent ON file_cache(parent_path)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_drive_path ON drive_info(path)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_id ON task_history(task_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_status ON task_history(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_license_key ON license(license_key)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_license_machine ON license(machine_id)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def get_file_icon(self, file_path: str, is_directory: bool = False) -> str:
        """Enhanced file icon detection"""
        try:
            if is_directory:
                return "📁"
            
            extension = os.path.splitext(file_path)[1].lower()
            
            # Enhanced icon mapping
            icon_map = {
                # Documents
                '.pdf': '📄', '.doc': '📄', '.docx': '📄', '.txt': '📄',
                '.rtf': '📄', '.odt': '📄', '.pages': '📄',
                
                # Images
                '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
                '.bmp': '🖼️', '.tiff': '🖼️', '.svg': '🖼️', '.webp': '🖼️',
                
                # Videos
                '.mp4': '🎥', '.avi': '🎥', '.mkv': '🎥', '.mov': '🎥',
                '.wmv': '🎥', '.flv': '🎥', '.webm': '🎥', '.m4v': '🎥',
                
                # Audio
                '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.aac': '🎵',
                '.ogg': '🎵', '.wma': '🎵', '.m4a': '🎵',
                
                # Archives
                '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦',
                '.gz': '📦', '.bz2': '📦', '.xz': '📦',
                
                # Executables
                '.exe': '⚙️', '.msi': '⚙️', '.app': '⚙️', '.deb': '⚙️',
                '.rpm': '⚙️', '.dmg': '⚙️',
                
                # Code
                '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
                '.php': '🐘', '.java': '☕', '.cpp': '⚡', '.c': '⚡',
                '.json': '📋', '.xml': '📋', '.sql': '🗄️',
                
                # System
                '.sys': '🔧', '.dll': '🔧', '.so': '🔧', '.dylib': '🔧',
                '.ini': '⚙️', '.cfg': '⚙️', '.conf': '⚙️',
                
                # Data
                '.csv': '📊', '.xlsx': '📊', '.xls': '📊', '.db': '🗄️',
                '.sqlite': '🗄️', '.mdb': '🗄️'
            }
            
            return icon_map.get(extension, '📄')
            
        except Exception as e:
            logger.error(f"File icon detection error: {e}")
            return "📄"
    
    def update_drives(self, drives: List[DriveInfo]):
        """Update drive information in database"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                for drive in drives:
                    cursor.execute('''
                        INSERT OR REPLACE INTO drive_info 
                        (path, name, label, total_space, free_space, used_space, 
                         filesystem, drive_type, device_type, is_ready, speed_class, last_scan)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        drive.path, drive.name, drive.label, drive.total_space,
                        drive.free_space, drive.used_space, drive.filesystem,
                        drive.drive_type, drive.device_type, drive.is_ready,
                        drive.speed_class, time.time()
                    ))
                
                conn.commit()
                logger.info(f"Updated {len(drives)} drives in database")
                
        except Exception as e:
            logger.error(f"Drive update error: {e}")
    
    def fast_index_directory(self, directory: str, drive_info: DriveInfo, max_files: int = 10000) -> int:
        """Enhanced recursive directory indexing with permissions"""
        try:
            indexed_count = 0
            start_time = time.time()
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Clear existing entries for this directory
                cursor.execute('DELETE FROM file_cache WHERE path LIKE ?', (f"{directory}%",))
                
                for root, dirs, files in os.walk(directory):
                    try:
                        # Check permissions
                        if not os.access(root, os.R_OK):
                            logger.warning(f"No read permission for: {root}")
                            continue
                        
                        # Process directories
                        for dir_name in dirs:
                            try:
                                dir_path = os.path.join(root, dir_name)
                                if os.access(dir_path, os.R_OK):
                                    stat_info = os.stat(dir_path)
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO file_cache 
                                        (path, name, size, modified, is_directory, 
                                         permissions, drive_type, indexed_at, parent_path)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (
                                        dir_path, dir_name, 0, stat_info.st_mtime,
                                        1, oct(stat_info.st_mode)[-3:], drive_info.drive_type,
                                        time.time(), root
                                    ))
                                    indexed_count += 1
                            except Exception as e:
                                logger.warning(f"Error indexing directory {dir_name}: {e}")
                                continue
                        
                        # Process files
                        for file_name in files:
                            try:
                                file_path = os.path.join(root, file_name)
                                if os.access(file_path, os.R_OK):
                                    stat_info = os.stat(file_path)
                                    extension = os.path.splitext(file_name)[1]
                                    
                                    cursor.execute('''
                                        INSERT OR REPLACE INTO file_cache 
                                        (path, name, size, modified, is_directory, 
                                         extension, permissions, drive_type, indexed_at, parent_path)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (
                                        file_path, file_name, stat_info.st_size, stat_info.st_mtime,
                                        0, extension, oct(stat_info.st_mode)[-3:], drive_info.drive_type,
                                        time.time(), root
                                    ))
                                    indexed_count += 1
                                    
                                    if indexed_count >= max_files:
                                        logger.warning(f"Reached max files limit: {max_files}")
                                        break
                            except Exception as e:
                                logger.warning(f"Error indexing file {file_name}: {e}")
                                continue
                        
                        if indexed_count >= max_files:
                            break
                            
                    except PermissionError:
                        logger.warning(f"Permission denied for: {root}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing directory {root}: {e}")
                        continue
                
                conn.commit()
                duration = time.time() - start_time
                logger.info(f"Indexed {indexed_count} items in {duration:.2f}s for {directory}")
                
                return indexed_count
                
        except Exception as e:
            logger.error(f"Directory indexing error: {e}")
            return 0

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
        
        logger.info(f"WebSocket connected: {client_id}")
        return client_id

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.connection_data[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")

    async def broadcast(self, message: dict):
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect(client_id)

manager = ConnectionManager()

# Enhanced File Operations Manager with better permissions and scanning
class FileOperationsManager:
    def __init__(self):
        self.active_tasks = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.event_loop = None
        self.device_detector = DeviceDetector()
    
    def get_optimal_buffer_size(self, source_device: str, dest_device: str) -> int:
        """Get optimal buffer size based on device types"""
        try:
            source_type = self.device_detector.detect_device_type(source_device)
            dest_type = self.device_detector.detect_device_type(dest_device)
            
            # Enhanced buffer size mapping
            buffer_sizes = {
                ('usb', 'hdd'): 512 * 1024,      # 512KB for USB to HDD
                ('usb', 'ssd'): 1024 * 1024,     # 1MB for USB to SSD
                ('hdd', 'usb'): 512 * 1024,      # 512KB for HDD to USB
                ('hdd', 'ssd'): 2048 * 1024,     # 2MB for HDD to SSD
                ('ssd', 'usb'): 1024 * 1024,     # 1MB for SSD to USB
                ('ssd', 'hdd'): 2048 * 1024,     # 2MB for SSD to HDD
                ('ssd', 'ssd'): 4096 * 1024,     # 4MB for SSD to SSD
                ('network', 'hdd'): 256 * 1024,   # 256KB for network to HDD
                ('network', 'ssd'): 512 * 1024,   # 512KB for network to SSD
            }
            
            return buffer_sizes.get((source_type, dest_type), 1024 * 1024)  # Default 1MB
            
        except Exception as e:
            logger.warning(f"Error getting optimal buffer size: {e}")
            return 1024 * 1024  # Default 1MB
    
    def start_copy_task(self, source_files: List[str], destination: str, options: Dict = None) -> str:
        """Start enhanced copy task with device optimization"""
        try:
            task_id = str(uuid.uuid4())
            
            # Validate source files
            valid_files = []
            total_size = 0
            for file_path in source_files:
                if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                    valid_files.append(file_path)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
                else:
                    logger.warning(f"File not accessible: {file_path}")
            
            if not valid_files:
                raise ValueError("هیچ فایل معتبری برای کپی یافت نشد")
            
            # Create destination directory if needed
            if options.get("create_destination", True):
                os.makedirs(destination, exist_ok=True)
            
            # Get device types for optimization
            source_device = os.path.dirname(valid_files[0]) if valid_files else ""
            dest_device = destination
            
            # Initialize task
            self.active_tasks[task_id] = {
                "task_id": task_id,
                "type": "copy",
                "status": "preparing",
                "progress": 0,
                "current_file": "",
                "speed": 0,
                "eta": 0,
                "total_files": len(valid_files),
                "copied_files": 0,
                "total_size": total_size,
                "copied_size": 0,
                "errors": [],
                "source_device": source_device,
                "dest_device": dest_device,
                "source_files": valid_files,
                "destination": destination,
                "options": options or {},
                "buffer_size": self.get_optimal_buffer_size(source_device, dest_device),
                "start_time": time.time(),
                "future": None
            }
            
            # Start copy operation in background
            future = self.executor.submit(self._copy_files_optimized, task_id)
            self.active_tasks[task_id]["future"] = future
            
            logger.info(f"Started copy task {task_id} with {len(valid_files)} files")
            return task_id
            
        except Exception as e:
            logger.error(f"Error starting copy task: {e}")
            raise
    
    def _copy_files_optimized(self, task_id: str):
        """Optimized copy with device-specific settings and pause/cancel support"""
        try:
            task = self.active_tasks[task_id]
            task["status"] = "running"
            
            source_files = task["source_files"]
            destination = task["destination"]
            buffer_size = task["buffer_size"]
            
            logger.info(f"Starting copy task {task_id} with {len(source_files)} files to {destination}")
            
            for i, source_file in enumerate(source_files):
                if task.get("cancelled"):
                    logger.info(f"Copy task {task_id} cancelled")
                    break
                
                if task.get("paused"):
                    logger.info(f"Copy task {task_id} paused")
                    while task.get("paused") and not task.get("cancelled"):
                        time.sleep(0.1)
                
                try:
                    filename = os.path.basename(source_file)
                    task["current_file"] = filename
                    
                    if os.path.isdir(source_file):
                        # Copy directory
                        dest_path = os.path.join(destination, filename)
                        logger.info(f"Copying directory: {source_file} -> {dest_path}")
                        shutil.copytree(source_file, dest_path, dirs_exist_ok=True)
                    else:
                        # Copy file with optimization
                        dest_path = os.path.join(destination, filename)
                        logger.info(f"Copying file: {source_file} -> {dest_path}")
                        self._optimized_file_copy(source_file, dest_path, buffer_size)
                    
                    task["copied_files"] += 1
                    task["progress"] = int((i + 1) / len(source_files) * 100)
                    
                    # Update speed and ETA
                    elapsed_time = time.time() - task["start_time"]
                    if elapsed_time > 0:
                        task["speed"] = task["copied_size"] / elapsed_time
                        remaining_files = len(source_files) - (i + 1)
                        task["eta"] = int(remaining_files * elapsed_time / (i + 1)) if i > 0 else 0
                    
                    # Schedule broadcast update
                    self._schedule_broadcast(task_id)
                    
                except Exception as e:
                    error_msg = f"Error copying {filename}: {str(e)}"
                    logger.error(error_msg)
                    task["errors"].append(error_msg)
                    continue
            
            # Mark task as completed
            if not task.get("cancelled"):
                task["status"] = "completed"
                task["progress"] = 100
                logger.info(f"Copy task {task_id} completed successfully")
            else:
                task["status"] = "cancelled"
                logger.info(f"Copy task {task_id} cancelled")
            
            # Final broadcast
            self._schedule_broadcast(task_id)
            
        except Exception as e:
            logger.error(f"Error in copy task {task_id}: {e}")
            task["status"] = "failed"
            task["errors"].append(str(e))
            self._schedule_broadcast(task_id)
    
    def _optimized_file_copy(self, source: str, destination: str, buffer_size: int):
        """Optimized file copy with custom buffer size"""
        try:
            with open(source, 'rb') as src, open(destination, 'wb') as dst:
                while True:
                    chunk = src.read(buffer_size)
                    if not chunk:
                        break
                    dst.write(chunk)
            
            # Preserve timestamps if requested
            shutil.copystat(source, destination)
            
        except Exception as e:
            logger.error(f"Error copying file {source}: {e}")
            raise
    
    def _schedule_broadcast(self, task_id: str):
        """Schedule task update broadcast"""
        try:
            if self.event_loop and not self.event_loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    self._broadcast_task_update(task_id), 
                    self.event_loop
                )
        except Exception as e:
            logger.debug(f"Broadcast scheduling failed: {e}")
    
    async def _broadcast_task_update(self, task_id: str):
        """Broadcast task update to all connected clients"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                await manager.broadcast({
                    "type": "task_update",
                    "data": {
                        "task_id": task_id,
                        "status": task["status"],
                        "progress": task["progress"],
                        "current_file": task["current_file"],
                        "speed": task["speed"],
                        "eta": task["eta"],
                        "total_files": task["total_files"],
                        "copied_files": task["copied_files"],
                        "total_size": task["total_size"],
                        "copied_size": task["copied_size"],
                        "errors": task["errors"]
                    }
                })
        except Exception as e:
            logger.error(f"Error broadcasting task update: {e}")
    
    def _scan_directory_enhanced(self, task_id: str, directory: str, drive_info: DriveInfo, scan_settings: ScanSettings):
        """Enhanced directory scanning with advanced options"""
        try:
            task = self.active_tasks[task_id]
            task["status"] = "running"
            
            scanned_count = 0
            total_size = 0
            start_time = time.time()
            
            logger.info(f"Starting enhanced scan of {directory}")
            
            for root, dirs, files in os.walk(directory):
                if task.get("cancelled"):
                    break
                
                if task.get("paused"):
                    while task.get("paused") and not task.get("cancelled"):
                        time.sleep(0.1)
                
                # Check scan depth
                depth = root[len(directory):].count(os.sep)
                if depth > scan_settings.max_depth:
                    continue
                
                # Filter directories based on settings
                if not scan_settings.include_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                if not scan_settings.include_system:
                    dirs[:] = [d for d in dirs if d not in ['System Volume Information', '$Recycle.Bin', 'Thumbs.db']]
                
                # Process files
                for filename in files:
                    if scanned_count >= scan_settings.max_files:
                        logger.warning(f"Reached max files limit: {scan_settings.max_files}")
                        break
                    
                    try:
                        file_path = os.path.join(root, filename)
                        
                        # Check permissions
                        if not os.access(file_path, os.R_OK):
                            continue
                        
                        # Filter hidden files
                        if not scan_settings.include_hidden and filename.startswith('.'):
                            continue
                        
                        # Filter by file type if specified
                        if scan_settings.file_types:
                            ext = os.path.splitext(filename)[1].lower()
                            if ext not in scan_settings.file_types:
                                continue
                        
                        # Get file info
                        stat_info = os.stat(file_path)
                        file_size = stat_info.st_size
                        total_size += file_size
                        
                        # Update task progress
                        scanned_count += 1
                        task["scanned_files"] = scanned_count
                        task["scanned_size"] = total_size
                        task["current_file"] = filename
                        
                        if scanned_count % 100 == 0:
                            elapsed_time = time.time() - start_time
                            if elapsed_time > 0:
                                task["speed"] = scanned_count / elapsed_time
                            
                            task["progress"] = min(95, int(scanned_count / scan_settings.max_files * 100))
                            self._schedule_broadcast(task_id)
                        
                    except Exception as e:
                        error_msg = f"Error scanning {filename}: {str(e)}"
                        task["errors"].append(error_msg)
                        continue
                
                if scanned_count >= scan_settings.max_files:
                    break
            
            # Complete task
            if not task.get("cancelled"):
                task["status"] = "completed"
                task["progress"] = 100
                task["total_files"] = scanned_count
                task["total_size"] = total_size
                logger.info(f"Scan completed: {scanned_count} files, {total_size} bytes")
            else:
                task["status"] = "cancelled"
            
            self._schedule_broadcast(task_id)
            
        except Exception as e:
            logger.error(f"Error in enhanced scan: {e}")
            task["status"] = "failed"
            task["errors"].append(str(e))
            self._schedule_broadcast(task_id)

# Initialize managers
device_detector = DeviceDetector()
db_manager = DatabaseManager()
manager = ConnectionManager()
file_ops = FileOperationsManager()

# License Manager
class LicenseManager:
    def __init__(self):
        self.is_pro = False
        self.license_key = None
        self.activation_date = None
        self.expiry_date = None
        self.machine_id = self._get_machine_id()
        self.trial_days_left = 30
        self.check_license()
    
    def _get_machine_id(self) -> str:
        """Generate unique machine ID"""
        try:
            # Use MAC address and hostname for unique ID
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0,2*6,2)][::-1])
            hostname = platform.node()
            return hashlib.md5(f"{mac}-{hostname}".encode()).hexdigest()[:16]
        except:
            return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]
    
    def _load_license_from_db(self):
        """Load license from database"""
        try:
            with sqlite3.connect(db_manager.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM license ORDER BY id DESC LIMIT 1')
                result = cursor.fetchone()
                
                if result:
                    return {
                        'license_key': result[1],
                        'status': result[2],
                        'activated_at': result[3],
                        'expires_at': result[4],
                        'machine_id': result[5],
                        'features': result[6]
                    }
        except Exception as e:
            logger.error(f"Error loading license: {e}")
        return None
    
    def _save_license_to_db(self, license_data):
        """Save license to database"""
        try:
            with sqlite3.connect(db_manager.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO license 
                    (license_key, status, activated_at, expires_at, machine_id, features)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    license_data['license_key'],
                    license_data['status'],
                    license_data.get('activated_at'),
                    license_data.get('expires_at'),
                    license_data.get('machine_id'),
                    license_data.get('features', 'pro')
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving license: {e}")
            return False
    
    def generate_license_key(self, license_type='pro', days=365) -> str:
        """Generate a new license key"""
        import secrets, base64
        
        # Generate random key components
        prefix = "PFC-PRO" if license_type == 'pro' else "PFC-STD"
        random_part = secrets.token_hex(8).upper()
        year = str(datetime.now().year)
        
        # Create license string
        license_data = f"{prefix}-{year}-{random_part}"
        
        # Add checksum
        checksum = hashlib.md5(license_data.encode()).hexdigest()[:4].upper()
        final_key = f"{license_data}-{checksum}"
        
        return final_key
    
    def validate_license_key(self, license_key: str) -> bool:
        """Validate license key format and checksum"""
        try:
            if not license_key or len(license_key) < 20:
                return False
            
            # Split key parts
            parts = license_key.split('-')
            if len(parts) < 4:
                return False
            
            # Check prefix
            if parts[0] not in ['PFC', 'PERSIAN', 'FILECOPIER']:
                return False
            
            # Verify checksum
            license_part = '-'.join(parts[:-1])
            expected_checksum = hashlib.md5(license_part.encode()).hexdigest()[:4].upper()
            
            return parts[-1].upper() == expected_checksum
            
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return False
    
    def activate_license(self, license_key: str) -> dict:
        """Activate a license key"""
        try:
            # Validate format first
            if not self.validate_license_key(license_key):
                return {
                    'success': False,
                    'message': 'فرمت کلید لایسنس نامعتبر است'
                }
            
            # Check if already activated on this machine
            existing = self._load_license_from_db()
            if existing and existing['license_key'] == license_key:
                if existing['machine_id'] == self.machine_id:
                    return {
                        'success': True,
                        'message': 'لایسنس قبلاً فعال شده است'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'این لایسنس روی دستگاه دیگری فعال شده است'
                    }
            
            # Activate new license
            activation_time = int(time.time())
            expiry_time = activation_time + (365 * 24 * 60 * 60)  # 1 year
            
            license_data = {
                'license_key': license_key,
                'status': 'active',
                'activated_at': activation_time,
                'expires_at': expiry_time,
                'machine_id': self.machine_id,
                'features': 'pro'
            }
            
            if self._save_license_to_db(license_data):
                self.license_key = license_key
                self.is_pro = True
                self.activation_date = activation_time
                self.expiry_date = expiry_time
                
                return {
                    'success': True,
                    'message': 'لایسنس با موفقیت فعال شد'
                }
            else:
                return {
                    'success': False,
                    'message': 'خطا در ذخیره لایسنس'
                }
                
        except Exception as e:
            logger.error(f"License activation error: {e}")
            return {
                'success': False,
                'message': f'خطا در فعال‌سازی: {str(e)}'
            }
    
    def check_license(self):
        """Check current license status"""
        try:
            license_data = self._load_license_from_db()
            
            if not license_data:
                # No license, start trial
                self.is_pro = False
                self._start_trial()
                return
            
            # Check if license is valid
            current_time = int(time.time())
            
            if license_data['status'] == 'active':
                if license_data['expires_at'] and current_time > license_data['expires_at']:
                    # License expired
                    self.is_pro = False
                    self._mark_license_expired()
                elif license_data['machine_id'] != self.machine_id:
                    # Wrong machine
                    self.is_pro = False
                else:
                    # Valid license
                    self.is_pro = True
                    self.license_key = license_data['license_key']
                    self.activation_date = license_data['activated_at']
                    self.expiry_date = license_data['expires_at']
            else:
                # Invalid status
                self.is_pro = False
                
        except Exception as e:
            logger.error(f"License check error: {e}")
            self.is_pro = False
    
    def _start_trial(self):
        """Start trial period"""
        try:
            # Check if trial was already started
            with sqlite3.connect(db_manager.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO license (license_key, status, activated_at, machine_id)
                    VALUES (?, ?, ?, ?)
                ''', ('TRIAL', 'trial', int(time.time()), self.machine_id))
                conn.commit()
            
            # Calculate remaining trial days
            license_data = self._load_license_from_db()
            if license_data and license_data['activated_at']:
                days_passed = (int(time.time()) - license_data['activated_at']) // (24 * 60 * 60)
                self.trial_days_left = max(0, 30 - days_passed)
            
        except Exception as e:
            logger.error(f"Trial start error: {e}")
    
    def _mark_license_expired(self):
        """Mark license as expired"""
        try:
            with sqlite3.connect(db_manager.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE license SET status = ? WHERE machine_id = ?', 
                             ('expired', self.machine_id))
                conn.commit()
        except Exception as e:
            logger.error(f"License expiry marking error: {e}")
    
    def get_license_info(self) -> dict:
        """Get current license information"""
        return {
            'is_pro': self.is_pro,
            'license_key': self.license_key,
            'machine_id': self.machine_id,
            'trial_days_left': self.trial_days_left,
            'activation_date': self.activation_date,
            'expiry_date': self.expiry_date,
            'status': 'pro' if self.is_pro else ('trial' if self.trial_days_left > 0 else 'expired')
        }
    
    def get_features(self):
        """Get available features based on license"""
        if self.is_pro:
            return FEATURES['pro_version']
        return FEATURES['free_version']

# Drive scanner with auto-detection
class DriveScanner:
    def __init__(self):
        self.last_drives = set()
        
    async def scan_drives(self) -> List[DriveInfo]:
        """Enhanced drive scanning with device detection"""
        drives = []
        
        try:
            # Get system drives
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    device_type = device_detector.detect_device_type(partition.mountpoint)
                    
                    # Get drive label on Windows
                    label = None
                    if platform.system() == "Windows" and WINDOWS_AVAILABLE:
                        try:
                            label = win32api.GetVolumeInformation(partition.mountpoint)[0]
                        except Exception:
                            pass
                    
                    drive_info = DriveInfo(
                        path=partition.mountpoint,
                        name=partition.device,
                        label=label,
                        total_space=usage.total,
                        free_space=usage.free,
                        used_space=usage.used,
                        filesystem=partition.fstype,
                        drive_type="local",
                        device_type=device_type,
                        is_ready=True
                    )
                    drives.append(drive_info)
                    
                except Exception as e:
                    logger.error(f"Error scanning drive {partition.mountpoint}: {e}")
            
            # Add MTP devices
            mtp_devices = device_detector.scan_mtp_devices()
            for device in mtp_devices:
                drive_info = DriveInfo(
                    path=f"MTP:\\{device['id']}",
                    name=device['name'],
                    label=device['name'],
                    total_space=0,
                    free_space=0,
                    used_space=0,
                    filesystem="MTP",
                    drive_type="mtp",
                    device_type="mtp",
                    is_ready=device['status'] == 'OK'
                )
                drives.append(drive_info)
            
            # Update database
            db_manager.update_drives(drives)
            
            # Check for new drives
            current_drives = {drive.path for drive in drives}
            new_drives = current_drives - self.last_drives
            
            if new_drives:
                # Broadcast new drives detected
                await manager.broadcast({
                    "type": "new_drives_detected",
                    "data": {"drives": [d.path for d in drives if d.path in new_drives]}
                })
                
                # Auto-index new drives
                for drive in drives:
                    if drive.path in new_drives and drive.is_ready:
                        asyncio.create_task(self._auto_index_drive(drive))
            
            self.last_drives = current_drives
            
        except Exception as e:
            logger.error(f"Error scanning drives: {e}")
        
        return drives
    
    async def _auto_index_drive(self, drive: DriveInfo):
        """Auto-index new drive in background"""
        try:
            if drive.drive_type != "mtp":  # Skip MTP for now
                indexed_count = db_manager.fast_index_directory(drive.path, drive)
                await manager.broadcast({
                    "type": "drive_indexed",
                    "data": {"drive": drive.path, "count": indexed_count}
                })
        except Exception as e:
            logger.error(f"Error auto-indexing drive {drive.path}: {e}")

# Initialize remaining managers
license_manager = LicenseManager()
drive_scanner = DriveScanner()

# API Routes
@app.get("/")
async def serve_index():
    """Serve the main interface"""
    index_path = Path("index.html")
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    else:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>{APP_NAME}</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🌟 {APP_NAME}</h1>
            <p>{COMPANY_NAME}</p>
            <p>نسخه {APP_VERSION}</p>
            <p>لطفاً فایل index.html را در پوشه اصلی قرار دهید.</p>
        </body>
        </html>
        """)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections),
        "active_tasks": len(file_ops.active_tasks),
        "license": "pro" if license_manager.is_pro else "free"
    }

@app.get("/api/drives")
async def get_drives():
    """Get enhanced drives with real-time detection"""
    drives = await drive_scanner.scan_drives()
    return {"drives": drives, "timestamp": datetime.now().isoformat()}

@app.post("/api/search")
async def search_files(request: dict):
    """Ultra-fast file search with improved filtering"""
    try:
        search_term = request.get("search", "").strip()
        drive_filter = request.get("drive", "all")
        type_filter = request.get("type", "all")
        fast_mode = request.get("fast_mode", False)
        limit = min(request.get("limit", 500), 1000)  # Cap at 1000
        
        # Fast mode optimization
        if fast_mode and search_term and len(search_term) < 2:
            return {
                "files": [],
                "total": 0,
                "message": "حداقل 2 کاراکتر برای جستجو لازم است",
                "fast_mode": True
            }
        
        conn = sqlite3.connect(db_manager.db_file)
        cursor = conn.cursor()
        
        query = """
            SELECT path, name, size, modified, is_directory, extension, 
                   type, icon, permissions, drive_type
            FROM file_cache WHERE 1=1
        """
        params = []
        
        if search_term:
            if fast_mode:
                # Faster search - name only
                query += " AND name LIKE ?"
                params.append(f"%{search_term}%")
            else:
                # Full search - name and path
                query += " AND (name LIKE ? OR path LIKE ?)"
                params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if drive_filter and drive_filter != "all":
            query += " AND drive_type = ?"
            params.append(drive_filter)
            
        # Type filtering
        if type_filter and type_filter != "all":
            if type_filter == "image":
                query += " AND extension IN ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg')"
            elif type_filter == "video":
                query += " AND extension IN ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm')"
            elif type_filter == "audio":
                query += " AND extension IN ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')"
            elif type_filter == "document":
                query += " AND extension IN ('.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx')"
            elif type_filter == "archive":
                query += " AND extension IN ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2')"
            elif type_filter == "folder":
                query += " AND is_directory = 1"
        
        # Optimize sorting for fast mode
        if fast_mode:
            query += " ORDER BY name"
        else:
            query += " ORDER BY is_directory DESC, name"
            
        query += " LIMIT ?"
        params.append(limit)
        
        start_time = time.time()
        cursor.execute(query, params)
        results = cursor.fetchall()
        search_time = time.time() - start_time
        
        files = []
        for row in results:
            files.append({
                "path": row[0],
                "name": row[1],
                "size": row[2] or 0,
                "modified": row[3],
                "is_directory": bool(row[4]),
                "extension": row[5] or "",
                "type": row[6] or ("folder" if bool(row[4]) else "file"),
                "icon": row[7] or ("📁" if bool(row[4]) else "📄"),
                "permissions": row[8] or "",
                "drive_type": row[9] or ""
            })
        
        conn.close()
        
        return {
            "files": files,
            "total": len(files),
            "search_time": round(search_time * 1000, 2),  # ms
            "cached": True,
            "fast_mode": fast_mode,
            "filters": {
                "search": search_term,
                "drive": drive_filter,
                "type": type_filter
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/copy")
async def start_copy(request: CopyRequest):
    """Start optimized copy operation"""
    try:
        features = license_manager.get_features()
        
        # Check limits for free version
        if not license_manager.is_pro:
            if len(request.source_files) > features['max_files']:
                raise HTTPException(
                    status_code=403, 
                    detail=f"نسخه رایگان محدود به {features['max_files']} فایل است"
                )
            
            if len(file_ops.active_tasks) >= features['max_tasks']:
                raise HTTPException(
                    status_code=403,
                    detail=f"نسخه رایگان محدود به {features['max_tasks']} تسک همزمان است"
                )
        
        task_id = file_ops.start_copy_task(
            request.source_files,
            request.destination,
            request.options
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Copy operation started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting copy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
async def get_tasks():
    """Get all active tasks"""
    serializable_tasks = {}
    for task_id, task in file_ops.active_tasks.items():
        task_data = {k: v for k, v in task.items() if k != "future"}
        # Add control flags
        task_data["can_cancel"] = task.get("status") in ["running", "preparing", "paused"]
        task_data["can_pause"] = task.get("status") == "running"
        task_data["can_resume"] = task.get("status") == "paused"
        serializable_tasks[task_id] = task_data
    
    return {
        "tasks": serializable_tasks,
        "total": len(serializable_tasks)
    }

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task"""
    try:
        if task_id in file_ops.active_tasks:
            task = file_ops.active_tasks[task_id]
            task["status"] = "cancelled"
            task["cancelled"] = True
            
            # Try to cancel the future if it exists
            if "future" in task and not task["future"].done():
                task["future"].cancel()
            
            # Broadcast update
            await manager.broadcast({
                "type": "task_update",
                "data": {
                    "task_id": task_id,
                    "status": "cancelled",
                    "message": "تسک لغو شد"
                }
            })
            
            return {"success": True, "message": "تسک لغو شد"}
        else:
            raise HTTPException(status_code=404, detail="تسک یافت نشد")
            
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="خطا در لغو تسک")

@app.post("/api/tasks/{task_id}/pause")
async def pause_task(task_id: str):
    """Pause a running task"""
    try:
        if task_id in file_ops.active_tasks:
            task = file_ops.active_tasks[task_id]
            if task.get("status") == "running":
                task["status"] = "paused"
                task["paused"] = True
                
                # Broadcast update
                await manager.broadcast({
                    "type": "task_update", 
                    "data": {
                        "task_id": task_id,
                        "status": "paused",
                        "message": "تسک متوقف شد"
                    }
                })
                
                return {"success": True, "message": "تسک متوقف شد"}
            else:
                raise HTTPException(status_code=400, detail="تسک قابل توقف نیست")
        else:
            raise HTTPException(status_code=404, detail="تسک یافت نشد")
            
    except Exception as e:
        logger.error(f"Error pausing task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="خطا در توقف تسک")

@app.post("/api/tasks/{task_id}/resume")
async def resume_task(task_id: str):
    """Resume a paused task"""
    try:
        if task_id in file_ops.active_tasks:
            task = file_ops.active_tasks[task_id]
            if task.get("status") == "paused":
                task["status"] = "running"
                task["paused"] = False
                
                # Broadcast update
                await manager.broadcast({
                    "type": "task_update",
                    "data": {
                        "task_id": task_id,
                        "status": "running", 
                        "message": "تسک ادامه یافت"
                    }
                })
                
                return {"success": True, "message": "تسک ادامه یافت"}
            else:
                raise HTTPException(status_code=400, detail="تسک در حالت توقف نیست")
        else:
            raise HTTPException(status_code=404, detail="تسک یافت نشد")
            
    except Exception as e:
        logger.error(f"Error resuming task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="خطا در ادامه تسک")

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a completed task"""
    try:
        if task_id in file_ops.active_tasks:
            # Only allow deletion of completed tasks
            task = file_ops.active_tasks[task_id]
            if task.get("status") in ["completed", "failed", "cancelled"]:
                del file_ops.active_tasks[task_id]
                
                # Also remove from database
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM task_history WHERE task_id = ?', (task_id,))
                    conn.commit()
                
                await manager.broadcast({
                    "type": "task_deleted",
                    "data": {"task_id": task_id}
                })
                
                return {"success": True, "message": "تسک حذف شد"}
            else:
                raise HTTPException(status_code=400, detail="فقط تسک های تکمیل شده قابل حذف هستند")
        else:
            raise HTTPException(status_code=404, detail="تسک یافت نشد")
            
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="خطا در حذف تسک")

@app.delete("/api/tasks/completed")
async def clear_completed_tasks():
    """Clear all completed tasks"""
    try:
        completed_tasks = []
        for task_id, task in list(file_ops.active_tasks.items()):
            if task.get("status") in ["completed", "failed", "cancelled"]:
                completed_tasks.append(task_id)
                del file_ops.active_tasks[task_id]
        
        # Remove from database
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM task_history WHERE status IN (?, ?, ?)', 
                         ("completed", "failed", "cancelled"))
            conn.commit()
        
        await manager.broadcast({
            "type": "tasks_cleared",
            "data": {"deleted_count": len(completed_tasks)}
        })
        
        return {
            "success": True, 
            "message": f"{len(completed_tasks)} تسک حذف شد",
            "deleted_count": len(completed_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error clearing completed tasks: {e}")
        raise HTTPException(status_code=500, detail="خطا در حذف تسک‌ها")

@app.get("/api/config")
async def get_config():
    """Get application configuration"""
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "company": COMPANY_NAME,
        "themes": THEMES,
        "features": license_manager.get_features(),
        "is_pro": license_manager.is_pro,
        "license_info": license_manager.get_license_info()
    }

@app.get("/api/license")
async def get_license_info():
    """Get license information"""
    return license_manager.get_license_info()

@app.post("/api/license/activate")
async def activate_license(request: dict):
    """Activate a license key"""
    try:
        license_key = request.get("license_key", "").strip()
        if not license_key:
            raise HTTPException(status_code=400, detail="کلید لایسنس ارسال نشده")
        
        result = license_manager.activate_license(license_key)
        
        if result['success']:
            return {
                "success": True,
                "message": result['message'],
                "license_info": license_manager.get_license_info()
            }
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License activation error: {e}")
        raise HTTPException(status_code=500, detail="خطا در فعال‌سازی لایسنس")

@app.post("/api/license/generate")
async def generate_license(request: dict):
    """Generate a new license key (admin only)"""
    try:
        admin_key = request.get("admin_key", "")
        license_type = request.get("type", "pro")
        
        # Simple admin verification
        if admin_key != "ADMIN-2024-PERSIAN-FILE":
            raise HTTPException(status_code=403, detail="دسترسی غیرمجاز")
        
        new_key = license_manager.generate_license_key(license_type)
        
        return {
            "success": True,
            "license_key": new_key,
            "type": license_type,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License generation error: {e}")
        raise HTTPException(status_code=500, detail="خطا در تولید لایسنس")

@app.get("/api/settings")
async def get_settings():
    """Get application settings"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value, description FROM settings')
            settings = {}
            for row in cursor.fetchall():
                key, value, description = row
                try:
                    # Try to parse as JSON for complex values
                    settings[key] = json.loads(value)
                except:
                    settings[key] = value
            
            # Add default settings if not present
            default_settings = {
                "scan_max_depth": 10,
                "scan_max_files": 50000,
                "scan_include_hidden": False,
                "scan_include_system": False,
                "scan_subdirectories": True,
                "copy_verify": True,
                "copy_preserve_timestamps": True,
                "copy_create_destination": True,
                "copy_buffer_size": 1024 * 1024,  # 1MB
                "auto_index_drives": True,
                "index_interval": 300,  # 5 minutes
                "max_concurrent_tasks": 3,
                "task_timeout": 3600,  # 1 hour
                "log_level": "INFO",
                "theme": "light",
                "language": "fa"
            }
            
            # Merge with database settings
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value
            
            return {"settings": settings}
            
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت تنظیمات")

@app.post("/api/settings")
async def update_settings(request: dict):
    """Update application settings"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            for key, value in request.items():
                # Validate settings
                if key == "scan_max_depth" and not (1 <= value <= 50):
                    raise HTTPException(status_code=400, detail="عمق اسکن باید بین 1 تا 50 باشد")
                elif key == "scan_max_files" and not (1000 <= value <= 100000):
                    raise HTTPException(status_code=400, detail="حداکثر فایل‌ها باید بین 1000 تا 100000 باشد")
                elif key == "max_concurrent_tasks" and not (1 <= value <= 10):
                    raise HTTPException(status_code=400, detail="حداکثر تسک‌های همزمان باید بین 1 تا 10 باشد")
                
                # Store as JSON for complex values
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, description, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (key, str(value), f"Setting: {key}", time.time()))
            
            conn.commit()
            
            await manager.broadcast({
                "type": "settings_updated",
                "data": {"updated_settings": list(request.keys())}
            })
            
            return {"success": True, "message": "تنظیمات به‌روزرسانی شد"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail="خطا در به‌روزرسانی تنظیمات")

@app.post("/api/scan/directory")
async def scan_directory(request: dict):
    """Scan a specific directory with enhanced options"""
    try:
        directory = request.get("directory")
        settings = request.get("settings", {})
        
        if not directory or not os.path.exists(directory):
            raise HTTPException(status_code=400, detail="مسیر نامعتبر است")
        
        if not os.access(directory, os.R_OK):
            raise HTTPException(status_code=403, detail="دسترسی خواندن به مسیر وجود ندارد")
        
        # Create scan settings
        scan_settings = ScanSettings(
            max_depth=settings.get("max_depth", 10),
            max_files=settings.get("max_files", 50000),
            include_hidden=settings.get("include_hidden", False),
            include_system=settings.get("include_system", False),
            scan_subdirectories=settings.get("scan_subdirectories", True),
            file_types=settings.get("file_types")
        )
        
        # Start scanning in background
        task_id = str(uuid.uuid4())
        
        # Create drive info for the directory
        drive_info = DriveInfo(
            path=os.path.dirname(directory),
            name=os.path.basename(directory),
            label=os.path.basename(directory),
            total_space=0,
            free_space=0,
            used_space=0,
            filesystem="",
            drive_type="local",
            device_type="local"
        )
        
        # Add to active tasks
        file_ops.active_tasks[task_id] = {
            "task_id": task_id,
            "type": "scan",
            "status": "running",
            "progress": 0,
            "current_file": "",
            "speed": 0,
            "eta": 0,
            "total_files": 0,
            "scanned_files": 0,
            "total_size": 0,
            "scanned_size": 0,
            "errors": [],
            "source_device": directory,
            "dest_device": "",
            "scan_settings": scan_settings.dict(),
            "start_time": time.time(),
            "future": None
        }
        
        # Start scanning in background
        future = file_ops.executor.submit(
            file_ops._scan_directory_enhanced, 
            task_id, 
            directory, 
            drive_info, 
            scan_settings
        )
        file_ops.active_tasks[task_id]["future"] = future
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "اسکن شروع شد"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting directory scan: {e}")
        raise HTTPException(status_code=500, detail="خطا در شروع اسکن")

@app.post("/api/index/drive")
async def index_drive(request: dict):
    """Index a specific drive with enhanced options"""
    try:
        drive_path = request.get("drive_path")
        settings = request.get("settings", {})
        
        if not drive_path or not os.path.exists(drive_path):
            raise HTTPException(status_code=400, detail="مسیر درایو نامعتبر است")
        
        # Get drive info
        try:
            stat_info = os.statvfs(drive_path)
            drive_info = DriveInfo(
                path=drive_path,
                name=os.path.basename(drive_path),
                label=os.path.basename(drive_path),
                total_space=stat_info.f_blocks * stat_info.f_frsize,
                free_space=stat_info.f_bavail * stat_info.f_frsize,
                used_space=(stat_info.f_blocks - stat_info.f_bavail) * stat_info.f_frsize,
                filesystem="",
                drive_type=device_detector.detect_device_type(drive_path),
                device_type="local"
            )
        except Exception as e:
            logger.error(f"Error getting drive info: {e}")
            raise HTTPException(status_code=500, detail="خطا در دریافت اطلاعات درایو")
        
        # Start indexing in background
        task_id = str(uuid.uuid4())
        
        file_ops.active_tasks[task_id] = {
            "task_id": task_id,
            "type": "index",
            "status": "running",
            "progress": 0,
            "current_file": "",
            "speed": 0,
            "eta": 0,
            "total_files": 0,
            "indexed_files": 0,
            "total_size": 0,
            "indexed_size": 0,
            "errors": [],
            "source_device": drive_path,
            "dest_device": "",
            "start_time": time.time(),
            "future": None
        }
        
        # Start indexing in background
        max_files = settings.get("max_files", 50000)
        future = file_ops.executor.submit(
            db_manager.fast_index_directory,
            drive_path,
            drive_info,
            max_files
        )
        file_ops.active_tasks[task_id]["future"] = future
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "ایندکس شروع شد"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting drive indexing: {e}")
        raise HTTPException(status_code=500, detail="خطا در شروع ایندکس")

@app.get("/api/stats")
async def get_stats():
    """Get application statistics"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get file count
            cursor.execute('SELECT COUNT(*) FROM file_cache')
            total_files = cursor.fetchone()[0]
            
            # Get directory count
            cursor.execute('SELECT COUNT(*) FROM file_cache WHERE is_directory = 1')
            total_directories = cursor.fetchone()[0]
            
            # Get total size
            cursor.execute('SELECT SUM(size) FROM file_cache WHERE is_directory = 0')
            total_size = cursor.fetchone()[0] or 0
            
            # Get drive count
            cursor.execute('SELECT COUNT(*) FROM drive_info')
            total_drives = cursor.fetchone()[0]
            
            # Get task statistics
            cursor.execute('SELECT COUNT(*) FROM task_history')
            total_tasks = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM task_history WHERE status = "completed"')
            completed_tasks = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM task_history WHERE status = "failed"')
            failed_tasks = cursor.fetchone()[0]
            
            # Get recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM task_history 
                WHERE created_at > ?
            ''', (time.time() - 86400,))  # Last 24 hours
            recent_tasks = cursor.fetchone()[0]
            
            return {
                "stats": {
                    "total_files": total_files,
                    "total_directories": total_directories,
                    "total_size": total_size,
                    "total_drives": total_drives,
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "failed_tasks": failed_tasks,
                    "recent_tasks": recent_tasks,
                    "active_tasks": len(file_ops.active_tasks),
                    "uptime": time.time() - app.start_time if hasattr(app, 'start_time') else 0
                }
            }
            
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="خطا در دریافت آمار")

@app.post("/api/maintenance/cleanup")
async def cleanup_database():
    """Clean up old data and optimize database"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Remove old task history (older than 30 days)
            thirty_days_ago = time.time() - (30 * 24 * 3600)
            cursor.execute('DELETE FROM task_history WHERE created_at < ?', (thirty_days_ago,))
            deleted_tasks = cursor.rowcount
            
            # Remove orphaned file entries
            cursor.execute('''
                DELETE FROM file_cache 
                WHERE path NOT IN (
                    SELECT DISTINCT parent_path FROM file_cache WHERE parent_path IS NOT NULL
                ) AND is_directory = 1
            ''')
            deleted_dirs = cursor.rowcount
            
            # Optimize database
            cursor.execute('VACUUM')
            
            conn.commit()
            
            return {
                "success": True,
                "message": f"پاکسازی انجام شد: {deleted_tasks} تسک و {deleted_dirs} پوشه حذف شد",
                "deleted_tasks": deleted_tasks,
                "deleted_directories": deleted_dirs
            }
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail="خطا در پاکسازی")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# Background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks"""
    # Set event loop for file operations manager
    file_ops.event_loop = asyncio.get_running_loop()
    
    # Start drive monitoring
    asyncio.create_task(monitor_drives())
    logger.info(f"{APP_NAME} {APP_VERSION} started successfully")

async def monitor_drives():
    """Monitor drives for changes"""
    while True:
        try:
            await drive_scanner.scan_drives()
            await asyncio.sleep(REFRESH_INTERVALS['drives'] / 1000)
        except Exception as e:
            logger.error(f"Error in drive monitoring: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT, reload=False)