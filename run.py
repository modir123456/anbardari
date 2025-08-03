#!/usr/bin/env python3
"""
Persian File Copier Pro - Launcher Script
This script checks dependencies and launches the application
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    try:
        import tkinter
        print("✓ tkinter is available")
    except ImportError:
        missing_deps.append("tkinter (install with: apt install python3-tk)")
    
    try:
        import customtkinter
        print(f"✓ customtkinter {customtkinter.__version__}")
    except ImportError:
        missing_deps.append("customtkinter (install with: pip install customtkinter)")
    
    if missing_deps:
        print("\n❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        return False
    
    return True

def install_customtkinter():
    """Try to install customtkinter automatically"""
    print("\n🔧 Attempting to install customtkinter...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
        print("✓ customtkinter installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install customtkinter automatically")
        print("Please install manually with: pip install customtkinter")
        return False

def launch_application():
    """Launch the main application"""
    try:
        from file_copier_app import main
        print("\n🚀 Launching Persian File Copier Pro...")
        main()
    except ImportError as e:
        print(f"❌ Failed to import application: {e}")
        return False
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("=" * 50)
    print("Persian File Copier Pro - Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        # Try to install customtkinter if it's the only missing dependency
        try:
            import tkinter
            # tkinter is available, try to install customtkinter
            if install_customtkinter():
                # Recheck dependencies
                if not check_dependencies():
                    sys.exit(1)
            else:
                sys.exit(1)
        except ImportError:
            print("\n💡 Installation instructions:")
            print("1. Install tkinter: sudo apt install python3-tk (Linux)")
            print("2. Install customtkinter: pip install customtkinter")
            sys.exit(1)
    
    # Launch the application
    if not launch_application():
        sys.exit(1)

if __name__ == "__main__":
    main()