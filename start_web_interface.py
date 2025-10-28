#!/usr/bin/env python3
"""
NodeA Web Interface Startup Script
Starts the Flask web application with all necessary components
"""

import os
import sys
import subprocess
import threading
import time
from datetime import datetime

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'tensorflow', 'numpy', 'matplotlib', 
        'PIL', 'sklearn', 'web3', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'sklearn':
                import sklearn
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install missing packages with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_files():
    """Check if all required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = [
        'web_interface.py',
        'train.py',
        'file_transfer_client.py',
        'global_model_receiver.py',
        'templates/base.html',
        'templates/index.html',
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        'templates',
        'static/css',
        'static/js',
        'uploads',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ {directory}/")

def start_web_interface():
    """Start the Flask web interface"""
    print("\n🚀 Starting NodeA Web Interface...")
    print("=" * 60)
    print("🌐 Web Interface: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000")
    print("🧠 Training: http://localhost:5000/training")
    print("📁 Models: http://localhost:5000/models")
    print("🔄 Transfer: http://localhost:5000/transfer")
    print("📋 Logs: http://localhost:5000/logs")
    print("⚙️ Settings: http://localhost:5000/settings")
    print("=" * 60)
    print("💡 Press Ctrl+C to stop the web interface")
    print("=" * 60)
    
    try:
        # Start the Flask application
        subprocess.run([sys.executable, 'web_interface.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting web interface: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

def main():
    """Main function"""
    print("🔧 NodeA Web Interface Startup")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('web_interface.py'):
        print("❌ web_interface.py not found in current directory")
        print("💡 Please run this script from the nodeA directory")
        return False
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        return False
    
    # Check files
    if not check_files():
        print("\n❌ File check failed")
        return False
    
    # Create directories
    create_directories()
    
    # Start web interface
    start_web_interface()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
