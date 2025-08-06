"""
Persian File Copier Pro - Configuration File
فایل تنظیمات و متغیرهای برنامه
"""

# Application Information
APP_NAME = "Persian File Copier Pro"
APP_VERSION = "3.5.0"
APP_EDITION = "Professional Edition"

# Company Information
COMPANY_NAME = "شرکت فناوری نوآوران مثبت سبز"
COMPANY_NAME_EN = "Positive Green Innovation Technology Company"

# Contact Information
TELEGRAM_ID = "Scrubby3137"
SUPPORT_EMAIL = "support@persianfile.ir"
WEBSITE = "www.persianfile.ir"

# Technical Configuration
DEFAULT_PORT = 8547  # Non-reserved port
WEBSOCKET_PORT = 8548
MAX_FILE_SIZE_FREE = 100 * 1024 * 1024  # 100MB for free version
MAX_CONCURRENT_TASKS_FREE = 2
MAX_FILES_PER_TASK_FREE = 50

# Copy Speed Optimization
BUFFER_SIZES = {
    'usb_2': 64 * 1024,      # 64KB for USB 2.0
    'usb_3': 1024 * 1024,    # 1MB for USB 3.0
    'ssd': 4 * 1024 * 1024,  # 4MB for SSD
    'hdd': 512 * 1024,       # 512KB for HDD
    'mtp': 32 * 1024,        # 32KB for MTP devices
    'network': 256 * 1024     # 256KB for network drives
}

# Theme Colors
THEMES = {
    'light': {
        'name': 'روشن',
        'primary': '#667eea',
        'secondary': '#764ba2',
        'background': '#ffffff',
        'surface': '#f8f9fa'
    },
    'dark': {
        'name': 'تاریک',
        'primary': '#667eea',
        'secondary': '#764ba2',
        'background': '#1a1a2e',
        'surface': '#16213e'
    },
    'semi_dark': {
        'name': 'نیمه تاریک',
        'primary': '#667eea',
        'secondary': '#764ba2',
        'background': '#2d3748',
        'surface': '#4a5568'
    },
    'alborz': {
        'name': 'کوه البرز',
        'primary': '#2d7d32',
        'secondary': '#388e3c',
        'background': 'linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%)',
        'surface': '#f1f8e9'
    },
    'caspian': {
        'name': 'دریای خزر',
        'primary': '#0277bd',
        'secondary': '#0288d1',
        'background': 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
        'surface': '#e1f5fe'
    },
    'desert': {
        'name': 'کویر ایران',
        'primary': '#f57c00',
        'secondary': '#ff9800',
        'background': 'linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%)',
        'surface': '#fffde7'
    },
    'persian_gulf': {
        'name': 'خلیج فارس',
        'primary': '#00acc1',
        'secondary': '#00bcd4',
        'background': 'linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%)',
        'surface': '#e0f7fa'
    }
}

# Features Configuration
FEATURES = {
    'free_version': {
        'max_files': 100,
        'max_tasks': 2,
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'speed_optimization': False,
        'advanced_themes': False,
        'priority_support': False
    },
    'pro_version': {
        'max_files': -1,  # Unlimited
        'max_tasks': 10,
        'max_file_size': -1,  # Unlimited
        'speed_optimization': True,
        'advanced_themes': True,
        'priority_support': True
    }
}

# Device Types for Speed Optimization
DEVICE_TYPES = {
    'USB_2': 'usb_2',
    'USB_3': 'usb_3',
    'SSD': 'ssd',
    'HDD': 'hdd',
    'MTP': 'mtp',
    'NETWORK': 'network'
}

# MTP Device Patterns
MTP_PATTERNS = [
    'WPD\\',
    'MTP\\',
    'WPDUSB',
    'Android',
    'iPhone',
    'iPad'
]

# Auto-refresh intervals (milliseconds)
REFRESH_INTERVALS = {
    'drives': 5000,      # 5 seconds
    'files': 30000,      # 30 seconds
    'tasks': 1000,       # 1 second
    'device_detect': 3000 # 3 seconds
}

# File operation settings
FILE_OPERATIONS = {
    'chunk_size': 1024 * 1024,  # 1MB default
    'verify_hash': True,
    'preserve_timestamps': True,
    'skip_existing': False,
    'create_log': True,
    'max_retries': 3
}

# UI Settings
UI_SETTINGS = {
    'animation_duration': 300,  # milliseconds
    'notification_duration': 4000,  # 4 seconds
    'auto_hide_completed_tasks': True,
    'show_progress_percentage': True,
    'show_speed_indicator': True,
    'compact_file_list': False
}

# Security and License
LICENSE_CONFIG = {
    'trial_days': 30,
    'check_interval': 24 * 60 * 60,  # 24 hours in seconds
    'server_url': 'https://license.persianfile.ir/api/v1/',
    'public_key': 'persian_file_copier_pro_2024'
}

# Logging Configuration
LOG_CONFIG = {
    'level': 'INFO',
    'file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# About Information
ABOUT_INFO = {
    'description': """
    Persian File Copier Pro یک نرم‌افزار پیشرفته و حرفه‌ای برای مدیریت و کپی فایل‌ها است که با استفاده از جدیدترین تکنولوژی‌های وب و هوش مصنوعی طراحی شده است.
    
    این نرم‌افزار قابلیت‌های منحصر به فردی مانند تشخیص خودکار دستگاه‌ها، بهینه‌سازی سرعت کپی، و رابط کاربری زیبا و کاربرپسند را ارائه می‌دهد.
    """,
    'features': [
        "🚀 سرعت کپی بهینه شده برای انواع دستگاه‌ها",
        "🔍 تشخیص خودکار دستگاه‌های MTP، USB و شبکه",
        "🎨 تم‌های متنوع با الهام از طبیعت ایران",
        "⚡ عملکرد real-time با WebSocket",
        "🛡️ امنیت پیشرفته و سیستم لایسنس",
        "📱 رابط کاربری responsive و مدرن",
        "🔧 تنظیمات پیشرفته و قابل شخصی‌سازی",
        "📊 مدیریت تسک‌های همزمان"
    ],
    'technologies': [
        "Python 3.11+ with FastAPI",
        "Modern Web Technologies (HTML5, CSS3, JavaScript ES6+)",
        "WebSocket for Real-time Communication",
        "SQLite Database with Advanced Indexing",
        "Async/Await Operations",
        "Device Detection APIs",
        "Advanced File System Operations"
    ]
}