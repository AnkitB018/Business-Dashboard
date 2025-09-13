"""
Business Dashboard Uninstaller
Completely removes the Business Dashboard application and user data
"""

import os
import sys
import shutil
import winreg
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from pathlib import Path
import json

class BusinessDashboardUninstaller:
    def __init__(self):
        self.app_name = "Business Dashboard"
        self.install_dir = self.get_install_directory()
        self.user_data_dir = Path.home() / "BusinessDashboard"
        self.desktop_shortcut = Path.home() / "Desktop" / "Business Dashboard.lnk"
        self.start_menu_shortcut = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Business Dashboard.lnk"
        
    def get_install_directory(self):
        """Get the installation directory from registry"""
        try:
            # Try to read from registry
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BusinessDashboard")
            install_dir, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            return Path(install_dir)
        except:
            # Fallback to common installation paths
            possible_paths = [
                Path("C:/Program Files/Business Dashboard"),
                Path("C:/Program Files (x86)/Business Dashboard"),
                Path.home() / "AppData" / "Local" / "Business Dashboard"
            ]
            for path in possible_paths:
                if path.exists():
                    return path
            return None
    
    def show_uninstall_dialog(self):
        """Show the uninstall confirmation dialog"""
        self.window = ctk.CTk()
        self.window.title("Uninstall Business Dashboard")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.create_uninstall_interface()
        self.window.mainloop()
    
    def create_uninstall_interface(self):
        """Create the uninstall interface"""
        # Main frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon and title
        title_frame = ctk.CTkFrame(main_frame)
        title_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🗑️ Uninstall Business Dashboard",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Warning message
        warning_frame = ctk.CTkFrame(main_frame)
        warning_frame.pack(fill="x", padx=20, pady=10)
        
        warning_label = ctk.CTkLabel(
            warning_frame,
            text="⚠️ WARNING",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="red"
        )
        warning_label.pack(pady=(20, 10))
        
        warning_text = ctk.CTkLabel(
            warning_frame,
            text="This will completely remove Business Dashboard from your computer.\\n\\nThe following will be deleted:",
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        warning_text.pack(pady=(0, 20))
        
        # Items to be removed
        items_frame = ctk.CTkFrame(main_frame)
        items_frame.pack(fill="x", padx=20, pady=10)
        
        items_text = [
            "✓ Application files and executable",
            "✓ Desktop and Start Menu shortcuts",
            "✓ User configuration and database settings",
            "✓ Application logs and cache files",
            "✓ Registry entries"
        ]
        
        for item in items_text:
            item_label = ctk.CTkLabel(
                items_frame,
                text=item,
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            item_label.pack(anchor="w", padx=20, pady=2)
        
        # Keep user data option
        self.keep_data = ctk.BooleanVar(value=False)
        keep_data_check = ctk.CTkCheckBox(
            main_frame,
            text="Keep user data and configuration files",
            variable=self.keep_data,
            font=ctk.CTkFont(size=12)
        )
        keep_data_check.pack(pady=20)
        
        # Progress bar (hidden initially)
        self.progress_frame = ctk.CTkFrame(main_frame)
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Uninstalling...",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(padx=20, pady=(0, 20))
        self.progress_bar.set(0)
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.cancel_uninstall,
            height=40,
            width=120,
            font=ctk.CTkFont(size=14),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        cancel_button.pack(side="left", padx=20, pady=20)
        
        self.uninstall_button = ctk.CTkButton(
            buttons_frame,
            text="Uninstall",
            command=self.confirm_uninstall,
            height=40,
            width=120,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#DC2626",
            hover_color="#B91C1C"
        )
        self.uninstall_button.pack(side="right", padx=20, pady=20)
    
    def confirm_uninstall(self):
        """Confirm uninstallation"""
        result = messagebox.askyesno(
            "Confirm Uninstall",
            "Are you sure you want to uninstall Business Dashboard?\\n\\nThis action cannot be undone.",
            icon="warning"
        )
        
        if result:
            self.start_uninstall()
    
    def start_uninstall(self):
        """Start the uninstall process"""
        # Show progress frame
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        self.uninstall_button.configure(state="disabled")
        
        # Run uninstall in thread to prevent GUI freezing
        import threading
        thread = threading.Thread(target=self.perform_uninstall)
        thread.daemon = True
        thread.start()
    
    def perform_uninstall(self):
        """Perform the actual uninstallation"""
        try:
            steps = [
                ("Stopping application processes...", self.stop_app_processes),
                ("Removing application files...", self.remove_app_files),
                ("Removing shortcuts...", self.remove_shortcuts),
                ("Removing registry entries...", self.remove_registry_entries),
                ("Removing user data...", self.remove_user_data),
                ("Cleaning up...", self.cleanup)
            ]
            
            total_steps = len(steps)
            
            for i, (message, action) in enumerate(steps):
                self.update_progress(message, i / total_steps)
                action()
                
            self.update_progress("Uninstall completed!", 1.0)
            
            # Show completion message
            self.window.after(1000, self.show_completion)
            
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Error", f"Uninstall failed: {str(e)}"))
    
    def update_progress(self, message, progress):
        """Update progress bar and message"""
        self.window.after(0, lambda: self.progress_label.configure(text=message))
        self.window.after(0, lambda: self.progress_bar.set(progress))
        self.window.after(0, self.window.update)
    
    def stop_app_processes(self):
        """Stop any running application processes"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                if 'BusinessDashboard' in proc.info['name']:
                    proc.terminate()
        except:
            pass
    
    def remove_app_files(self):
        """Remove application files"""
        if self.install_dir and self.install_dir.exists():
            try:
                shutil.rmtree(self.install_dir)
            except Exception as e:
                print(f"Error removing app files: {e}")
    
    def remove_shortcuts(self):
        """Remove desktop and start menu shortcuts"""
        shortcuts = [self.desktop_shortcut, self.start_menu_shortcut]
        
        for shortcut in shortcuts:
            try:
                if shortcut.exists():
                    shortcut.unlink()
            except Exception as e:
                print(f"Error removing shortcut {shortcut}: {e}")
    
    def remove_registry_entries(self):
        """Remove registry entries"""
        try:
            # Remove uninstall entry
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\BusinessDashboard")
        except:
            pass
    
    def remove_user_data(self):
        """Remove user data if not keeping it"""
        if not self.keep_data.get() and self.user_data_dir.exists():
            try:
                shutil.rmtree(self.user_data_dir)
            except Exception as e:
                print(f"Error removing user data: {e}")
    
    def cleanup(self):
        """Final cleanup"""
        # Remove any remaining temp files
        import tempfile
        temp_dir = Path(tempfile.gettempdir())
        
        for item in temp_dir.glob("BusinessDashboard*"):
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except:
                pass
    
    def show_completion(self):
        """Show uninstall completion message"""
        messagebox.showinfo(
            "Uninstall Complete",
            "Business Dashboard has been successfully removed from your computer."
        )
        self.window.destroy()
    
    def cancel_uninstall(self):
        """Cancel the uninstall process"""
        self.window.destroy()

def main():
    """Main function to run the uninstaller"""
    if len(sys.argv) > 1 and sys.argv[1] == "/S":
        # Silent uninstall
        uninstaller = BusinessDashboardUninstaller()
        uninstaller.perform_uninstall()
    else:
        # Interactive uninstall
        uninstaller = BusinessDashboardUninstaller()
        uninstaller.show_uninstall_dialog()

if __name__ == "__main__":
    main()
