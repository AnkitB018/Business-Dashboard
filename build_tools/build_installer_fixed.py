"""
Business Dashboard Build Script
This script creates a standalone installer for the Business Dashboard application.
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
import json

class BusinessDashboardBuilder:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent  # Go up one level from build_tools
        self.build_tools_dir = Path(__file__).parent  # Current build_tools directory
        self.dist_dir = self.build_tools_dir / "dist"
        self.build_dir = self.build_tools_dir / "build"
        self.installer_dir = self.build_tools_dir / "installer"
        self.temp_dir = self.build_tools_dir / "temp_build"
        
    def clean_build_dirs(self):
        """Clean previous build directories"""
        print("🧹 Cleaning previous build directories...")
        
        for dir_path in [self.dist_dir, self.build_dir, self.installer_dir, self.temp_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
        
        # Create fresh directories
        self.installer_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
    def build_main_application(self):
        """Build the main application executable"""
        print("🔨 Building main application executable...")
        
        # Create the spec content with proper paths and database config
        spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hiddenimports = [
    'tkinter',
    'customtkinter',
    'pymongo',
    'pandas',
    'matplotlib',
    'matplotlib.backends.backend_tkagg',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'numpy',
    'datetime',
    'logging',
    'json',
    'os',
    'sys',
    'threading',
    'queue',
    'configparser',
    'python-dotenv',
    'urllib.parse',
    'pathlib',
    'winreg',
    'requests',
    'packaging',
    'update_manager'
]

datas = [
    (r'{self.root_dir}\\*.py', '.'),
    (r'{self.root_dir}\\_docs', '_docs'),
    (r'{self.root_dir}\\LICENSE.md', '.'),
    (r'{self.root_dir}\\README.md', '.'),
    (r'{self.root_dir}\\requirements.txt', '.'),
    (r'{self.root_dir}\\.env.example', '.'),
]

a = Analysis(
    [r'{self.root_dir}\\app_gui.py'],
    pathex=[r'{self.root_dir}'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='BusinessDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BusinessDashboard'
)"""
        
        # Write updated spec file
        spec_file = self.build_tools_dir / "app_build.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # Build with PyInstaller
        try:
            cmd = f'pyinstaller --clean --noconfirm "{spec_file}"'
            result = subprocess.run(cmd, shell=True, cwd=self.root_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ PyInstaller failed: {result.stderr}")
                return False
            
            print("✅ Main application built successfully")
            return True
            
        except Exception as e:
            print(f"❌ Build failed: {str(e)}")
            return False
    
    def build_uninstaller(self):
        """Build the uninstaller executable"""
        print("🔨 Building uninstaller...")
        
        uninstaller_spec = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{self.root_dir}\\uninstaller.py'],
    pathex=[r'{self.root_dir}'],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'customtkinter', 'winreg', 'pathlib'],
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
    name='Uninstall',
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
)"""
        
        # Write uninstaller spec file
        uninstaller_spec_file = self.build_tools_dir / "uninstaller.spec"
        with open(uninstaller_spec_file, 'w') as f:
            f.write(uninstaller_spec)
        
        # Build uninstaller
        try:
            cmd = f'pyinstaller --clean --noconfirm "{uninstaller_spec_file}"'
            result = subprocess.run(cmd, shell=True, cwd=self.root_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Uninstaller build failed: {result.stderr}")
                return False
            
            print("✅ Uninstaller built successfully")
            return True
            
        except Exception as e:
            print(f"❌ Uninstaller build failed: {str(e)}")
            return False
    
    def create_installer_package(self):
        """Create the final installer package"""
        print("📦 Creating installer package...")
        
        # Copy built files to installer directory
        app_dist = self.root_dir / "dist" / "BusinessDashboard"
        uninstaller_exe = self.root_dir / "dist" / "Uninstall.exe"
        
        if not app_dist.exists():
            print("❌ Application build not found")
            return False
            
        # Copy application files
        app_dest = self.installer_dir / "app"
        app_dest.mkdir(exist_ok=True)
        shutil.copytree(app_dist, app_dest / "BusinessDashboard", dirs_exist_ok=True)
        
        # Copy uninstaller if it exists
        if uninstaller_exe.exists():
            shutil.copy2(uninstaller_exe, app_dest / "BusinessDashboard" / "Uninstall.exe")
        
        # Copy license and readme
        for file in ["LICENSE.md", "README.md"]:
            src_file = self.root_dir / file
            if src_file.exists():
                shutil.copy2(src_file, self.installer_dir / file)
        
        # Create NSIS installer if available
        if self.create_nsis_installer():
            print("✅ NSIS installer created successfully")
        else:
            # Fallback to ZIP package
            self.create_zip_package()
            print("✅ ZIP package created as fallback")
        
        return True
    
    def create_nsis_installer(self):
        """Create NSIS installer"""
        try:
            # Check if NSIS is installed
            nsis_path = None
            possible_paths = [
                "C:\\Program Files (x86)\\NSIS\\makensis.exe",
                "C:\\Program Files\\NSIS\\makensis.exe",
                "makensis.exe"  # In PATH
            ]
            
            for path in possible_paths:
                if shutil.which(path) or os.path.exists(path):
                    nsis_path = path
                    break
            
            if not nsis_path:
                print("⚠️ NSIS not found, will create ZIP package instead")
                return False
            
            # Update NSIS script with correct paths
            nsis_script = self.build_tools_dir / "installer.nsi"
            if not nsis_script.exists():
                print("⚠️ NSIS script not found")
                return False
                
            # Compile NSIS installer
            cmd = f'"{nsis_path}" "{nsis_script}"'
            result = subprocess.run(cmd, shell=True, cwd=self.build_tools_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ NSIS compilation failed: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ NSIS installer creation failed: {str(e)}")
            return False
    
    def create_zip_package(self):
        """Create ZIP package as fallback"""
        print("📦 Creating ZIP package...")
        
        zip_file = self.installer_dir / "BusinessDashboard_Portable.zip"
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add application files
            app_dir = self.installer_dir / "app" / "BusinessDashboard"
            if app_dir.exists():
                for file_path in app_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.installer_dir / "app")
                        zf.write(file_path, arcname)
            
            # Add documentation
            for file in ["LICENSE.md", "README.md"]:
                file_path = self.installer_dir / file
                if file_path.exists():
                    zf.write(file_path, file_path.name)
        
        print(f"✅ ZIP package created: {zip_file}")
    
    def build_all(self):
        """Build complete installer package"""
        print("🚀 Starting Business Dashboard build process...")
        print("=" * 60)
        
        try:
            # Clean previous builds
            self.clean_build_dirs()
            
            # Build main application
            if not self.build_main_application():
                print("❌ Main application build failed")
                return False
            
            # Build uninstaller
            if not self.build_uninstaller():
                print("⚠️ Uninstaller build failed, continuing without it")
            
            # Create installer package
            if not self.create_installer_package():
                print("❌ Installer package creation failed")
                return False
            
            print("=" * 60)
            print("🎉 Build process completed successfully!")
            print(f"📦 Installer files are in: {self.installer_dir}")
            
            return True
            
        except Exception as e:
            print(f"❌ Build process failed: {str(e)}")
            return False

def main():
    """Main function to run the build process"""
    builder = BusinessDashboardBuilder()
    success = builder.build_all()
    
    if success:
        print("\n✅ Build completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the installer on a clean system")
        print("2. Verify database configuration wizard works")
        print("3. Test uninstaller functionality")
        print("4. Distribute the installer to users")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
