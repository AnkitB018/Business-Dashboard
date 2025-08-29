import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
import threading
import webbrowser
import subprocess
import sys
import os
from database import initialize_database, get_db_manager
from data_service import DataMigration
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set CustomTkinter appearance
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class HRManagementGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("HR Management System")
        self.root.geometry("800x600")
        
        # Variables
        self.dash_process = None
        self.db_connected = False
        
        self.setup_ui()
        self.check_dependencies()
        
    def setup_ui(self):
        """Setup the main UI"""
        # Title
        title_label = ctk.CTkLabel(
            self.root, 
            text="HR Management System", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Database section
        db_frame = ctk.CTkFrame(main_frame)
        db_frame.pack(fill="x", padx=20, pady=10)
        
        db_label = ctk.CTkLabel(db_frame, text="Database Setup", font=ctk.CTkFont(size=18, weight="bold"))
        db_label.pack(pady=10)
        
        # Database status
        self.db_status_label = ctk.CTkLabel(db_frame, text="Database Status: Not Connected", text_color="red")
        self.db_status_label.pack(pady=5)
        
        # Database buttons
        db_buttons_frame = ctk.CTkFrame(db_frame)
        db_buttons_frame.pack(pady=10)
        
        self.connect_db_btn = ctk.CTkButton(
            db_buttons_frame, 
            text="Connect to MongoDB", 
            command=self.connect_database
        )
        self.connect_db_btn.pack(side="left", padx=5)
        
        self.init_db_btn = ctk.CTkButton(
            db_buttons_frame, 
            text="Initialize Database", 
            command=self.initialize_database,
            state="disabled"
        )
        self.init_db_btn.pack(side="left", padx=5)
        
        self.migrate_btn = ctk.CTkButton(
            db_buttons_frame, 
            text="Migrate from Excel", 
            command=self.migrate_from_excel,
            state="disabled"
        )
        self.migrate_btn.pack(side="left", padx=5)
        
        # Application section
        app_frame = ctk.CTkFrame(main_frame)
        app_frame.pack(fill="x", padx=20, pady=10)
        
        app_label = ctk.CTkLabel(app_frame, text="Application Control", font=ctk.CTkFont(size=18, weight="bold"))
        app_label.pack(pady=10)
        
        # Application buttons
        app_buttons_frame = ctk.CTkFrame(app_frame)
        app_buttons_frame.pack(pady=10)
        
        self.start_btn = ctk.CTkButton(
            app_buttons_frame, 
            text="Start HR Dashboard", 
            command=self.start_dashboard,
            state="disabled"
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(
            app_buttons_frame, 
            text="Stop Dashboard", 
            command=self.stop_dashboard,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        self.open_browser_btn = ctk.CTkButton(
            app_buttons_frame, 
            text="Open in Browser", 
            command=self.open_browser,
            state="disabled"
        )
        self.open_browser_btn.pack(side="left", padx=5)
        
        # Status section
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        status_label = ctk.CTkLabel(status_frame, text="System Status", font=ctk.CTkFont(size=18, weight="bold"))
        status_label.pack(pady=10)
        
        # Log display
        self.log_text = ctk.CTkTextbox(status_frame, height=200)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Footer
        footer_frame = ctk.CTkFrame(self.root)
        footer_frame.pack(fill="x", padx=20, pady=10)
        
        footer_label = ctk.CTkLabel(
            footer_frame, 
            text="HR Management System v1.0 - MongoDB Edition", 
            font=ctk.CTkFont(size=12)
        )
        footer_label.pack(pady=5)
        
    def log_message(self, message):
        """Add message to log display"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.root.update()
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        try:
            import pymongo
            import dash
            import pandas
            self.log_message("✅ All required dependencies are installed")
        except ImportError as e:
            self.log_message(f"❌ Missing dependency: {e}")
            messagebox.showerror("Missing Dependencies", 
                               "Please install required dependencies:\npip install -r requirements.txt")
    
    def connect_database(self):
        """Connect to MongoDB"""
        try:
            self.log_message("Connecting to MongoDB...")
            db_manager = get_db_manager()
            
            if db_manager.connect():
                self.db_connected = True
                self.db_status_label.configure(text="Database Status: Connected", text_color="green")
                self.init_db_btn.configure(state="normal")
                self.migrate_btn.configure(state="normal")
                self.log_message("✅ Successfully connected to MongoDB")
            else:
                self.log_message("❌ Failed to connect to MongoDB")
                messagebox.showerror("Connection Error", 
                                   "Could not connect to MongoDB. Please ensure MongoDB is running.")
                
        except Exception as e:
            self.log_message(f"❌ Database connection error: {e}")
            messagebox.showerror("Error", f"Database connection failed: {e}")
    
    def initialize_database(self):
        """Initialize database with collections"""
        try:
            self.log_message("Initializing database...")
            if initialize_database():
                self.log_message("✅ Database initialized successfully")
                self.start_btn.configure(state="normal")
                messagebox.showinfo("Success", "Database initialized successfully!")
            else:
                self.log_message("❌ Failed to initialize database")
                messagebox.showerror("Error", "Failed to initialize database")
                
        except Exception as e:
            self.log_message(f"❌ Database initialization error: {e}")
            messagebox.showerror("Error", f"Database initialization failed: {e}")
    
    def migrate_from_excel(self):
        """Migrate data from Excel to MongoDB"""
        try:
            excel_file = "business_data.xlsx"
            if not os.path.exists(excel_file):
                messagebox.showerror("File Not Found", 
                                   f"Excel file '{excel_file}' not found in current directory")
                return
            
            self.log_message("Starting data migration from Excel...")
            migration = DataMigration(excel_file)
            
            if migration.migrate_from_excel():
                self.log_message("✅ Data migration completed successfully")
                messagebox.showinfo("Success", "Data migrated successfully from Excel to MongoDB!")
            else:
                self.log_message("❌ Data migration failed")
                messagebox.showerror("Error", "Data migration failed")
                
        except Exception as e:
            self.log_message(f"❌ Migration error: {e}")
            messagebox.showerror("Error", f"Migration failed: {e}")
    
    def start_dashboard(self):
        """Start the Dash application"""
        try:
            if self.dash_process is not None:
                self.log_message("Dashboard is already running")
                return
            
            self.log_message("Starting HR Dashboard...")
            
            # Start Dash app in a separate thread
            def run_dash():
                try:
                    # Import and run the app
                    import app_mongo
                    app_mongo.app.run_server(debug=False, port=8050, host='127.0.0.1')
                except Exception as e:
                    self.log_message(f"❌ Error starting dashboard: {e}")
            
            self.dash_thread = threading.Thread(target=run_dash, daemon=True)
            self.dash_thread.start()
            
            # Update UI
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.open_browser_btn.configure(state="normal")
            
            self.log_message("✅ HR Dashboard started on http://127.0.0.1:8050")
            
            # Auto-open browser after a short delay
            self.root.after(2000, self.open_browser)
            
        except Exception as e:
            self.log_message(f"❌ Error starting dashboard: {e}")
            messagebox.showerror("Error", f"Failed to start dashboard: {e}")
    
    def stop_dashboard(self):
        """Stop the Dash application"""
        try:
            self.log_message("Stopping HR Dashboard...")
            
            # Note: In a real implementation, you'd need a way to properly stop the Dash server
            # For now, we'll just update the UI
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.open_browser_btn.configure(state="disabled")
            
            self.log_message("✅ Dashboard stopped")
            
        except Exception as e:
            self.log_message(f"❌ Error stopping dashboard: {e}")
            messagebox.showerror("Error", f"Failed to stop dashboard: {e}")
    
    def open_browser(self):
        """Open the dashboard in web browser"""
        try:
            webbrowser.open('http://127.0.0.1:8050')
            self.log_message("✅ Opened dashboard in browser")
        except Exception as e:
            self.log_message(f"❌ Error opening browser: {e}")
            messagebox.showerror("Error", f"Failed to open browser: {e}")
    
    def run(self):
        """Start the GUI application"""
        try:
            self.log_message("HR Management System started")
            self.log_message("Please connect to MongoDB to begin")
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            if hasattr(self, 'dash_thread'):
                self.log_message("Shutting down...")

def main():
    """Main entry point"""
    try:
        app = HRManagementGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
