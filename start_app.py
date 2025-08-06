#!/usr/bin/env python3
"""
Persian File Copier Pro - Startup Script
🚀 Modern file management with React + FastAPI
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check Node.js (if frontend exists)
    frontend_path = Path("frontend")
    if frontend_path.exists():
        try:
            subprocess.run(["node", "--version"], capture_output=True, check=True)
            subprocess.run(["npm", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Node.js and npm are required for frontend")
            return False
    
    print("✅ Dependencies check passed")
    return True

def install_backend_deps():
    """Install backend dependencies"""
    print("📦 Installing backend dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ], check=True)
        print("✅ Backend dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install backend dependencies")
        return False

def install_frontend_deps():
    """Install frontend dependencies"""
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        return True
        
    print("📦 Installing frontend dependencies...")
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True)
        print("✅ Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install frontend dependencies")
        return False

def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    try:
        return subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start React frontend"""
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        return None
        
    print("🚀 Starting React frontend...")
    try:
        return subprocess.Popen(["npm", "run", "dev"], cwd="frontend")
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main function"""
    print("🚀 Persian File Copier Pro - Starting Application...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Install dependencies
    if not install_backend_deps():
        sys.exit(1)
    
    if not install_frontend_deps():
        sys.exit(1)
    
    # Start services
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    frontend_process = start_frontend()
    
    print("\n" + "=" * 50)
    print("✅ Application started successfully!")
    print("🌐 Backend API: http://localhost:8000")
    print("🌐 Frontend: http://localhost:3000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    # Open browser
    try:
        if frontend_process:
            webbrowser.open("http://localhost:3000")
        else:
            webbrowser.open("http://localhost:8000")
    except:
        pass
    
    try:
        # Wait for processes
        if frontend_process:
            frontend_process.wait()
        else:
            backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        
        print("✅ Application stopped")

if __name__ == "__main__":
    main()