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
        # Set modern appearance with improved theme
        ctk.set_appearance_mode("dark")  # Modern dark mode
        ctk.set_default_color_theme("blue")
        
        # Create main window with modern styling
        self.root = ctk.CTk()
        self.root.title("🏢 Business Dashboard - Enterprise Edition")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 900)
        
        # Modern color scheme
        self.colors = {
            'primary': '#1F2937',      # Dark gray
            'secondary': '#374151',    # Medium gray
            'accent': '#3B82F6',       # Blue
            'success': '#10B981',      # Green
            'warning': '#F59E0B',      # Orange
            'danger': '#EF4444',       # Red
            'surface': '#111827',      # Very dark gray
            'text_primary': '#F9FAFB', # Light gray
            'text_secondary': '#9CA3AF' # Medium light gray
        }
        
        # Configure window icon and styling
        try:
            # Try to set a modern icon (if available)
            self.root.iconbitmap(default='')
        except:
            pass
            
        # Center the window
        self.center_window()
        
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
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_main_structure(self):
        """Create modern application structure with enhanced UI"""
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
        
        # Modern status indicator
        self.status_frame = ctk.CTkFrame(
            self.header_frame, 
            corner_radius=20,
            fg_color=self.colors['secondary']
        )
        self.status_frame.pack(side="right", padx=30, pady=15)
        
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
        """Update the modern connection status in the UI"""
        if connected:
            self.status_label.configure(
                text=f"✅ {message}",
                text_color=self.colors['success']
            )
            self.status_indicator.configure(fg_color=self.colors['success'])
        else:
            self.status_label.configure(
                text=f"❌ {message}",
                text_color=self.colors['danger']
            )
            self.status_indicator.configure(fg_color=self.colors['danger'])
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
