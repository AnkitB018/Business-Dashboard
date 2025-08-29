"""
Build script to create executable for HR Management System
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error code {e.returncode}")
        return False

def install_build_tools():
    """Install PyInstaller"""
    return run_command(
        f"{sys.executable} -m pip install pyinstaller",
        "Installing PyInstaller"
    )

def build_executable():
    """Build the executable"""
    # PyInstaller command for GUI launcher
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=HR_Management_System",
        "--add-data=requirements.txt;.",
        "--add-data=config.py;.",
        "--add-data=README_MONGO.md;.",
        "--hidden-import=pymongo",
        "--hidden-import=dash",
        "--hidden-import=plotly",
        "gui_launcher.py"
    ]
    
    return run_command(
        " ".join(pyinstaller_cmd),
        "Building executable"
    )

def create_installer_files():
    """Create additional files for distribution"""
    try:
        # Create a simple README for the executable
        readme_content = """
HR Management System - Executable Version

REQUIREMENTS:
1. MongoDB must be installed and running
2. Python is NOT required (included in executable)

INSTALLATION:
1. Extract all files to a folder
2. Install MongoDB from https://www.mongodb.com/download-center/community
3. Start MongoDB service
4. Run HR_Management_System.exe

FIRST TIME SETUP:
1. Click "Connect to MongoDB"
2. Click "Initialize Database"
3. If you have Excel data, click "Migrate from Excel"
4. Click "Start HR Dashboard"

For support, see README_MONGO.md
"""
        
        with open("dist/README_EXECUTABLE.txt", "w") as f:
            f.write(readme_content)
        
        print("✅ Created README_EXECUTABLE.txt")
        return True
        
    except Exception as e:
        print(f"❌ Error creating installer files: {e}")
        return False

def main():
    """Main build function"""
    print("HR Management System - Build Script")
    print("==================================")
    
    # Check if we're in the right directory
    if not os.path.exists("gui_launcher.py"):
        print("❌ gui_launcher.py not found. Please run from project directory.")
        return False
    
    # Install build tools
    if not install_build_tools():
        return False
    
    # Build executable
    if not build_executable():
        return False
    
    # Create additional files
    create_installer_files()
    
    print("\n" + "="*50)
    print("BUILD SUMMARY")
    print("="*50)
    
    if os.path.exists("dist/HR_Management_System.exe"):
        print("✅ Executable built successfully!")
        print(f"📂 Location: {os.path.abspath('dist/HR_Management_System.exe')}")
        
        # Get file size
        size = os.path.getsize("dist/HR_Management_System.exe")
        size_mb = size / (1024 * 1024)
        print(f"📊 Size: {size_mb:.1f} MB")
        
        print("\n📋 Distribution files:")
        for file in os.listdir("dist"):
            print(f"   • {file}")
        
        print("\n📝 Next steps:")
        print("1. Test the executable on your system")
        print("2. Copy the 'dist' folder to target machines")
        print("3. Ensure MongoDB is installed on target machines")
        print("4. Run HR_Management_System.exe")
        
    else:
        print("❌ Executable build failed")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\nBuild cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error during build: {e}")
        input("Press Enter to exit...")
