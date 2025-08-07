# Persian File Copier Pro - C# Edition
## فارسی کاپیر فایل حرفه‌ای - نسخه C#

[![.NET](https://img.shields.io/badge/.NET-8.0-blue.svg)](https://dotnet.microsoft.com/)
[![ASP.NET Core](https://img.shields.io/badge/ASP.NET%20Core-8.0-purple.svg)](https://docs.microsoft.com/en-us/aspnet/core/)
[![SignalR](https://img.shields.io/badge/SignalR-Latest-green.svg)](https://docs.microsoft.com/en-us/aspnet/core/signalr/)
[![License](https://img.shields.io/badge/License-Pro-gold.svg)](#)

یک نرم‌افزار پیشرفته و حرفه‌ای برای کپی کردن فایل‌ها با قابلیت‌های فوق‌العاده که به زبان C# و با استفاده از ASP.NET Core نوشته شده است.

## ✨ ویژگی‌های جدید نسخه C#

### 🚀 عملکرد بهتر
- **معماری جدید**: مبتنی بر ASP.NET Core 8.0
- **پردازش موازی**: استفاده از Task-based Asynchronous Pattern
- **مدیریت حافظه بهینه**: Garbage Collection بهینه شده
- **پردازش چندهسته‌ای**: استفاده کامل از قدرت پردازنده

### 🔄 ارتباط Real-time
- **SignalR**: جایگزین WebSocket برای ارتباط دوطرفه
- **اتصال مجدد خودکار**: قطع و وصل بدون از دست دادن داده
- **پیام‌رسانی پایدار**: تضمین رسیدن پیام‌ها
- **به‌روزرسانی لحظه‌ای**: نمایش progress بدون تأخیر

### 🛡️ امنیت و پایداری
- **مدیریت خطا پیشرفته**: Exception handling جامع
- **Logging پیشرفته**: ثبت تمام فعالیت‌ها
- **Validation**: اعتبارسنجی دقیق ورودی‌ها
- **Thread Safety**: ایمن در محیط چندنخی

## 📋 پیش‌نیازها

### Windows
- **Windows 10/11** (64-bit)
- **.NET 8.0 Runtime** یا جدیدتر
- **حداقل 4GB RAM**
- **500MB فضای خالی**

### Linux/macOS
- **Ubuntu 20.04+** / **macOS 10.15+**
- **.NET 8.0 Runtime** یا جدیدتر
- **حداقل 2GB RAM**
- **500MB فضای خالی**

## 🚀 نصب و راه‌اندازی

### نصب .NET Runtime
```bash
# Windows (PowerShell)
winget install Microsoft.DotNet.Runtime.8

# Ubuntu/Debian
wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update && sudo apt-get install -y dotnet-runtime-8.0

# macOS (Homebrew)
brew install --cask dotnet
```

### راه‌اندازی نرم‌افزار

#### Windows
```cmd
# Download and extract the application
# Then run:
run.bat
```

#### Linux/macOS
```bash
# Download and extract the application
# Then run:
chmod +x run.sh
./run.sh
```

#### Development Mode
```bash
# Clone the repository
git clone <repository-url>
cd PersianFileCopierPro

# Restore packages
dotnet restore

# Run the application
dotnet run
```

## 🌐 دسترسی به نرم‌افزار

پس از اجرا، نرم‌افزار در آدرس زیر در دسترس خواهد بود:
```
http://localhost:8548
```

## 🏗️ معماری نرم‌افزار

### Backend (C# ASP.NET Core)
```
┌─ Controllers/          # API Controllers
│  ├─ TaskController     # مدیریت تسک‌ها
│  ├─ DriveController    # مدیریت درایوها  
│  ├─ FileController     # عملیات فایل
│  └─ ConfigController   # تنظیمات و لایسنس
│
├─ Services/             # Business Logic
│  ├─ TaskManagerService # مدیریت تسک‌های کپی
│  ├─ FileOperationService # عملیات فایل
│  ├─ DriveService       # مدیریت درایوها
│  ├─ ConfigurationService # تنظیمات
│  └─ LicenseService     # مدیریت لایسنس
│
├─ Models/               # Data Models
│  ├─ TaskModel         # مدل تسک
│  ├─ DriveModel        # مدل درایو
│  ├─ FileModel         # مدل فایل
│  └─ ConfigurationModel # مدل تنظیمات
│
├─ Hubs/                # SignalR Hubs
│  └─ TaskHub           # Hub برای Real-time updates
│
└─ wwwroot/             # Static Files
   ├─ index.html        # UI اصلی
   ├─ manifest.json     # PWA Manifest
   └─ sw.js            # Service Worker
```

### Frontend (HTML/CSS/JavaScript)
- **Progressive Web App (PWA)**
- **Responsive Design**
- **Real-time Updates با SignalR**
- **Drag & Drop بهینه شده**
- **Task Management پیشرفته**

## 🔧 API Endpoints

### تسک‌ها (Tasks)
```http
GET    /api/task                    # دریافت همه تسک‌ها
GET    /api/task/{id}               # دریافت تسک خاص
POST   /api/task/copy               # ایجاد تسک کپی
POST   /api/task/{id}/pause         # توقف تسک
POST   /api/task/{id}/resume        # ادامه تسک
POST   /api/task/{id}/cancel        # لغو تسک
DELETE /api/task/{id}               # حذف تسک
POST   /api/task/{id}/retry         # تلاش مجدد
POST   /api/task/pause-all          # توقف همه
POST   /api/task/resume-all         # ادامه همه
POST   /api/task/cancel-all         # لغو همه
POST   /api/task/clear-completed    # پاکسازی تکمیل شده
GET    /api/task/export             # خروجی گزارش
```

### درایوها (Drives)
```http
GET    /api/drive                   # دریافت همه درایوها
GET    /api/drive/{path}            # دریافت درایو خاص
POST   /api/drive/refresh           # به‌روزرسانی درایوها
GET    /api/drive/{path}/ready      # بررسی آماده بودن
```

### فایل‌ها (Files)
```http
GET    /api/file?path={path}        # دریافت فایل‌ها
POST   /api/file/create-directory  # ایجاد پوشه
DELETE /api/file/file?path={path}  # حذف فایل
DELETE /api/file/directory?path={path} # حذف پوشه
GET    /api/file/size?path={path}  # اندازه پوشه
GET    /api/file/count?path={path} # تعداد فایل‌ها
GET    /api/file/exists?path={path} # بررسی وجود
```

### تنظیمات (Configuration)
```http
GET    /api/config                  # دریافت تنظیمات
POST   /api/config                  # به‌روزرسانی تنظیمات
GET    /api/config/license          # اطلاعات لایسنس
POST   /api/config/license/activate # فعال‌سازی لایسنس
GET    /api/config/license/machine-id # Machine ID
POST   /api/config/license/generate # تولید لایسنس
GET    /api/config/license/validate # اعتبارسنجی لایسنس
GET    /api/config/version          # اطلاعات نسخه
```

## 📊 مقایسه با نسخه Python

| ویژگی | Python | C# |
|--------|--------|-----|
| **سرعت اجرا** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **مصرف حافظه** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **پایداری** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Real-time Updates** | WebSocket | SignalR ⭐⭐⭐⭐⭐ |
| **Cross Platform** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **مدیریت خطا** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Threading** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Type Safety** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🔥 بهبودهای عملکرد

### مدیریت Task ها
- **Thread Pool**: استفاده بهینه از Thread Pool
- **Async/Await**: عملیات غیرهمزمان کامل
- **CancellationToken**: لغو ایمن تسک‌ها
- **Progress Reporting**: گزارش‌دهی دقیق پیشرفت

### بهینه‌سازی I/O
- **Buffer Size**: بافر 1MB برای کپی
- **FileStream Options**: بهینه‌سازی خواندن/نوشتن
- **Sequential Access**: دسترسی ترتیبی به فایل‌ها
- **Memory Management**: مدیریت حافظه بهینه

## 🚨 رفع مشکلات

### خطاهای رایج

#### ❌ "Port 8548 is already in use"
```bash
# بررسی process های در حال اجرا
netstat -tulpn | grep 8548

# یا تغییر پورت
export PORT=8549
dotnet run
```

#### ❌ ".NET Runtime not found"
```bash
# نصب .NET Runtime
# Windows
winget install Microsoft.DotNet.Runtime.8

# Linux
sudo apt install dotnet-runtime-8.0
```

#### ❌ "Access denied to drive"
- نرم‌افزار را به عنوان Administrator اجرا کنید
- دسترسی‌های فایل سیستم را بررسی کنید

### Performance Tuning

#### تنظیمات بهینه
```json
{
  "maxConcurrentTasks": 3,
  "bufferSize": 1048576,
  "verifyAfterCopy": true,
  "enableRealTimeUpdates": true,
  "updateIntervalMs": 500
}
```

## 🤝 مشارکت در توسعه

### ساختار Development
```bash
# Clone repository
git clone <repo-url>
cd PersianFileCopierPro

# Install dependencies
dotnet restore

# Run in development mode
dotnet run --environment Development

# Run tests
dotnet test

# Build for production
dotnet publish -c Release
```

### Coding Standards
- **C# Naming Conventions**
- **Async/Await Pattern**
- **Dependency Injection**
- **SOLID Principles**
- **Clean Architecture**

## 📞 پشتیبانی

### اطلاعات تماس
- **وبسایت**: [در حال توسعه]
- **ایمیل**: support@persiancoppier.com
- **GitHub Issues**: برای گزارش باگ
- **Telegram**: [@PersianFileCopier]

### سطوح پشتیبانی
- **رایگان**: باگ‌های عمومی
- **Pro**: پشتیبانی ۲۴/۷
- **Enterprise**: پشتیبانی اختصاصی

## 📄 لایسنس

این نرم‌افزار تحت لایسنس تجاری Persian File Copier Pro منتشر شده است.

### نوع لایسنس‌ها
- **Trial**: ۳۰ روز آزمایشی
- **Personal**: استفاده شخصی
- **Professional**: استفاده تجاری
- **Enterprise**: استفاده سازمانی

---

**Persian File Copier Pro 3.5.0 - C# Edition**  
*فارسی کاپیر فایل حرفه‌ای - نسخه C#*

© 2024 Persian File Copier Team. All rights reserved.