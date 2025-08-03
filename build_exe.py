#!/usr/bin/env python3
"""
Persian File Copier Pro - Build Script
Creates standalone executable with all dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} is available")
        return True
    except ImportError:
        print("❌ PyInstaller not found")
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("🔧 Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "--break-system-packages"])
        print("✓ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠ PyInstaller may already be installed, continuing...")
        return True

def install_dependencies():
    """Install all required dependencies"""
    print("🔧 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--break-system-packages"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠ Dependencies may already be installed, continuing...")
        return True

def create_spec_file():
    """Create PyInstaller spec file with custom configuration"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['file_copier_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'customtkinter',
        'psutil',
        'tkinterdnd2',
        'PIL',
        'PIL._tkinter_finder'
    ],
    hookspath=[],
    hooksconfig={},
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
    name='Persian_File_Copier_Pro',
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
    icon=None,
)
'''
    
    with open('file_copier_app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🚀 Building executable...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("✓ Cleaned previous build")
    
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("✓ Cleaned build cache")
    
    try:
        # Build with spec file
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "file_copier_app.spec"
        ])
        print("✓ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build executable: {e}")
        return False

def create_installer_script():
    """Create an installer script for Windows"""
    installer_content = '''@echo off
echo ================================
echo Persian File Copier Pro Installer
echo ================================
echo.

:: Check if target directory exists
if not exist "C:\\Persian_File_Copier_Pro" (
    mkdir "C:\\Persian_File_Copier_Pro"
)

:: Copy executable
echo Installing Persian File Copier Pro...
copy "Persian_File_Copier_Pro.exe" "C:\\Persian_File_Copier_Pro\\"

:: Create desktop shortcut
echo Creating desktop shortcut...
set SCRIPT="%TEMP%\\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\\Desktop\\Persian File Copier Pro.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "C:\\Persian_File_Copier_Pro\\Persian_File_Copier_Pro.exe" >> %SCRIPT%
echo oLink.WorkingDirectory = "C:\\Persian_File_Copier_Pro" >> %SCRIPT%
echo oLink.Description = "Persian File Copier Pro - Advanced File Management Tool" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

:: Create start menu entry
echo Creating start menu entry...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Persian File Copier Pro" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Persian File Copier Pro"
)

set SCRIPT="%TEMP%\\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Persian File Copier Pro\\Persian File Copier Pro.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "C:\\Persian_File_Copier_Pro\\Persian_File_Copier_Pro.exe" >> %SCRIPT%
echo oLink.WorkingDirectory = "C:\\Persian_File_Copier_Pro" >> %SCRIPT%
echo oLink.Description = "Persian File Copier Pro - Advanced File Management Tool" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%

echo.
echo ================================
echo Installation completed successfully!
echo You can now run Persian File Copier Pro from:
echo - Desktop shortcut
echo - Start Menu
echo - C:\\Persian_File_Copier_Pro\\Persian_File_Copier_Pro.exe
echo ================================
pause
'''
    
    os.makedirs('dist', exist_ok=True)
    with open('dist/install.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    print("✓ Created Windows installer script")

def create_readme():
    """Create README for the distribution"""
    readme_content = '''# Persian File Copier Pro - Standalone Executable

## Installation and Usage

### Windows:
1. Run `install.bat` as Administrator to install the application system-wide
2. Or simply run `Persian_File_Copier_Pro.exe` directly

### Linux:
1. Make the executable runnable: `chmod +x Persian_File_Copier_Pro`
2. Run: `./Persian_File_Copier_Pro`

## Features:
- ✅ Colored tabs for different sections
- ✅ B Nazanin font support (if installed on system)
- ✅ Full drag and drop functionality
- ✅ Advanced file copying with progress tracking
- ✅ Multi-threaded operations
- ✅ Persian/Farsi interface

## System Requirements:
- Windows 10/11 or Linux with GUI
- 50MB free disk space
- No additional dependencies required (all bundled)

## Font Installation (Optional):
For best experience, install B Nazanin font on your system:
- Windows: Copy font files to C:\\Windows\\Fonts\\
- Linux: Copy font files to ~/.local/share/fonts/ or /usr/share/fonts/

## Support:
If you encounter any issues, please check that you have:
1. Proper file permissions
2. Sufficient disk space
3. Modern operating system (Windows 10+ or recent Linux distribution)
'''
    
    os.makedirs('dist', exist_ok=True)
    with open('dist/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✓ Created distribution README")

def main():
    """Main build process"""
    print("=" * 50)
    print("Persian File Copier Pro - Build Script")
    print("=" * 50)
    
    # Check current directory
    if not os.path.exists('file_copier_app.py'):
        print("❌ file_copier_app.py not found. Run this script from the project directory.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check/install PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            sys.exit(1)
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    # Create additional files
    create_installer_script()
    create_readme()
    
    print("\n" + "=" * 50)
    print("✅ BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("Files created in 'dist' directory:")
    print("- Persian_File_Copier_Pro.exe (or Persian_File_Copier_Pro on Linux)")
    print("- install.bat (Windows installer)")
    print("- README.txt (installation instructions)")
    print("\nYour standalone executable is ready!")
    print("All dependencies are bundled - no additional installation required.")

if __name__ == "__main__":
    main()