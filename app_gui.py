"""
Business Dashboard - Desktop GUI Application
© 2025 Antrocraft and Arolive Build. All Rights Reserved.

Created by: Antrocraft and Arolive Build
Owned by: Ankit Banerjee and Aritra Banerjee
Licensed for Business Use by: M/s Designo (Owner: Anupam Das)

PROPRIETARY SOFTWARE - UNAUTHORIZED USE PROHIBITED
This software is licensed exclusively to M/s Designo for internal business operations.
Any unauthorized use, copying, distribution, or sharing is strictly prohibited.

Main application file with automatic routing and database initialization
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import sys
import os
from database import get_db_manager
from data_service import HRDataService
from logger_config import get_logger, log_function_call, log_info, log_error
import logging
import time
from datetime import datetime

# Import GUI pages
from data_page_gui import ModernDataPageGUI
from reports_page_gui import ModernReportsPageGUI
from settings_page_gui import SettingsPageGUI

# Initialize enhanced logging system
dashboard_logger = get_logger()
logger = dashboard_logger.main_logger

class HRManagementApp:
    @log_function_call
    def __init__(self):
        try:
            # Log application startup
            dashboard_logger.log_app_start()
            log_info("Initializing Business Dashboard Application", "APP_INIT")
            
            # Set modern appearance with improved theme
            ctk.set_appearance_mode("light")  # Modern light mode
            ctk.set_default_color_theme("blue")
            log_info("CustomTkinter theme configured", "APP_INIT")
            
            # Create main window with modern styling
            self.root = ctk.CTk()
            self.root.title("🏢 Business Dashboard - Enterprise Edition")
            
            # Set window state and properties for better positioning
            self.root.state('normal')  # Ensure normal window state
            self.root.resizable(True, True)  # Allow resizing
            
            # Set initial size and position
            self.root.geometry("1600x1000")
            self.root.minsize(1400, 900)
            log_info("Main window created with dimensions 1600x1000", "APP_INIT")
            
            # Modern color scheme for light theme
            self.colors = {
                'primary': '#F8FAFC',      # Light gray background
                'secondary': '#E5E7EB',    # Light medium gray
                'accent': '#3B82F6',       # Blue (same)
                'success': '#10B981',      # Green (same)
                'warning': '#F59E0B',      # Orange (same)
                'danger': '#EF4444',       # Red (same)
                'surface': '#FFFFFF',      # White surface
                'text_primary': '#111827', # Dark gray text
                'text_secondary': '#6B7280' # Medium gray text
            }
            
            # Configure window icon and styling
            try:
                # Try to set a modern icon (if available)
                self.root.iconbitmap(default='')
            except Exception as e:
                dashboard_logger.log_debug("No icon file found, using default", {'error': str(e)})
                
            # Center the window (after a brief delay to ensure proper sizing)
            self.root.after(100, self.center_window)
            
            # Initialize database connection immediately (no threading for now)
            self.db_manager = None
            self.data_service = None
            self.is_connected = False
            
            # Initialize pages storage
            self.pages = {}
            self.current_page = None
            
            # Create modern frame structure
            self.create_main_structure()
            
            # Initialize database connection synchronously
            self.initialize_database_sync()
            
            # Create pages after database initialization
            self.create_pages()
            
            # Show default page
            self.show_page("data")
            
            # Handle window close event
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            log_info("Application initialization completed successfully", "APP_INIT")
            
        except Exception as e:
            log_error(e, "APP_INIT_CRITICAL")
            messagebox.showerror("Initialization Error", 
                               f"Failed to initialize application: {str(e)}")
            sys.exit(1)
        
    def center_window(self):
        """Center the window on the screen with improved positioning"""
        # Get the desired window size (1600x1000 as set in geometry)
        window_width = 1600
        window_height = 1000
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position to center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Ensure the window doesn't go off-screen (for smaller displays)
        x = max(0, x)
        y = max(0, y)
        
        # Set the window position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Additional window management for better appearance
        self.root.lift()  # Bring to front
        self.root.attributes('-topmost', True)  # Temporarily make topmost
        self.root.after(100, lambda: self.root.attributes('-topmost', False))  # Remove topmost after brief delay
        
        # Focus the window
        self.root.focus_force()
        
    @log_function_call
    def create_main_structure(self):
        """Create modern application structure with enhanced UI"""
        try:
            log_info("Creating main UI structure", "UI_INIT")
            
            # Create modern header with gradient-like effect
            self.header_frame = ctk.CTkFrame(
                self.root, 
                height=80, 
                corner_radius=0,
                fg_color=self.colors['surface']
            )
            self.header_frame.pack(fill="x", padx=0, pady=0)
            self.header_frame.pack_propagate(False)
            
            # App title with modern typography
            title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
            title_frame.pack(side="left", fill="y", padx=30, pady=10)
            
            app_title = ctk.CTkLabel(
                title_frame,
                text="🏢 Business Dashboard",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=self.colors['text_primary']
            )
            app_title.pack(side="top", pady=(5, 0))
            
            subtitle = ctk.CTkLabel(
                title_frame,
                text="Enterprise Management System",
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_secondary']
            )
            subtitle.pack(side="top")
            
            # Container for status and storage indicators
            indicators_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
            indicators_container.pack(side="right", padx=30, pady=15)
            
            # Storage usage indicator
            self.storage_frame = ctk.CTkFrame(
                indicators_container,
                corner_radius=20,
                fg_color=self.colors['secondary']
            )
            self.storage_frame.pack(side="left", padx=(0, 15))
            
            # Make storage frame clickable for manual refresh
            self.storage_frame.bind("<Button-1>", lambda e: self.update_storage_indicator())
            
            # Storage progress bar
            self.storage_progress = ctk.CTkProgressBar(
                self.storage_frame,
                width=150,
                height=10,
                corner_radius=5,
                progress_color=self.colors['success']
            )
            self.storage_progress.pack(side="left", padx=(15, 5), pady=15)
            self.storage_progress.set(0)
            
            # Storage label
            self.storage_label = ctk.CTkLabel(
                self.storage_frame,
                text="Storage: 0%",
                font=ctk.CTkFont(size=11),
                text_color=self.colors['text_primary']
            )
            self.storage_label.pack(side="left", padx=(5, 15), pady=15)
            
            # Add tooltip-like behavior
            self.storage_label.bind("<Button-1>", lambda e: self.update_storage_indicator())
            
            # Modern status indicator
            self.status_frame = ctk.CTkFrame(
                indicators_container, 
                corner_radius=20,
                fg_color=self.colors['secondary']
            )
            self.status_frame.pack(side="left")
            
            log_info("Main UI structure created successfully", "UI_INIT")
            
        except Exception as e:
            log_error(e, "UI_INIT")
        
        self.status_indicator = ctk.CTkFrame(
            self.status_frame,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=self.colors['warning']  # Orange for connecting
        )
        self.status_indicator.pack(side="left", padx=(15, 10), pady=15)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Connecting to database...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.status_label.pack(side="left", padx=(0, 15), pady=15)
        
        # Modern navigation with improved styling
        self.nav_frame = ctk.CTkFrame(
            self.root, 
            height=70, 
            corner_radius=0,
            fg_color=self.colors['primary']
        )
        self.nav_frame.pack(fill="x", padx=0, pady=0)
        self.nav_frame.pack_propagate(False)
        
        # Create navigation container
        nav_container = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        nav_container.pack(expand=True, fill="both", padx=30, pady=10)
        
        # Modern navigation buttons with icons
        self.nav_buttons = {}
        nav_items = [
            ("📊 Data Management", "data", self.colors['accent']),
            ("📈 Reports & Analytics", "reports", self.colors['success']),
            ("⚙️ Settings", "settings", self.colors['warning'])
        ]
        
        for i, (text, page_id, color) in enumerate(nav_items):
            btn = ctk.CTkButton(
                nav_container,
                text=text,
                command=lambda p=page_id: self.show_page(p),
                width=250,
                height=45,
                corner_radius=15,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=self.darken_color(color),
                text_color="white"
            )
            btn.pack(side="left", padx=15, pady=5)
            self.nav_buttons[page_id] = btn
        
        # Theme toggle button
        theme_btn = ctk.CTkButton(
            nav_container,
            text="🌙 Dark",
            command=self.toggle_theme,
            width=100,
            height=45,
            corner_radius=15,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['secondary'],
            hover_color=self.darken_color(self.colors['secondary'])
        )
        theme_btn.pack(side="right", padx=15, pady=5)
        self.theme_btn = theme_btn
        
        # Create modern content frame with subtle shadow effect
        self.content_frame = ctk.CTkFrame(
            self.root, 
            corner_radius=0,
            fg_color=("gray95", "gray10")  # Light/dark mode adaptive
        )
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
    @log_function_call
    def initialize_database_sync(self):
        """Initialize database connection synchronously"""
        start_time = time.time()
        try:
            log_info("Initializing database connection...", "DB_INIT")
            dashboard_logger.log_user_activity("DATABASE_INIT_START", {"method": "synchronous"})
            
            self.db_manager = get_db_manager()
            
            if self.db_manager.connect():
                self.data_service = HRDataService(self.db_manager)
                self.is_connected = True
                self.update_connection_status(True, "Connected to MongoDB Atlas")
                
                duration = (time.time() - start_time) * 1000
                log_info(f"Database connection established successfully in {duration:.2f}ms", "DB_INIT")
                dashboard_logger.log_performance("database_connection", duration, {"success": True})
                dashboard_logger.log_user_activity("DATABASE_CONNECTED", {"duration_ms": duration})
                
            else:
                self.update_connection_status(False, "Failed to connect to database")
                log_error(Exception("Database connection failed"), "DB_INIT")
                dashboard_logger.log_user_activity("DATABASE_CONNECTION_FAILED", {})
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_msg = f"Database connection error: {str(e)}"
            self.update_connection_status(False, error_msg)
            log_error(e, "DB_INIT")
            dashboard_logger.log_performance("database_connection", duration, {"success": False, "error": str(e)})
            dashboard_logger.log_user_activity("DATABASE_INIT_ERROR", {"error": str(e), "duration_ms": duration})
            
    @log_function_call
    def initialize_database(self):
        """Initialize database connection in a separate thread"""
        def connect_db():
            start_time = time.time()
            try:
                log_info("Initializing database connection (threaded)...", "DB_INIT_THREAD")
                dashboard_logger.log_user_activity("DATABASE_INIT_START", {"method": "threaded"})
                
                self.db_manager = get_db_manager()
                
                if self.db_manager.connect():
                    self.data_service = HRDataService(self.db_manager)
                    self.is_connected = True
                    
                    duration = (time.time() - start_time) * 1000
                    # Update UI in main thread
                    self.root.after(0, self.update_connection_status, True, "Connected to MongoDB Atlas")
                    log_info(f"Database connection established successfully in {duration:.2f}ms", "DB_INIT_THREAD")
                    dashboard_logger.log_performance("database_connection_threaded", duration, {"success": True})
                    dashboard_logger.log_user_activity("DATABASE_CONNECTED", {"duration_ms": duration, "method": "threaded"})
                    
                else:
                    self.root.after(0, self.update_connection_status, False, "Failed to connect to database")
                    log_error(Exception("Database connection failed"), "DB_INIT_THREAD")
                    dashboard_logger.log_user_activity("DATABASE_CONNECTION_FAILED", {"method": "threaded"})
                    
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                error_msg = f"Database connection error: {str(e)}"
                self.root.after(0, self.update_connection_status, False, error_msg)
                log_error(e, "DB_INIT_THREAD")
                dashboard_logger.log_performance("database_connection_threaded", duration, {"success": False, "error": str(e)})
                dashboard_logger.log_user_activity("DATABASE_INIT_ERROR", {"error": str(e), "duration_ms": duration, "method": "threaded"})
        
        # Start connection in background thread
        threading.Thread(target=connect_db, daemon=True).start()
        
    def update_connection_status(self, connected, message):
        """Update the modern connection status in the UI"""
        if connected:
            self.status_label.configure(
                text=f"✅ {message}",
                text_color=self.colors['success']
            )
            self.status_indicator.configure(fg_color=self.colors['success'])
            # Update storage indicator when connected
            self.update_storage_indicator()
        else:
            self.status_label.configure(
                text=f"❌ {message}",
                text_color=self.colors['danger']
            )
            self.status_indicator.configure(fg_color=self.colors['danger'])
            # Show error dialog for connection issues
            messagebox.showerror("Database Connection Error", message)
    
    def update_storage_indicator(self):
        """Update the MongoDB storage usage indicator"""
        try:
            if self.data_service:
                storage_info = self.data_service.get_storage_usage()
                usage_percentage = storage_info.get('usage_percentage', 0)
                total_size_mb = storage_info.get('total_size_mb', 0)
                limit_mb = storage_info.get('limit_mb', 512)
                
                # Update progress bar
                self.storage_progress.set(usage_percentage / 100)
                
                # Update color based on usage
                if usage_percentage > 80:
                    color = self.colors['danger']
                elif usage_percentage > 60:
                    color = self.colors['warning']
                else:
                    color = self.colors['success']
                
                self.storage_progress.configure(progress_color=color)
                
                # Update label
                self.storage_label.configure(
                    text=f"Storage: {usage_percentage}% ({total_size_mb:.1f}MB)"
                )
                
        except Exception as e:
            logger.error(f"Error updating storage indicator: {e}")
            self.storage_label.configure(text="Storage: N/A")
            self.storage_progress.set(0)
            
        # Schedule next update in 30 seconds
        self.root.after(30000, self.update_storage_indicator)
    
    def create_pages(self):
        """Create all application pages"""
        try:
            # Data Management Page
            logger.info("Creating Data Management page...")
            self.pages["data"] = ModernDataPageGUI(self.content_frame, self.data_service)
            logger.info("Data Management page created successfully")
            
            # Reports Page  
            logger.info("Creating Reports page...")
            self.pages["reports"] = ModernReportsPageGUI(self.content_frame, self.data_service)
            logger.info("Reports page created successfully")
            
            # Settings Page
            logger.info("Creating Settings page...")
            self.pages["settings"] = SettingsPageGUI(
                self.content_frame, 
                self.data_service,
                restart_callback=self.restart_application,
                theme_callback=self.change_theme
            )
            logger.info("Settings page created successfully")
            
            logger.info("All GUI pages created successfully")
            
        except Exception as e:
            logger.error(f"Error creating pages: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            messagebox.showerror("Initialization Error", f"Failed to create application pages: {str(e)}")
    
    def darken_color(self, color, factor=0.8):
        """Darken a hex color for hover effects"""
        if color.startswith('#'):
            color = color[1:]
        
        # Convert to RGB
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        # Darken
        darkened = tuple(int(c * factor) for c in rgb)
        # Convert back to hex
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="☀️ Light")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="🌙 Dark")
    
    def show_page(self, page_id):
        """Show the specified page with modern navigation feedback"""
        if self.current_page:
            self.current_page.hide()
        
        if page_id in self.pages:
            self.current_page = self.pages[page_id]
            self.current_page.show()
            
            # Update navigation button states with modern styling
            for btn_id, btn in self.nav_buttons.items():
                if btn_id == page_id:
                    # Active state - make button more prominent
                    btn.configure(
                        fg_color=("gray75", "gray25"),
                        border_width=2,
                        border_color=self.colors['accent']
                    )
                else:
                    # Reset to original colors
                    if btn_id == "data":
                        btn.configure(
                            fg_color=self.colors['accent'],
                            border_width=0
                        )
                    elif btn_id == "reports":
                        btn.configure(
                            fg_color=self.colors['success'],
                            border_width=0
                        )
                    elif btn_id == "settings":
                        btn.configure(
                            fg_color=self.colors['warning'],
                            border_width=0
                        )
        
    def change_theme(self, mode):
        """Change the application theme"""
        ctk.set_appearance_mode(mode)
        
    def restart_application(self):
        """Restart the application"""
        try:
            # Close database connections
            if self.db_manager:
                self.db_manager.disconnect()
            
            # Close current window
            self.root.destroy()
            
            # Restart the application
            python = sys.executable
            os.execl(python, python, *sys.argv)
            
        except Exception as e:
            logger.error(f"Error restarting application: {e}")
            messagebox.showerror("Restart Error", f"Failed to restart application: {str(e)}")
    
    @log_function_call
    def on_closing(self):
        """Handle application closing"""
        try:
            log_info("Application shutdown initiated", "APP_SHUTDOWN")
            dashboard_logger.log_user_activity("APPLICATION_SHUTDOWN_START", {})
            
            # Close database connection
            if self.db_manager:
                self.db_manager.disconnect()
                log_info("Database connection closed", "APP_SHUTDOWN")
                dashboard_logger.log_database_operation("disconnect", "all_collections")
                
            # Log application shutdown
            dashboard_logger.log_app_shutdown()
            dashboard_logger.log_user_activity("APPLICATION_SHUTDOWN_COMPLETE", {})
            
            # Destroy the main window
            self.root.destroy()
            
        except Exception as e:
            log_error(e, "APP_SHUTDOWN")
        finally:
            sys.exit(0)
    
    @log_function_call
    def run(self):
        """Start the application"""
        try:
            log_info("Starting HR Management System main loop...", "APP_RUN")
            dashboard_logger.log_user_activity("APPLICATION_MAIN_LOOP_START", {})
            self.root.mainloop()
        except Exception as e:
            log_error(e, "APP_RUN")
            dashboard_logger.log_user_activity("APPLICATION_MAIN_LOOP_ERROR", {"error": str(e)})
            messagebox.showerror("Application Error", f"An unexpected error occurred: {str(e)}")


def main():
    """Main entry point"""
    try:
        log_info("=== BUSINESS DASHBOARD APPLICATION STARTING ===", "MAIN")
        dashboard_logger.log_user_activity("APPLICATION_START", {
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": os.getcwd()
        })
        
        app = HRManagementApp()
        app.run()
        
    except Exception as e:
        log_error(e, "MAIN_CRITICAL")
        dashboard_logger.log_user_activity("APPLICATION_CRITICAL_ERROR", {"error": str(e)})
        messagebox.showerror("Critical Error", 
                           f"Critical application error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start the HR Management System: {str(e)}")


if __name__ == "__main__":
    main()
