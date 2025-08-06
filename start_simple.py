#!/usr/bin/env python3
"""
Persian File Copier Pro - Modern Launcher
🚀 FastAPI backend with modern HTML interface
شرکت فناوری نوآوران مثبت سبز
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    packages = [
        "fastapi",
        "uvicorn[standard]", 
        "websockets",
        "pydantic",
        "psutil",
        "aiofiles",
        "python-multipart"
    ]
    
    try:
        for package in packages:
            print(f"   Installing {package}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", package, "--break-system-packages"
            ], capture_output=True, check=True)
        
        print("✅ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    
    # Check if backend directory exists
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
        print("⏳ Waiting for backend to start...")
        time.sleep(5)
        
        # Test connection
        try:
            import urllib.request
            with urllib.request.urlopen('http://localhost:8000/api/health') as response:
                if response.status == 200:
                    print("✅ Backend started successfully!")
                    return process
        except Exception as e:
            print(f"⚠️ Backend health check failed: {e}")
            # Continue anyway, might still work
            return process
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def open_interface():
    """Open the web interface"""
    
    # Try different interface options
    interfaces = [
        ("Modern UI", "http://localhost:8000"),
        ("API Documentation", "http://localhost:8000/docs"),
    ]
    
    print("\n🌐 Available interfaces:")
    for i, (name, url) in enumerate(interfaces, 1):
        print(f"   {i}. {name} - {url}")
    
    # Auto-open the main interface
    main_url = "http://localhost:8000"
    print(f"\n🚀 Opening: {main_url}")
    try:
        webbrowser.open(main_url)
    except:
        print(f"📋 Please manually open: {main_url}")

def main():
    """Main function"""
    print("🚀 Persian File Copier Pro - Modern Launcher")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Persian File Copier Pro is running!")
    print("🌐 Main Interface: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    # Open interface
    open_interface()
    
    try:
        print("\n📡 Backend is running... Press Ctrl+C to stop")
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        print("✅ Application stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()