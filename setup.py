"""
Setup script for HR Management System - MongoDB Edition
This script helps set up the application and dependencies
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported")
        print("Please install Python 3.8 or higher")
        return False

def install_dependencies():
    """Install Python dependencies"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def check_mongodb():
    """Check if MongoDB is accessible"""
    try:
        import pymongo
        client = pymongo.MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
        return True
    except ImportError:
        print("❌ PyMongo not installed")
        return False
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\nPlease ensure MongoDB is installed and running:")
        print("1. Download from: https://www.mongodb.com/download-center/community")
        print("2. Install MongoDB Community Edition")
        print("3. Start MongoDB service")
        print("4. Ensure it's running on localhost:27017")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if platform.system() != "Windows":
        return False
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "HR Management System.lnk")
        target = os.path.join(os.getcwd(), "run_hr_system.bat")
        wDir = os.getcwd()
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = target
        shortcut.save()
        
        print("✅ Desktop shortcut created")
        return True
    except ImportError:
        print("⚠️ Could not create desktop shortcut (missing winshell/pywin32)")
        return False
    except Exception as e:
        print(f"⚠️ Could not create desktop shortcut: {e}")
        return False

def main():
    """Main setup function"""
    print("HR Management System - Setup Script")
    print("====================================")
    
    # Check Python version
    if not check_python():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check MongoDB
    mongodb_ok = check_mongodb()
    
    # Create desktop shortcut (Windows only)
    if platform.system() == "Windows":
        create_desktop_shortcut()
    
    print("\n" + "="*50)
    print("SETUP SUMMARY")
    print("="*50)
    
    print("✅ Python dependencies installed")
    
    if mongodb_ok:
        print("✅ MongoDB connection verified")
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python migrate_to_mongo.py (if you have Excel data)")
        print("2. Run: python app_mongo.py (for web interface)")
        print("3. Or run: python gui_launcher.py (for desktop GUI)")
        print("4. Or double-click: run_hr_system.bat")
    else:
        print("⚠️ MongoDB connection issues detected")
        print("\n⚠️ Setup completed with warnings")
        print("\nPlease install and start MongoDB, then:")
        print("1. Run this setup script again")
        print("2. Or manually test MongoDB connection")
    
    if platform.system() == "Windows":
        print("\n📍 Desktop shortcut created (if supported)")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\nSetup cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error during setup: {e}")
        input("Press Enter to exit...")
