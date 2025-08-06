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

# Enhanced Device Detection Class
class DeviceDetector:
    def __init__(self):
        self.mtp_devices = {}
        self.last_scan = 0
        
    def detect_device_type(self, drive_path: str) -> str:
        """Detect device type for speed optimization"""
        try:
            if platform.system() == "Windows" and WINDOWS_AVAILABLE:
                drive_type = win32file.GetDriveType(drive_path)
                
                if drive_type == win32con.DRIVE_REMOVABLE:
                    # Check if it's USB 3.0 or 2.0
                    if self._is_usb3(drive_path):
                        return DEVICE_TYPES['USB_3']
                    return DEVICE_TYPES['USB_2']
                elif drive_type == win32con.DRIVE_FIXED:
                    # Check if SSD or HDD
                    if self._is_ssd(drive_path):
                        return DEVICE_TYPES['SSD']
                    return DEVICE_TYPES['HDD']
                elif drive_type == win32con.DRIVE_REMOTE:
                    return DEVICE_TYPES['NETWORK']
                    
            return DEVICE_TYPES['HDD']  # Default
        except Exception as e:
            logger.debug(f"Device type detection failed: {e}")
            return DEVICE_TYPES['HDD']
    
    def _is_usb3(self, drive_path: str) -> bool:
        """Check if USB device is 3.0"""
        try:
            # Simple heuristic: check transfer speed
            # This is a simplified check
            return True  # Assume USB 3.0 for now
        except:
            return False
    
    def _is_ssd(self, drive_path: str) -> bool:
        """Check if drive is SSD"""
        try:
            # Windows WMI query for drive type
            import wmi
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                if disk.MediaType and 'SSD' in disk.MediaType:
                    return True
            return False
        except ImportError:
            logger.warning("WMI module not available for SSD detection")
            return False
        except Exception as e:
            logger.error(f"Error detecting SSD: {e}")
            return False
    
    def scan_mtp_devices(self) -> List[Dict]:
        """Scan for MTP devices"""
        devices = []
        try:
            if platform.system() == "Windows" and WINDOWS_AVAILABLE:
                # Use Windows API to detect MTP devices
                devices = self._scan_windows_mtp()
        except Exception as e:
            logger.debug(f"MTP scanning not available: {e}")
        
        return devices
    
    def _scan_windows_mtp(self) -> List[Dict]:
        """Scan MTP devices on Windows"""
        devices = []
        try:
            # Use WMI to detect portable devices
            import wmi
            c = wmi.WMI()
            for device in c.Win32_PnPEntity():
                if device.DeviceID and any(pattern in device.DeviceID for pattern in MTP_PATTERNS):
                    devices.append({
                        'name': device.Name or 'Unknown Device',
                        'device_id': device.DeviceID,
                        'type': 'MTP',
                        'status': device.Status or 'Unknown'
                    })
        except ImportError:
            logger.warning("WMI module not available for MTP detection")
            return []
        except Exception as e:
            logger.debug(f"MTP scan failed (normal if no MTP devices): {e}")
        
        return devices

device_detector = DeviceDetector()

# Enhanced Database Manager
class DatabaseManager:
    def __init__(self, db_file: str = "persian_file_cache.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize enhanced database tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Enhanced files table
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
                mime_type TEXT,
                icon TEXT,
                drive_type TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed INTEGER
            )
        ''')
        
        # Drives table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drives (
                path TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                label TEXT,
                total_space INTEGER,
                free_space INTEGER,
                filesystem TEXT,
                drive_type TEXT,
                device_type TEXT,
                last_updated INTEGER DEFAULT (strftime('%s', 'now')),
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Settings table
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
                error_message TEXT,
                source_device TEXT,
                dest_device TEXT,
                average_speed REAL
            )
        ''')
        
        # License table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS license (
                id INTEGER PRIMARY KEY,
                license_key TEXT,
                status TEXT DEFAULT 'trial',
                activated_at INTEGER,
                expires_at INTEGER,
                machine_id TEXT,
                features TEXT
            )
        ''')
        
        # Create comprehensive indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_drive ON files(drive)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_name ON files(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_extension ON files(extension)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_size ON files(size)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_type ON files(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_drive_type ON files(drive_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_drives_type ON drives(drive_type)')
        
        conn.commit()
        conn.close()
    
    def get_file_icon(self, file_path: str, is_directory: bool = False) -> str:
        """Get appropriate icon for file type"""
        if is_directory:
            return "📁"
        
        ext = Path(file_path).suffix.lower()
        icon_map = {
            '.pdf': '📄', '.doc': '📄', '.docx': '📄', '.txt': '📄', '.rtf': '📄',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.bmp': '🖼️', '.svg': '🖼️', '.webp': '🖼️',
            '.mp4': '🎬', '.avi': '🎬', '.mkv': '🎬', '.mov': '🎬', '.wmv': '🎬', '.flv': '🎬', '.webm': '🎬',
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.m4a': '🎵', '.ogg': '🎵', '.aac': '🎵',
            '.zip': '🗂️', '.rar': '🗂️', '.7z': '🗂️', '.tar': '🗂️', '.gz': '🗂️', '.bz2': '🗂️',
            '.exe': '⚙️', '.msi': '⚙️', '.deb': '⚙️', '.rpm': '⚙️', '.dmg': '⚙️',
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨', '.json': '📋',
            '.iso': '💿', '.img': '💿', '.bin': '💿',
            '.xlsx': '📊', '.xls': '📊', '.csv': '📊',
            '.pptx': '📊', '.ppt': '📊'
        }
        return icon_map.get(ext, '📄')
    
    def update_drives(self, drives: List[DriveInfo]):
        """Update drives information in database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            for drive in drives:
                cursor.execute('''
                    INSERT OR REPLACE INTO drives 
                    (path, name, label, total_space, free_space, filesystem, 
                     drive_type, device_type, last_updated, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    drive.path, drive.name, drive.label, drive.total_space,
                    drive.free_space, drive.filesystem, drive.drive_type,
                    drive.device_type, int(time.time()), True
                ))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating drives: {e}")
        finally:
            conn.close()
    
    def fast_index_directory(self, directory: str, drive_info: DriveInfo, max_files: int = 10000) -> int:
        """Fast indexing with limits for better performance"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        indexed_count = 0
        
        try:
            start_time = time.time()
            
            for root, dirs, files in os.walk(directory):
                # Check time limit (max 15 seconds)
                if time.time() - start_time > 15:
                    break
                
                # Check file count limit
                if indexed_count >= max_files:
                    break
                
                for name in dirs + files:
                    try:
                        full_path = os.path.join(root, name)
                        stat_info = os.stat(full_path)
                        is_dir = os.path.isdir(full_path)
                        
                        size = stat_info.st_size if not is_dir else 0
                        modified = int(stat_info.st_mtime)
                        extension = Path(name).suffix.lower() if not is_dir else ""
                        mime_type = mimetypes.guess_type(full_path)[0] if not is_dir else "folder"
                        icon = self.get_file_icon(full_path, is_dir)
                        permissions = oct(stat_info.st_mode)[-3:]
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO files 
                            (path, name, size, modified, drive, extension, type, is_directory, 
                             indexed_at, permissions, mime_type, icon, drive_type)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            full_path, name, size, modified, drive_info.path, extension,
                            mime_type, is_dir, int(time.time()), permissions, 
                            mime_type, icon, drive_info.device_type
                        ))
                        
                        indexed_count += 1
                        
                        if indexed_count % 50 == 0:
                            conn.commit()
                            
                    except (OSError, PermissionError):
                        continue
            
            conn.commit()
            logger.info(f"Indexed {indexed_count} files from {directory} in {time.time() - start_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error indexing directory {directory}: {e}")
        finally:
            conn.close()
        
        return indexed_count

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

# Enhanced File Operations Manager
class FileOperationsManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.active_tasks: Dict[str, Dict] = {}
        
    def get_optimal_buffer_size(self, source_device: str, dest_device: str) -> int:
        """Get optimal buffer size based on device types"""
        source_buffer = BUFFER_SIZES.get(source_device, BUFFER_SIZES['hdd'])
        dest_buffer = BUFFER_SIZES.get(dest_device, BUFFER_SIZES['hdd'])
        return min(source_buffer, dest_buffer)  # Use smaller buffer size
    
    def start_copy_task(self, source_files: List[str], destination: str, options: Dict = None) -> str:
        """Start enhanced copy task with device optimization"""
        task_id = str(uuid.uuid4())
        
        if options is None:
            options = {}
        
        # Detect source and destination device types
        source_device = device_detector.detect_device_type(source_files[0][:3] if source_files else "C:\\")
        dest_device = device_detector.detect_device_type(destination[:3])
        
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
            "source_device": source_device,
            "dest_device": dest_device,
            "buffer_size": self.get_optimal_buffer_size(source_device, dest_device)
        }
        
        self.active_tasks[task_id] = task_info
        
        # Submit task to executor
        future = self.executor.submit(self._copy_files_optimized, task_id)
        task_info["future"] = future
        
        return task_id
    
    def _copy_files_optimized(self, task_id: str):
        """Optimized copy with device-specific settings and pause/cancel support"""
        task = self.active_tasks.get(task_id)
        if not task:
            return

        try:
            os.makedirs(task["destination"], exist_ok=True)
            start_time = time.time()
            
            for i, source_file in enumerate(task["source_files"]):
                # Check for pause/cancel requests
                while task.get("paused", False):
                    time.sleep(0.5)  # Wait while paused
                    if task.get("cancelled", False):
                        break
                
                # Check if task was cancelled
                if task.get("cancelled", False):
                    task["status"] = "cancelled"
                    logger.info(f"Task {task_id} was cancelled by user")
                    break
                
                if not os.path.exists(source_file):
                    task["errors"].append(f"File not found: {source_file}")
                    continue
                
                filename = os.path.basename(source_file)
                dest_path = os.path.join(task["destination"], filename)
                
                # Skip if destination exists
                if os.path.exists(dest_path):
                    logger.info(f"File already exists, skipping: {dest_path}")
                    task["copied_files"] = i + 1
                    continue
                
                task["current_file"] = filename
                task["copied_files"] = i
                task["progress"] = int((i / len(task["source_files"])) * 100)
                
                # Calculate speed and ETA
                elapsed = time.time() - start_time
                if elapsed > 0 and task["copied_size"] > 0:
                    speed = task["copied_size"] / elapsed
                    task["speed"] = speed
                    
                    remaining_size = task["total_size"] - task["copied_size"]
                    if speed > 0:
                        task["eta"] = int(remaining_size / speed)
                
                # Broadcast progress
                asyncio.create_task(self._broadcast_task_update(task_id))
                
                # Optimized copy
                try:
                    if os.path.isdir(source_file):
                        shutil.copytree(source_file, dest_path, dirs_exist_ok=True)
                    else:
                        self._optimized_file_copy(source_file, dest_path, task["buffer_size"])
                        if os.path.exists(source_file):
                            task["copied_size"] += os.path.getsize(source_file)
                        
                except Exception as e:
                    error_msg = f"Error copying {filename}: {str(e)}"
                    task["errors"].append(error_msg)
                    logger.error(error_msg)
                    continue
            
            # Set final status
            if task.get("cancelled", False):
                task["status"] = "cancelled"
            elif task["errors"]:
                task["status"] = "completed_with_errors"
            else:
                task["status"] = "completed"
                
            task["progress"] = 100
            task["end_time"] = time.time()
            
        except Exception as e:
            logger.error(f"Error in copy task {task_id}: {e}")
            task["status"] = "error"
            task["errors"].append(str(e))
        
        # Final broadcast
        asyncio.create_task(self._broadcast_task_update(task_id))
    
    def _optimized_file_copy(self, source: str, destination: str, buffer_size: int):
        """Optimized file copy with custom buffer size"""
        with open(source, 'rb') as src, open(destination, 'wb') as dst:
            while True:
                chunk = src.read(buffer_size)
                if not chunk:
                    break
                dst.write(chunk)
        
        # Preserve timestamps
        stat_info = os.stat(source)
        os.utime(destination, (stat_info.st_atime, stat_info.st_mtime))
    
    async def _broadcast_task_update(self, task_id: str):
        """Broadcast task update to all connected clients"""
        task = self.active_tasks.get(task_id)
        if task:
            broadcast_task = {k: v for k, v in task.items() if k not in ["future"]}
            await manager.broadcast({
                "type": "task_update",
                "data": broadcast_task
            })

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
        import uuid, platform
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
            conn = sqlite3.connect(db_manager.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM license ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            conn.close()
            
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
            conn = sqlite3.connect(db_manager.db_file)
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
            conn.close()
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
            conn = sqlite3.connect(db_manager.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO license (license_key, status, activated_at, machine_id)
                VALUES (?, ?, ?, ?)
            ''', ('TRIAL', 'trial', int(time.time()), self.machine_id))
            conn.commit()
            conn.close()
            
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
            conn = sqlite3.connect(db_manager.db_file)
            cursor = conn.cursor()
            cursor.execute('UPDATE license SET status = ? WHERE machine_id = ?', 
                         ('expired', self.machine_id))
            conn.commit()
            conn.close()
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

license_manager = LicenseManager()

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
                    path=f"MTP:\\{device['device_id']}",
                    name=device['name'],
                    label=device['name'],
                    total_space=0,
                    free_space=0,
                    used_space=0,
                    filesystem="MTP",
                    drive_type="mtp",
                    device_type=DEVICE_TYPES['MTP'],
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
            FROM files WHERE 1=1
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
            query += " AND drive = ?"
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
                raise HTTPException(status_code=400, detail="تسک قابل ادامه نیست")
        else:
            raise HTTPException(status_code=404, detail="تسک یافت نشد")
            
    except Exception as e:
        logger.error(f"Error resuming task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="خطا در ادامه تسک")

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