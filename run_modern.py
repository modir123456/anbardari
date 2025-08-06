#!/usr/bin/env python3
"""
Persian File Copier Pro - Modern Version Runner
🚀 FastAPI + Modern UI
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def start_modern_backend():
    """Start the modern FastAPI backend"""
    print("🚀 Starting Persian File Copier Pro - Modern Version...")
    print("📡 Backend: FastAPI + WebSockets")
    print("🎨 Frontend: Modern HTML + TailwindCSS")
    print("-" * 50)
    
    try:
        # Start FastAPI backend
        print("🔧 Starting FastAPI backend on port 8000...")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], cwd=Path(__file__).parent)
        
        # Wait for backend to start
        time.sleep(3)
        
        # Test backend
        try:
            import urllib.request
            with urllib.request.urlopen('http://localhost:8000/api/health') as response:
                if response.status == 200:
                    print("✅ Backend started successfully!")
                else:
                    print("❌ Backend health check failed")
                    return None
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return None
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def open_ui():
    """Open the modern UI in browser"""
    ui_file = Path(__file__).parent / "test_modern_ui.html"
    
    if ui_file.exists():
        file_url = f"file://{ui_file.absolute()}"
        print(f"🌐 Opening Modern UI: {file_url}")
        try:
            webbrowser.open(file_url)
            return True
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
            print(f"📂 Please manually open: {file_url}")
            return False
    else:
        print("❌ UI file not found")
        return False

def main():
    """Main function"""
    print("🚀 Persian File Copier Pro - Modern Version")
    print("=" * 50)
    
    # Start backend
    backend_process = start_modern_backend()
    if not backend_process:
        print("❌ Failed to start application")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Application is running!")
    print("🌐 Backend API: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🎨 Modern UI: Will open automatically")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    # Open UI
    open_ui()
    
    try:
        # Keep running
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ Application stopped")

if __name__ == "__main__":
    main()