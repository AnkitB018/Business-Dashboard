"""
GitHub Auto-Update Manager for Business Dashboard
Handles checking for updates from GitHub Releases and downloading new versions
"""

import requests
import json
import os
import sys
import subprocess
import tempfile
import threading
from datetime import datetime
from packaging import version
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)

class UpdateManager:
    def __init__(self, current_version="2.0.0", repo="AnkitB018/Business-Dashboard"):
        self.current_version = current_version
        self.repo = repo
        self.github_api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        self.update_window = None
        self.progress_var = None
        self.progress_bar = None
        
    def check_for_updates(self, show_no_update_message=True):
        """Check for updates from GitHub Releases"""
        try:
            logger.info(f"Checking for updates from {self.github_api_url}")
            
            # Make API request with timeout
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            
            release_info = response.json()
            
            # Extract version info
            latest_version = release_info['tag_name'].replace('v', '').replace('V', '')
            current_ver = self.current_version.replace('v', '').replace('V', '')
            
            logger.info(f"Current version: {current_ver}, Latest version: {latest_version}")
            
            # Compare versions
            if version.parse(latest_version) > version.parse(current_ver):
                # Find Windows installer asset
                download_url = None
                for asset in release_info.get('assets', []):
                    if asset['name'].endswith('.exe') or asset['name'].endswith('.msi'):
                        download_url = asset['browser_download_url']
                        break
                
                if not download_url:
                    logger.warning("No Windows installer found in latest release")
                    if show_no_update_message:
                        messagebox.showwarning("Update Check", 
                                             "Update available but no Windows installer found.")
                    return None
                
                update_info = {
                    'latest_version': latest_version,
                    'current_version': current_ver,
                    'download_url': download_url,
                    'release_notes': release_info.get('body', 'No release notes available'),
                    'release_date': release_info.get('published_at', ''),
                    'release_name': release_info.get('name', f'Version {latest_version}')
                }
                
                logger.info(f"Update available: {latest_version}")
                return update_info
                
            else:
                logger.info("No updates available")
                if show_no_update_message:
                    messagebox.showinfo("Update Check", 
                                      f"You are running the latest version ({current_ver})")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Update check timed out")
            if show_no_update_message:
                messagebox.showerror("Update Check", "Update check timed out. Please check your internet connection.")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during update check: {e}")
            if show_no_update_message:
                messagebox.showerror("Update Check", f"Failed to check for updates: {str(e)}")
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error during update check: {e}")
            if show_no_update_message:
                messagebox.showerror("Update Check", f"Update check failed: {str(e)}")
            return None
    
    def show_update_dialog(self, update_info):
        """Show update available dialog with release notes"""
        if self.update_window and self.update_window.winfo_exists():
            self.update_window.lift()
            return
            
        self.update_window = ctk.CTkToplevel()
        self.update_window.title("Update Available")
        self.update_window.geometry("650x580")
        self.update_window.resizable(False, False)
        
        # Center the window
        self.update_window.transient()
        self.update_window.grab_set()
        
        # Header
        header_frame = ctk.CTkFrame(self.update_window, height=80, corner_radius=10,
                                   fg_color=("#4CAF50", "#2E7D32"))
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20, pady=15)
        
        ctk.CTkLabel(
            header_content,
            text="🚀 Update Available",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_content,
            text=f"v{update_info['latest_version']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="right")
        
        # Content area
        content_frame = ctk.CTkFrame(self.update_window, corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Version info
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            info_frame,
            text=f"Current Version: {update_info['current_version']}",
            font=ctk.CTkFont(size=14),
            anchor="w"
        ).pack(fill="x")
        
        ctk.CTkLabel(
            info_frame,
            text=f"Latest Version: {update_info['latest_version']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            text_color=("#2E7D32", "#4CAF50")
        ).pack(fill="x")
        
        # Release notes
        notes_label = ctk.CTkLabel(
            content_frame,
            text="📝 What's New:",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        notes_label.pack(fill="x", padx=20, pady=(10, 5))
        
        # Scrollable text area for release notes
        notes_frame = ctk.CTkFrame(content_frame, corner_radius=8)
        notes_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        notes_text = ctk.CTkTextbox(
            notes_frame,
            height=200,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        notes_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Format and insert release notes
        notes_content = update_info['release_notes']
        if len(notes_content) > 1000:
            notes_content = notes_content[:1000] + "..."
        
        notes_text.insert("1.0", notes_content)
        notes_text.configure(state="disabled")
        
        # Buttons
        button_frame = ctk.CTkFrame(self.update_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            button_frame,
            text="❌ Skip Update",
            command=self.update_window.destroy,
            width=120,
            height=40,
            corner_radius=10,
            fg_color=("#757575", "#424242"),
            hover_color=("#616161", "#303030")
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="⬇️ Download & Install",
            command=lambda: self.download_and_install_update(update_info),
            width=160,
            height=40,
            corner_radius=10,
            fg_color=("#4CAF50", "#2E7D32"),
            hover_color=("#45A049", "#1B5E20")
        ).pack(side="right")
    
    def download_and_install_update(self, update_info):
        """Download and install the update"""
        # Disable buttons during download
        for widget in self.update_window.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkButton):
                        child.configure(state="disabled")
        
        # Show progress
        self.show_download_progress()
        
        # Start download in background thread
        download_thread = threading.Thread(
            target=self._download_worker,
            args=(update_info,),
            daemon=True
        )
        download_thread.start()
    
    def show_download_progress(self):
        """Show download progress dialog"""
        # Clear existing content
        for widget in self.update_window.winfo_children():
            widget.destroy()
        
        # Progress header
        header_frame = ctk.CTkFrame(self.update_window, height=80, corner_radius=10,
                                   fg_color=("#2196F3", "#1565C0"))
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="⬇️ Downloading Update...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(expand=True)
        
        # Progress content
        progress_frame = ctk.CTkFrame(self.update_window, corner_radius=10)
        progress_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            progress_frame,
            text="Please wait while the update is downloaded and installed...",
            font=ctk.CTkFont(size=14),
            wraplength=500
        ).pack(pady=30)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            height=20,
            variable=self.progress_var
        )
        self.progress_bar.pack(pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Preparing download...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=10)
    
    def _download_worker(self, update_info):
        """Background worker for downloading the update"""
        try:
            # Update status
            self.update_window.after(0, lambda: self.status_label.configure(text="Downloading installer..."))
            
            # Download the installer
            response = requests.get(update_info['download_url'], stream=True)
            response.raise_for_status()
            
            # Get file size for progress calculation
            total_size = int(response.headers.get('content-length', 0))
            
            # Create temporary file for installer
            temp_dir = tempfile.gettempdir()
            installer_filename = f"BusinessDashboard_Update_v{update_info['latest_version']}.exe"
            installer_path = os.path.join(temp_dir, installer_filename)
            
            # Download with progress updates
            downloaded = 0
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.update_window.after(0, lambda p=progress: self.progress_var.set(p/100))
                            self.update_window.after(0, lambda: self.status_label.configure(
                                text=f"Downloaded {downloaded//1024//1024}MB of {total_size//1024//1024}MB"))
            
            # Update status
            self.update_window.after(0, lambda: self.status_label.configure(text="Starting installer..."))
            self.update_window.after(0, lambda: self.progress_var.set(1.0))
            
            # Run installer
            logger.info(f"Running installer: {installer_path}")
            
            # Show completion message
            self.update_window.after(0, self._show_install_completion, installer_path)
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            self.update_window.after(0, lambda: messagebox.showerror(
                "Download Failed", f"Failed to download update: {str(e)}"))
            self.update_window.after(0, self.update_window.destroy)
    
    def _show_install_completion(self, installer_path):
        """Show installation completion dialog"""
        # Clear progress content
        for widget in self.update_window.winfo_children():
            widget.destroy()
        
        # Completion header
        header_frame = ctk.CTkFrame(self.update_window, height=80, corner_radius=10,
                                   fg_color=("#4CAF50", "#2E7D32"))
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="✅ Download Complete",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(expand=True)
        
        # Completion content
        content_frame = ctk.CTkFrame(self.update_window, corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            content_frame,
            text="The installer has been downloaded successfully.\nClick 'Install Now' to update your Business Dashboard.",
            font=ctk.CTkFont(size=14),
            justify="center"
        ).pack(pady=40)
        
        # Action buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="📁 Open Download Folder",
            command=lambda: self._open_download_folder(installer_path),
            width=180,
            height=40,
            corner_radius=10,
            fg_color=("#FF9800", "#E65100"),
            hover_color=("#F57C00", "#BF360C")
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="🚀 Install Now",
            command=lambda: self._run_installer_and_exit(installer_path),
            width=140,
            height=40,
            corner_radius=10,
            fg_color=("#4CAF50", "#2E7D32"),
            hover_color=("#45A049", "#1B5E20")
        ).pack(side="right")
    
    def _open_download_folder(self, installer_path):
        """Open the folder containing the downloaded installer"""
        try:
            folder_path = os.path.dirname(installer_path)
            subprocess.Popen(f'explorer /select,"{installer_path}"')
        except Exception as e:
            logger.error(f"Failed to open download folder: {e}")
    
    def _run_installer_and_exit(self, installer_path):
        """Run the installer and exit the current application"""
        try:
            # Close update window
            self.update_window.destroy()
            
            # Run installer
            subprocess.Popen([installer_path])
            
            # Show exit message
            if messagebox.askyesno("Install Update", 
                                 "The installer will start now. Close Business Dashboard to complete the update?"):
                # Exit the application
                sys.exit(0)
                
        except Exception as e:
            logger.error(f"Failed to run installer: {e}")
            messagebox.showerror("Installation Failed", f"Failed to start installer: {str(e)}")

# Convenience function for easy integration
def check_for_updates_async(parent_window=None, current_version="2.0.0", show_no_update=True):
    """Check for updates in a background thread"""
    def worker():
        try:
            update_manager = UpdateManager(current_version=current_version)
            update_info = update_manager.check_for_updates(show_no_update_message=show_no_update)
            
            if update_info and parent_window:
                # Show update dialog in main thread
                parent_window.after(0, lambda: update_manager.show_update_dialog(update_info))
                
        except Exception as e:
            logger.error(f"Background update check failed: {e}")
    
    # Start background thread
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
