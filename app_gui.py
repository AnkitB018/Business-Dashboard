"""
HR Management System - Desktop GUI Application
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
import logging

# Import GUI pages
from data_page_gui import ModernDataPageGUI
from reports_page_gui import ModernReportsPageGUI
from settings_page_gui import SettingsPageGUI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HRManagementApp:
    def __init__(self):
        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")  # Default to dark mode
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("HR Management System - Desktop Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Center the window
        self.center_window()
        
        # Initialize database connection immediately (no threading for now)
        self.db_manager = None
        self.data_service = None
        self.is_connected = False
        
        # Initialize pages storage
        self.pages = {}
        self.current_page = None
        
        # Create main frame structure
        self.create_main_structure()
        
        # Initialize database connection synchronously
        self.initialize_database_sync()
        
        # Create pages after database initialization
        self.create_pages()
        
        # Show default page
        self.show_page("data")
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_main_structure(self):
        """Create the main application structure"""
        # Create header frame
        self.header_frame = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="HR Management System",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=20)
        
        # Connection status
        self.status_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.status_frame.pack(side="right", padx=20, pady=20)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Connecting to database...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack()
        
        # Create navigation frame
        self.nav_frame = ctk.CTkFrame(self.root, height=60, corner_radius=0)
        self.nav_frame.pack(fill="x", padx=0, pady=0)
        self.nav_frame.pack_propagate(False)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Data Management", "data"),
            ("Reports & Analytics", "reports"),
            ("Settings", "settings")
        ]
        
        for i, (text, page_id) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.nav_frame,
                text=text,
                command=lambda p=page_id: self.show_page(p),
                width=200,
                height=40,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            btn.pack(side="left", padx=10, pady=10)
            self.nav_buttons[page_id] = btn
        
        # Create main content frame
        self.content_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
    def initialize_database_sync(self):
        """Initialize database connection synchronously"""
        try:
            logger.info("Initializing database connection...")
            self.db_manager = get_db_manager()
            
            if self.db_manager.connect():
                self.data_service = HRDataService(self.db_manager)
                self.is_connected = True
                self.update_connection_status(True, "Connected to MongoDB Atlas")
                logger.info("Database connection established successfully")
            else:
                self.update_connection_status(False, "Failed to connect to database")
                logger.error("Failed to establish database connection")
                
        except Exception as e:
            error_msg = f"Database connection error: {str(e)}"
            self.update_connection_status(False, error_msg)
            logger.error(f"Database initialization error: {e}")
            
    def initialize_database(self):
        """Initialize database connection in a separate thread"""
        def connect_db():
            try:
                logger.info("Initializing database connection...")
                self.db_manager = get_db_manager()
                
                if self.db_manager.connect():
                    self.data_service = HRDataService(self.db_manager)
                    self.is_connected = True
                    
                    # Update UI in main thread
                    self.root.after(0, self.update_connection_status, True, "Connected to MongoDB Atlas")
                    logger.info("Database connection established successfully")
                else:
                    self.root.after(0, self.update_connection_status, False, "Failed to connect to database")
                    logger.error("Failed to establish database connection")
                    
            except Exception as e:
                error_msg = f"Database connection error: {str(e)}"
                self.root.after(0, self.update_connection_status, False, error_msg)
                logger.error(f"Database initialization error: {e}")
        
        # Start connection in background thread
        threading.Thread(target=connect_db, daemon=True).start()
        
    def update_connection_status(self, connected, message):
        """Update the connection status in the UI"""
        if connected:
            self.status_label.configure(
                text=f"✅ {message}",
                text_color="green"
            )
        else:
            self.status_label.configure(
                text=f"❌ {message}",
                text_color="red"
            )
            # Show error dialog for connection issues
            messagebox.showerror("Database Connection Error", message)
    
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
    
    def show_page(self, page_id):
        """Show the specified page"""
        if self.current_page:
            self.current_page.hide()
        
        if page_id in self.pages:
            self.current_page = self.pages[page_id]
            self.current_page.show()
            
            # Update navigation button states
            for btn_id, btn in self.nav_buttons.items():
                if btn_id == page_id:
                    btn.configure(fg_color=("gray75", "gray25"))
                else:
                    btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])
        
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
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Close database connection
            if self.db_manager:
                self.db_manager.disconnect()
                logger.info("Database connection closed")
                
            # Destroy the main window
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
        finally:
            sys.exit(0)
    
    def run(self):
        """Start the application"""
        logger.info("Starting HR Management System...")
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", f"An unexpected error occurred: {str(e)}")


def main():
    """Main entry point"""
    try:
        app = HRManagementApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start the HR Management System: {str(e)}")


if __name__ == "__main__":
    main()
