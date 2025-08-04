#!/usr/bin/env python3
"""
Build script for Serial Number Generator
Creates standalone executable for license management
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_serial_generator():
    """Build the serial generator executable"""
    print("🔑 Building Serial Number Generator...")
    
    # Clean previous builds
    if os.path.exists('dist_serial'):
        shutil.rmtree('dist_serial')
    if os.path.exists('build_serial'):
        shutil.rmtree('build_serial')
    
    # Create spec file for serial generator
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['serial_generator.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'customtkinter',
        'hashlib',
        'base64',
        'uuid',
        'csv',
        'datetime'
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
    name='Serial_Generator',
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
    icon='app_icon.ico',
)
'''
    
    with open('serial_generator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    # Build using PyInstaller
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--distpath=dist_serial',
            '--workpath=build_serial',
            'serial_generator.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✓ Serial Generator built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def create_license_package():
    """Create a complete licensing package"""
    print("📦 Creating licensing package...")
    
    # Create licensing directory
    license_dir = Path("dist_serial/licensing_package")
    license_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy serial generator executable
    if os.path.exists("dist_serial/Serial_Generator.exe"):
        shutil.copy2("dist_serial/Serial_Generator.exe", license_dir)
    elif os.path.exists("dist_serial/Serial_Generator"):
        shutil.copy2("dist_serial/Serial_Generator", license_dir)
    
    # Create usage instructions
    instructions = """
Persian File Copier Pro - Licensing System
==========================================

This package contains the Serial Number Generator for Persian File Copier Pro.

Files included:
- Serial_Generator.exe (or Serial_Generator on Linux/Mac)
- This README file

How to use:
1. Run the Serial_Generator executable
2. Enter customer information (name and email)
3. Select license type (standard, professional, enterprise, lifetime)
4. Click "Generate Serial Number"
5. Copy the generated serial and provide it to the customer

Features:
- Generate unique serial numbers for each customer
- Track all generated licenses
- Export license data to CSV
- Email template generation
- Customer information management

For support contact:
Email: support@persianfile.ir
Phone: +98 21 1234 5678

© 2024 Persian File Technology Company
All rights reserved.
"""
    
    with open(license_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    # Create batch file for Windows
    batch_content = """@echo off
echo Persian File Copier Pro - Serial Generator
echo ==========================================
echo.
echo Starting Serial Number Generator...
echo.
Serial_Generator.exe
pause
"""
    
    with open(license_dir / "run_generator.bat", "w") as f:
        f.write(batch_content)
    
    # Create shell script for Linux/Mac
    shell_content = """#!/bin/bash
echo "Persian File Copier Pro - Serial Generator"
echo "=========================================="
echo
echo "Starting Serial Number Generator..."
echo
./Serial_Generator
"""
    
    with open(license_dir / "run_generator.sh", "w") as f:
        f.write(shell_content)
    
    # Make shell script executable
    try:
        os.chmod(license_dir / "run_generator.sh", 0o755)
    except:
        pass  # Windows doesn't support chmod
    
    print("✓ Licensing package created successfully")

def main():
    """Main build process for serial generator"""
    print("=" * 50)
    print("Persian File Copier Pro - Serial Generator Build")
    print("=" * 50)
    
    # Check if serial_generator.py exists
    if not os.path.exists('serial_generator.py'):
        print("❌ serial_generator.py not found.")
        sys.exit(1)
    
    # Create icon if it doesn't exist
    if not os.path.exists('app_icon.ico'):
        print("🎨 Creating application icon...")
        try:
            subprocess.check_call([sys.executable, "create_icon.py"])
        except:
            print("⚠ Could not create icon, continuing without it...")
    
    # Build serial generator
    if not build_serial_generator():
        sys.exit(1)
    
    # Create licensing package
    create_license_package()
    
    print("\n" + "=" * 50)
    print("✅ SERIAL GENERATOR BUILD COMPLETED!")
    print("=" * 50)
    print("Files created in 'dist_serial/licensing_package' directory:")
    print("- Serial_Generator.exe (Windows) or Serial_Generator (Linux/Mac)")
    print("- README.txt (usage instructions)")
    print("- run_generator.bat (Windows launcher)")
    print("- run_generator.sh (Linux/Mac launcher)")
    print("\nYour licensing system is ready!")

if __name__ == "__main__":
    main()