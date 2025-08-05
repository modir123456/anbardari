#!/usr/bin/env python3
"""
Persian File Copier Pro - Build Installer Script
اسکریپت تولید فایل نصبی برای Persian File Copier Pro
شرکت فناوری نوآئران مثبت سبز
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import json

class BuildConfig:
    """پیکربندی ساخت"""
    
    def __init__(self):
        self.app_name = "Persian File Copier Pro"
        self.app_version = "2.0.0"
        self.app_description = "ابزار حرفه‌ای کپی فایل با رابط کاربری پیشرفته"
        self.company_name = "شرکت فناوری نوآئران مثبت سبز"
        self.copyright = "© 2024 Noavaran Mosbat Sabz Technology"
        
        self.main_script = "run_web_pro.py"
        self.icon_file = "web/favicon.ico"
        self.build_dir = "build"
        self.dist_dir = "dist"
        self.installer_dir = "installer"
        
        # Files to include
        self.data_files = [
            ("web", "web"),
            ("requirements_web_pro.txt", "."),
            ("README.md", "."),
        ]
        
        # Hidden imports
        self.hidden_imports = [
            'eel',
            'psutil',
            'requests',
            'Pillow',
            'sqlite3',
            'hashlib',
            'uuid',
            'base64',
            'queue',
            'watchdog',
            'concurrent.futures',
            'threading',
            'json',
            'datetime',
            'pathlib'
        ]

class BuildManager:
    """مدیریت فرآیند ساخت"""
    
    def __init__(self):
        self.config = BuildConfig()
        self.script_dir = Path(__file__).parent
        self.is_windows = platform.system() == "Windows"
        
    def print_step(self, step, message):
        """نمایش مرحله ساخت"""
        print(f"\n{'='*60}")
        print(f"🔧 Step {step}: {message}")
        print(f"{'='*60}")
    
    def run_command(self, command, shell=True):
        """اجرای دستور"""
        print(f"💻 Running: {command}")
        try:
            result = subprocess.run(command, shell=shell, check=True, 
                                  capture_output=True, text=True)
            if result.stdout:
                print(f"✅ Output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stderr:
                print(f"❌ Error details: {e.stderr}")
            return False
    
    def clean_build_dirs(self):
        """پاک کردن پوشه‌های ساخت قبلی"""
        self.print_step(1, "Cleaning previous build directories")
        
        dirs_to_clean = [self.config.build_dir, self.config.dist_dir, self.config.installer_dir]
        
        for dir_name in dirs_to_clean:
            dir_path = self.script_dir / dir_name
            if dir_path.exists():
                print(f"🗑️  Removing {dir_path}")
                shutil.rmtree(dir_path)
            else:
                print(f"✅ {dir_path} doesn't exist")
        
        # Create installer directory
        installer_path = self.script_dir / self.config.installer_dir
        installer_path.mkdir(exist_ok=True)
        print(f"📁 Created {installer_path}")
    
    def check_dependencies(self):
        """بررسی وابستگی‌ها"""
        self.print_step(2, "Checking dependencies")
        
        required_packages = ['pyinstaller', 'eel', 'psutil', 'requests', 'Pillow']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} is installed")
            except ImportError:
                print(f"❌ {package} is missing")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
            install_cmd = f"{sys.executable} -m pip install {' '.join(missing_packages)}"
            if not self.run_command(install_cmd):
                print("❌ Failed to install dependencies")
                return False
        
        return True
    
    def create_spec_file(self):
        """ایجاد فایل spec برای PyInstaller"""
        self.print_step(3, "Creating PyInstaller spec file")
        
        # Create icon if not exists
        icon_path = self.script_dir / self.config.icon_file
        if not icon_path.exists():
            print(f"⚠️  Icon file not found at {icon_path}, creating default")
            self.create_default_icon()
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{self.config.main_script}'],
    pathex=['{self.script_dir}'],
    binaries=[],
    datas={self.config.data_files},
    hiddenimports={self.config.hidden_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.config.app_name.replace(" ", "_")}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path}' if icon_path.exists() else None,
    version_file=None,
)
'''
        
        spec_file = self.script_dir / f"{self.config.app_name.replace(' ', '_')}.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✅ Created spec file: {spec_file}")
        return spec_file
    
    def create_default_icon(self):
        """ایجاد آیکون پیش‌فرض"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple icon
            size = (256, 256)
            image = Image.new('RGBA', size, (102, 126, 234, 255))
            draw = ImageDraw.Draw(image)
            
            # Draw a simple file icon
            draw.rectangle([50, 50, 206, 206], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=3)
            draw.text((128, 128), "PFC", fill=(102, 126, 234, 255), anchor="mm")
            
            icon_path = self.script_dir / self.config.icon_file
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(icon_path, format='ICO')
            print(f"✅ Created default icon: {icon_path}")
            
        except ImportError:
            print("⚠️  Pillow not available, skipping icon creation")
    
    def build_executable(self):
        """ساخت فایل اجرایی"""
        self.print_step(4, "Building executable with PyInstaller")
        
        spec_file = self.create_spec_file()
        
        build_cmd = f"pyinstaller --clean --noconfirm {spec_file}"
        
        if not self.run_command(build_cmd):
            print("❌ Failed to build executable")
            return False
        
        print("✅ Executable built successfully")
        return True
    
    def create_installer_script(self):
        """ایجاد اسکریپت نصب"""
        self.print_step(5, "Creating installer script")
        
        if self.is_windows:
            return self.create_nsis_installer()
        else:
            return self.create_linux_installer()
    
    def create_nsis_installer(self):
        """ایجاد نصب‌کننده NSIS برای Windows"""
        print("🪟 Creating NSIS installer for Windows")
        
        nsis_script = f'''
; Persian File Copier Pro Installer Script
; Generated by build_installer.py

!define APP_NAME "{self.config.app_name}"
!define APP_VERSION "{self.config.app_version}"
!define APP_PUBLISHER "{self.config.company_name}"
!define APP_EXE "{self.config.app_name.replace(" ", "_")}.exe"
!define APP_DESCRIPTION "{self.config.app_description}"

; Modern UI
!include "MUI2.nsh"

; General settings
Name "${{APP_NAME}}"
OutFile "installer\\${{APP_NAME}}_v${{APP_VERSION}}_Setup.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "web\\favicon.ico"
!define MUI_UNICON "web\\favicon.ico"

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
!define MUI_LANGDLL_REGISTRY_KEY "Software\\${{APP_NAME}}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "README.md"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Persian"

; Version Information
VIProductVersion "${{APP_VERSION}}.0"
VIAddVersionKey "ProductName" "${{APP_NAME}}"
VIAddVersionKey "CompanyName" "${{APP_PUBLISHER}}"
VIAddVersionKey "FileDescription" "${{APP_DESCRIPTION}}"
VIAddVersionKey "FileVersion" "${{APP_VERSION}}"
VIAddVersionKey "ProductVersion" "${{APP_VERSION}}"
VIAddVersionKey "LegalCopyright" "{self.config.copyright}"

; Installer sections
Section "Core Application" SecCore
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    File /r "dist\\${{APP_EXE}}"
    File "README.md"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    
    ; Registry
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
SectionEnd

; Uninstaller
Section "Uninstall"
    Delete "$INSTDIR\\${{APP_EXE}}"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\Uninstall.exe"
    
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    DeleteRegKey HKCU "Software\\${{APP_NAME}}"
    
    RMDir "$INSTDIR"
SectionEnd
'''
        
        nsis_file = self.script_dir / "installer.nsi"
        with open(nsis_file, 'w', encoding='utf-8') as f:
            f.write(nsis_script)
        
        print(f"✅ Created NSIS script: {nsis_file}")
        
        # Try to compile with NSIS
        nsis_cmd = f"makensis {nsis_file}"
        if self.run_command(nsis_cmd):
            print("✅ NSIS installer created successfully")
            return True
        else:
            print("⚠️  NSIS not found. Install NSIS to create Windows installer")
            print("📥 Download from: https://nsis.sourceforge.io/Download")
            return False
    
    def create_linux_installer(self):
        """ایجاد نصب‌کننده برای Linux"""
        print("🐧 Creating Linux installer")
        
        # Create AppImage or DEB package script
        install_script = f'''#!/bin/bash
# {self.config.app_name} Linux Installer
# {self.config.copyright}

APP_NAME="{self.config.app_name}"
APP_VERSION="{self.config.app_version}"
INSTALL_DIR="/opt/$APP_NAME"
DESKTOP_FILE="/usr/share/applications/persian-file-copier-pro.desktop"

echo "🚀 Installing $APP_NAME v$APP_VERSION"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)" 
   exit 1
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy files
echo "📁 Copying application files..."
cp -r dist/* "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/{self.config.app_name.replace(' ', '_')}"

# Create desktop entry
echo "🖥️  Creating desktop entry..."
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name={self.config.app_name}
Comment={self.config.app_description}
Exec=$INSTALL_DIR/{self.config.app_name.replace(' ', '_')}
Icon=$INSTALL_DIR/icon.png
Terminal=false
Categories=Utility;FileManager;
EOF

# Create symlink
ln -sf "$INSTALL_DIR/{self.config.app_name.replace(' ', '_')}" "/usr/local/bin/persian-file-copier-pro"

echo "✅ Installation completed!"
echo "🚀 Run 'persian-file-copier-pro' from terminal or find it in applications menu"
'''
        
        install_file = self.script_dir / self.config.installer_dir / "install.sh"
        with open(install_file, 'w', encoding='utf-8') as f:
            f.write(install_script)
        
        # Make executable
        os.chmod(install_file, 0o755)
        
        print(f"✅ Created Linux installer: {install_file}")
        return True
    
    def create_portable_version(self):
        """ایجاد نسخه قابل حمل"""
        self.print_step(6, "Creating portable version")
        
        portable_dir = self.script_dir / self.config.installer_dir / "Portable"
        portable_dir.mkdir(exist_ok=True)
        
        # Copy executable and required files
        dist_dir = self.script_dir / self.config.dist_dir
        if dist_dir.exists():
            shutil.copytree(dist_dir, portable_dir / "app", dirs_exist_ok=True)
        
        # Create portable launcher
        if self.is_windows:
            launcher_content = f'''@echo off
title {self.config.app_name} - Portable
cd /d "%~dp0\\app"
start "" "{self.config.app_name.replace(" ", "_")}.exe"
'''
            launcher_file = portable_dir / f"Start_{self.config.app_name.replace(' ', '_')}.bat"
        else:
            launcher_content = f'''#!/bin/bash
cd "$(dirname "$0")/app"
./{self.config.app_name.replace(" ", "_")}
'''
            launcher_file = portable_dir / f"start_{self.config.app_name.replace(' ', '_').lower()}.sh"
            # Make executable
            os.chmod(launcher_file, 0o755)
        
        with open(launcher_file, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        # Copy README
        readme_src = self.script_dir / "README.md"
        if readme_src.exists():
            shutil.copy2(readme_src, portable_dir / "README.md")
        
        print(f"✅ Created portable version: {portable_dir}")
        return True
    
    def package_release(self):
        """بسته‌بندی نهایی"""
        self.print_step(7, "Packaging final release")
        
        # Create ZIP of portable version
        portable_dir = self.script_dir / self.config.installer_dir / "Portable"
        if portable_dir.exists():
            zip_name = f"{self.config.app_name.replace(' ', '_')}_v{self.config.app_version}_Portable"
            shutil.make_archive(
                self.script_dir / self.config.installer_dir / zip_name,
                'zip',
                portable_dir
            )
            print(f"✅ Created portable ZIP: {zip_name}.zip")
        
        return True
    
    def build(self):
        """فرآیند کامل ساخت"""
        print(f"🚀 Starting build process for {self.config.app_name} v{self.config.app_version}")
        print(f"🖥️  Platform: {platform.system()} {platform.machine()}")
        print(f"🐍 Python: {sys.version}")
        
        try:
            # Step by step build
            if not self.clean_build_dirs():
                return False
            
            if not self.check_dependencies():
                return False
            
            if not self.build_executable():
                return False
            
            if not self.create_installer_script():
                print("⚠️  Installer creation failed, but executable is ready")
            
            if not self.create_portable_version():
                print("⚠️  Portable version creation failed")
            
            if not self.package_release():
                print("⚠️  Release packaging failed")
            
            self.print_step("DONE", "Build process completed!")
            print("📁 Check the following directories:")
            print(f"   🎯 Executable: {self.script_dir / self.config.dist_dir}")
            print(f"   📦 Installer: {self.script_dir / self.config.installer_dir}")
            print(f"   💼 Portable: {self.script_dir / self.config.installer_dir / 'Portable'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return False

def main():
    """تابع اصلی"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(f"""
🔧 Persian File Copier Pro Build Script

Usage: python build_installer.py [options]

Options:
  --help    Show this help message
  
This script will:
  1. Clean previous builds
  2. Check and install dependencies  
  3. Create PyInstaller spec file
  4. Build executable
  5. Create installer (Windows NSIS / Linux script)
  6. Create portable version
  7. Package final release

Requirements:
  - PyInstaller
  - NSIS (for Windows installer)
  - All app dependencies (eel, psutil, etc.)
        """)
        return
    
    builder = BuildManager()
    success = builder.build()
    
    if success:
        print("\n🎉 Build completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()