"""
Database Configuration Setup
Allows users to configure their own MongoDB connection
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import json
from pathlib import Path
import pymongo
from urllib.parse import quote_plus

class DatabaseConfigWindow:
    def __init__(self):
        self.window = None
        self.config_file = Path.home() / "BusinessDashboard" / "config.json"
        self.config_file.parent.mkdir(exist_ok=True)
        
    def show_setup_wizard(self):
        """Show the database configuration wizard"""
        self.window = ctk.CTk()
        self.window.title("Business Dashboard - Database Setup")
        self.window.geometry("600x700")
        self.window.resizable(False, False)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Center the window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.create_setup_interface()
        self.window.mainloop()
        
    def create_setup_interface(self):
        """Create the setup interface"""
        # Main frame
        main_frame = ctk.CTkScrollableFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🗄️ Database Configuration",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Configure your MongoDB database connection for Business Dashboard",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        desc_label.pack(pady=(0, 30))
        
        # Connection type selection
        type_frame = ctk.CTkFrame(main_frame)
        type_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            type_frame,
            text="Connection Type:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        self.connection_type = ctk.StringVar(value="atlas")
        
        atlas_radio = ctk.CTkRadioButton(
            type_frame,
            text="MongoDB Atlas (Cloud)",
            variable=self.connection_type,
            value="atlas",
            command=self.on_connection_type_change
        )
        atlas_radio.pack(anchor="w", padx=40, pady=5)
        
        local_radio = ctk.CTkRadioButton(
            type_frame,
            text="Local MongoDB Server",
            variable=self.connection_type,
            value="local",
            command=self.on_connection_type_change
        )
        local_radio.pack(anchor="w", padx=40, pady=(5, 20))
        
        # Atlas configuration frame
        self.atlas_frame = ctk.CTkFrame(main_frame)
        self.atlas_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            self.atlas_frame,
            text="MongoDB Atlas Configuration:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Atlas fields
        self.atlas_username = self.create_field(self.atlas_frame, "Username:", "your_username")
        self.atlas_password = self.create_field(self.atlas_frame, "Password:", "", show="*")
        self.atlas_cluster = self.create_field(self.atlas_frame, "Cluster URL:", "cluster0.xxxxx.mongodb.net")
        self.atlas_database = self.create_field(self.atlas_frame, "Database Name:", "BusinessDashboard")
        
        # Local configuration frame
        self.local_frame = ctk.CTkFrame(main_frame)
        self.local_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            self.local_frame,
            text="Local MongoDB Configuration:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Local fields
        self.local_host = self.create_field(self.local_frame, "Host:", "localhost")
        self.local_port = self.create_field(self.local_frame, "Port:", "27017")
        self.local_username = self.create_field(self.local_frame, "Username (optional):", "")
        self.local_password = self.create_field(self.local_frame, "Password (optional):", "", show="*")
        self.local_database = self.create_field(self.local_frame, "Database Name:", "BusinessDashboard")
        
        # Hide local frame initially
        self.local_frame.pack_forget()
        
        # Test connection button
        self.test_button = ctk.CTkButton(
            main_frame,
            text="🔍 Test Connection",
            command=self.test_connection,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.test_button.pack(pady=20)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=20)
        
        save_button = ctk.CTkButton(
            buttons_frame,
            text="💾 Save & Continue",
            command=self.save_configuration,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#059669",
            hover_color="#047857"
        )
        save_button.pack(side="right", padx=(10, 20), pady=20)
        
        skip_button = ctk.CTkButton(
            buttons_frame,
            text="⏭️ Skip (Use Demo Mode)",
            command=self.skip_configuration,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        skip_button.pack(side="right", padx=20, pady=20)
        
    def create_field(self, parent, label_text, placeholder, show=None):
        """Create a labeled input field"""
        field_frame = ctk.CTkFrame(parent)
        field_frame.pack(fill="x", padx=20, pady=5)
        
        label = ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120
        )
        label.pack(side="left", padx=(20, 10), pady=15)
        
        entry = ctk.CTkEntry(
            field_frame,
            placeholder_text=placeholder,
            show=show,
            height=35
        )
        entry.pack(side="right", fill="x", expand=True, padx=(10, 20), pady=15)
        
        return entry
    
    def on_connection_type_change(self):
        """Handle connection type change"""
        if self.connection_type.get() == "atlas":
            self.atlas_frame.pack(fill="x", pady=(0, 20), before=self.local_frame)
            self.local_frame.pack_forget()
        else:
            self.local_frame.pack(fill="x", pady=(0, 20), before=self.test_button)
            self.atlas_frame.pack_forget()
    
    def test_connection(self):
        """Test the database connection"""
        try:
            self.status_label.configure(text="🔄 Testing connection...", text_color="orange")
            self.window.update()
            
            connection_string = self.build_connection_string()
            
            # Test connection
            client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            
            self.status_label.configure(text="✅ Connection successful!", text_color="green")
            
        except Exception as e:
            self.status_label.configure(text=f"❌ Connection failed: {str(e)}", text_color="red")
    
    def build_connection_string(self):
        """Build MongoDB connection string"""
        if self.connection_type.get() == "atlas":
            username = quote_plus(self.atlas_username.get())
            password = quote_plus(self.atlas_password.get())
            cluster = self.atlas_cluster.get()
            database = self.atlas_database.get()
            
            if not all([username, password, cluster]):
                raise ValueError("Please fill in all required Atlas fields")
            
            return f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority"
        
        else:
            host = self.local_host.get() or "localhost"
            port = self.local_port.get() or "27017"
            username = self.local_username.get()
            password = self.local_password.get()
            database = self.local_database.get() or "BusinessDashboard"
            
            if username and password:
                auth = f"{quote_plus(username)}:{quote_plus(password)}@"
            else:
                auth = ""
            
            return f"mongodb://{auth}{host}:{port}/{database}"
    
    def save_configuration(self):
        """Save the configuration"""
        try:
            connection_string = self.build_connection_string()
            
            # Test connection first
            client = pymongo.MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            
            # Save configuration
            config = {
                "mongodb_uri": connection_string,
                "database_name": (self.atlas_database.get() if self.connection_type.get() == "atlas" 
                                else self.local_database.get() or "BusinessDashboard"),
                "connection_type": self.connection_type.get(),
                "configured": True
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Success", "Database configuration saved successfully!")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def skip_configuration(self):
        """Skip configuration and use demo mode"""
        config = {
            "mongodb_uri": "demo_mode",
            "database_name": "demo",
            "connection_type": "demo",
            "configured": False
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        messagebox.showinfo("Demo Mode", "Application will run in demo mode with sample data.")
        self.window.destroy()

def check_database_configuration():
    """Check if database is configured"""
    config_file = Path.home() / "BusinessDashboard" / "config.json"
    
    if not config_file.exists():
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('configured', False)
    except:
        return False

def get_database_config():
    """Get database configuration"""
    config_file = Path.home() / "BusinessDashboard" / "config.json"
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except:
        return None

if __name__ == "__main__":
    # Run the database configuration wizard
    config_window = DatabaseConfigWindow()
    config_window.show_setup_wizard()
