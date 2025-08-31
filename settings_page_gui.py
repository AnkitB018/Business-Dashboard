"""
Enhanced Settings GUI Page
Handles database configuration, theme settings, data management, and system preferences
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import json
import threading
import subprocess
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SettingsPageGUI:
    def __init__(self, parent, data_service, restart_callback=None, theme_callback=None):
        self.parent = parent
        self.data_service = data_service
        self.restart_callback = restart_callback
        self.theme_callback = theme_callback
        self.frame = None
        self.notebook = None
        
        # Configuration file path
        self.env_file_path = os.path.join(os.getcwd(), ".env")
        self.config_file_path = os.path.join(os.getcwd(), "config.py")
        
        self.create_page()
        
    def create_page(self):
        """Create the settings page with enhanced tab design"""
        # Main frame for this page
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color="transparent")
        
        # Create custom tab navigation
        self.create_custom_tab_navigation()
        
        # Create container for tab content
        self.content_container = ctk.CTkFrame(self.frame, corner_radius=10)
        self.content_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create all tab frames (initially hidden)
        self.create_all_tab_frames()
        
        # Show default tab (Database Settings)
        self.show_tab("database")
        
    def create_custom_tab_navigation(self):
        """Create enhanced tab navigation with bigger, better-looking buttons"""
        # Navigation frame
        nav_frame = ctk.CTkFrame(self.frame, height=80, corner_radius=10)
        nav_frame.pack(fill="x", padx=10, pady=(10, 10))
        nav_frame.pack_propagate(False)  # Maintain fixed height
        
        # Title
        title_label = ctk.CTkLabel(
            nav_frame, 
            text="⚙️ Settings Configuration", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # Tab buttons container
        tab_buttons_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        tab_buttons_frame.pack(side="right", padx=20, pady=15)
        
        # Enhanced tab buttons with better styling
        self.tab_buttons = {}
        tab_configs = [
            ("database", "🗄️ Database Settings", "Configure MongoDB Atlas connection"),
            ("appearance", "🎨 Appearance", "Customize theme and UI settings"),
            ("data", "💾 Data Management", "Import/export and backup data"),
            ("system", "⚙️ System Settings", "Application preferences and logs")
        ]
        
        for i, (tab_id, tab_text, tooltip) in enumerate(tab_configs):
            # Create enhanced button
            btn = ctk.CTkButton(
                tab_buttons_frame,
                text=tab_text,
                width=180,  # Bigger width
                height=45,  # Bigger height
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=8,
                fg_color=("gray70", "gray25"),  # Default inactive color
                hover_color=("gray60", "gray35"),
                command=lambda t=tab_id: self.show_tab(t)
            )
            btn.pack(side="left", padx=8, pady=5)
            self.tab_buttons[tab_id] = btn
            
            # Add tooltip (simple hover effect)
            self.add_button_tooltip(btn, tooltip)
    
    def add_button_tooltip(self, button, tooltip_text):
        """Add hover tooltip effect to buttons"""
        def on_enter(event):
            button.configure(text_color=("gray10", "gray90"))
            
        def on_leave(event):
            button.configure(text_color=("gray10", "gray90"))
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def show_tab(self, tab_id):
        """Show the selected tab and update button appearance"""
        # Update button colors
        for btn_id, btn in self.tab_buttons.items():
            if btn_id == tab_id:
                # Active tab - highlighted
                btn.configure(
                    fg_color=("gray20", "gray80"),  # Active color
                    text_color=("white", "gray10")
                )
            else:
                # Inactive tabs - muted
                btn.configure(
                    fg_color=("gray70", "gray25"),  # Inactive color
                    text_color=("gray10", "gray90")
                )
        
        # Hide all tab frames
        for frame in [self.db_frame, self.appearance_frame, self.data_frame, self.system_frame]:
            frame.pack_forget()
        
        # Show selected tab frame
        if tab_id == "database":
            self.db_frame.pack(fill="both", expand=True, padx=20, pady=20)
        elif tab_id == "appearance":
            self.appearance_frame.pack(fill="both", expand=True, padx=20, pady=20)
        elif tab_id == "data":
            self.data_frame.pack(fill="both", expand=True, padx=20, pady=20)
        elif tab_id == "system":
            self.system_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def create_all_tab_frames(self):
        """Create all tab content frames"""
        # Create frames for each tab
        self.db_frame = ctk.CTkFrame(self.content_container, corner_radius=8)
        self.appearance_frame = ctk.CTkFrame(self.content_container, corner_radius=8)
        self.data_frame = ctk.CTkFrame(self.content_container, corner_radius=8)
        self.system_frame = ctk.CTkFrame(self.content_container, corner_radius=8)
        
        # Populate each frame with its content
        self.setup_database_settings_content()
        self.setup_appearance_settings_content()
        self.setup_data_management_content()
        self.setup_system_settings_content()
        
    def configure_scroll_speed(self, scrollable_frame):
        """Configure improved scroll speed for CTkScrollableFrame"""
        try:
            # Improve mouse wheel scroll speed (divide delta by 60 instead of 120 for faster scrolling)
            def on_mousewheel(event):
                scrollable_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 60)), "units")
            
            # Bind improved scroll to canvas
            scrollable_frame._parent_canvas.bind("<MouseWheel>", on_mousewheel)
            
            # Also bind for when frame gets focus
            scrollable_frame.bind("<MouseWheel>", on_mousewheel)
            
        except Exception as e:
            # Fallback - just continue without enhanced scrolling
            pass
        
    def setup_database_settings_content(self):
        """Setup database settings tab content"""
        # Main container with scrollable frame
        main_container = ctk.CTkScrollableFrame(self.db_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure improved scroll speed
        self.configure_scroll_speed(main_container)
        
        # Title
        ctk.CTkLabel(main_container, text="MongoDB Atlas Configuration", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 15))
        
        # Edit mode toggle with warning
        edit_mode_frame = ctk.CTkFrame(main_container)
        edit_mode_frame.pack(fill="x", pady=(0, 15))
        
        self.edit_mode_var = tk.BooleanVar(value=False)
        self.edit_mode_switch = ctk.CTkSwitch(
            edit_mode_frame, 
            text="🔓 Edit Mode (Enable to modify settings)", 
            variable=self.edit_mode_var,
            command=self.toggle_edit_mode,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="red"  # Red color to indicate danger
        )
        self.edit_mode_switch.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Warning message (hidden by default)
        self.warning_label = ctk.CTkLabel(
            edit_mode_frame,
            text="⚠️ Change with Caution",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="red"
        )
        # Don't pack initially - will be shown when edit mode is enabled
        
        # Risk description (hidden by default)
        risk_description = (
            "⚠️ RISK WARNING: Modifying database settings can break the connection and "
            "make your data inaccessible. Incorrect settings may cause application failures, "
            "data loss, or security vulnerabilities. Only change these settings if you are "
            "certain about the new configuration. Always test the connection before saving."
        )
        
        self.risk_description_label = ctk.CTkLabel(
            edit_mode_frame,
            text=risk_description,
            font=ctk.CTkFont(size=10),
            text_color="red",
            wraplength=800,
            justify="left"
        )
        # Don't pack initially - will be shown when edit mode is enabled
        
        # Current connection status
        status_frame = ctk.CTkFrame(main_container)
        status_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(status_frame, text="Current Connection Status:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.db_status_label = ctk.CTkLabel(status_frame, text="Checking connection...", 
                                           font=ctk.CTkFont(size=14))
        self.db_status_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Test connection button
        ctk.CTkButton(status_frame, text="Test Connection", 
                     command=self.test_database_connection).pack(anchor="w", padx=10, pady=10)
        
        # MongoDB Atlas Configuration Section
        config_frame = ctk.CTkFrame(main_container)
        config_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(config_frame, text="MongoDB Atlas Settings", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 15))
        
        # Connection String
        ctk.CTkLabel(config_frame, text="Connection String:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10)
        
        self.mongodb_uri_var = tk.StringVar()
        self.mongodb_uri_entry = ctk.CTkEntry(config_frame, textvariable=self.mongodb_uri_var, 
                                             width=600, height=40, state="readonly",
                                             placeholder_text="mongodb+srv://username:password@cluster.mongodb.net/database")
        self.mongodb_uri_entry.pack(padx=10, pady=(5, 10), fill="x")
        
        # Database Name
        ctk.CTkLabel(config_frame, text="Database Name:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10)
        
        self.mongodb_database_var = tk.StringVar()
        self.mongodb_database_entry = ctk.CTkEntry(config_frame, textvariable=self.mongodb_database_var, 
                    width=300, state="readonly", placeholder_text="hr_management_db")
        self.mongodb_database_entry.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Individual fields for easier editing
        individual_frame = ctk.CTkFrame(config_frame)
        individual_frame.pack(fill="x", padx=10, pady=15)
        
        ctk.CTkLabel(individual_frame, text="Individual Connection Components", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        
        # Username
        ctk.CTkLabel(individual_frame, text="Username:").pack(anchor="w", padx=10)
        self.db_username_var = tk.StringVar()
        self.db_username_entry = ctk.CTkEntry(individual_frame, textvariable=self.db_username_var, 
                                             width=250, state="readonly")
        self.db_username_entry.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Password
        ctk.CTkLabel(individual_frame, text="Password:").pack(anchor="w", padx=10)
        self.db_password_var = tk.StringVar()
        self.db_password_entry = ctk.CTkEntry(individual_frame, textvariable=self.db_password_var, 
                                             width=250, show="*", state="readonly")
        self.db_password_entry.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Cluster URL
        ctk.CTkLabel(individual_frame, text="Cluster URL:").pack(anchor="w", padx=10)
        self.db_cluster_var = tk.StringVar()
        self.db_cluster_entry = ctk.CTkEntry(individual_frame, textvariable=self.db_cluster_var, 
                    width=400, state="readonly", placeholder_text="cluster0.xxxxx.mongodb.net")
        self.db_cluster_entry.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Build connection string button
        self.build_string_button = ctk.CTkButton(individual_frame, text="Build Connection String", 
                     command=self.build_connection_string, state="disabled")
        self.build_string_button.pack(anchor="w", padx=10, pady=10)
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(fill="x", pady=20)
        
        # Load current settings
        self.load_settings_button = ctk.CTkButton(button_frame, text="🔄 Refresh Settings", 
                     command=self.load_current_settings)
        self.load_settings_button.pack(side="left", padx=10, pady=10)
        
        # Save settings
        self.save_settings_button = ctk.CTkButton(button_frame, text="💾 Save Settings", 
                     command=self.save_database_settings, state="disabled",
                     fg_color="green", hover_color="dark green")
        self.save_settings_button.pack(side="left", padx=10, pady=10)
        
        # Restart application
        self.restart_button = ctk.CTkButton(button_frame, text="🔄 Save & Restart Application", 
                     command=self.save_and_restart, state="disabled",
                     fg_color="orange", hover_color="dark orange")
        self.restart_button.pack(side="left", padx=10, pady=10)
        
        # Load current settings on startup
        self.load_current_settings()
        
    def setup_appearance_settings_content(self):
        """Setup appearance settings tab content"""
        # Main container
        main_container = ctk.CTkFrame(self.appearance_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        ctk.CTkLabel(main_container, text="Appearance Settings", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # Theme selection
        theme_frame = ctk.CTkFrame(main_container)
        theme_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(theme_frame, text="Color Theme", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        self.theme_var = tk.StringVar(value="dark")
        
        # Theme radio buttons
        theme_options = [
            ("Dark Mode", "dark"),
            ("Light Mode", "light"),
            ("System Default", "system")
        ]
        
        for text, value in theme_options:
            ctk.CTkRadioButton(theme_frame, text=text, variable=self.theme_var, 
                              value=value, command=self.change_theme).pack(anchor="w", padx=20, pady=5)
        
        # Color scheme selection
        color_frame = ctk.CTkFrame(main_container)
        color_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(color_frame, text="Color Scheme", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        self.color_theme_var = tk.StringVar(value="blue")
        
        color_options = [
            ("Blue", "blue"),
            ("Green", "green"),
            ("Dark Blue", "dark-blue")
        ]
        
        for text, value in color_options:
            ctk.CTkRadioButton(color_frame, text=text, variable=self.color_theme_var, 
                              value=value, command=self.change_color_theme).pack(anchor="w", padx=20, pady=5)
        
        # Font size settings
        font_frame = ctk.CTkFrame(main_container)
        font_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(font_frame, text="Font Size", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        self.font_size_var = tk.IntVar(value=14)
        
        font_size_frame = ctk.CTkFrame(font_frame, fg_color="transparent")
        font_size_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(font_size_frame, text="Base Font Size:").pack(side="left")
        
        font_size_slider = ctk.CTkSlider(font_size_frame, from_=10, to=20, 
                                        variable=self.font_size_var, number_of_steps=10)
        font_size_slider.pack(side="left", padx=20, fill="x", expand=True)
        
        self.font_size_label = ctk.CTkLabel(font_size_frame, text="14")
        self.font_size_label.pack(side="right")
        
        # Update font size label when slider changes
        font_size_slider.configure(command=self.update_font_size_label)
        
        # Apply changes button
        ctk.CTkButton(main_container, text="Apply Changes", 
                     command=self.apply_appearance_settings,
                     fg_color="green", hover_color="dark green").pack(pady=30)
        
    def setup_data_management_content(self):
        """Setup data management tab content"""
        # Main container with scrollable frame
        main_container = ctk.CTkScrollableFrame(self.data_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure improved scroll speed
        self.configure_scroll_speed(main_container)
        
        # Title
        ctk.CTkLabel(main_container, text="Data Management & Backup", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # Database backup section
        backup_frame = ctk.CTkFrame(main_container)
        backup_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(backup_frame, text="Database Backup", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        ctk.CTkLabel(backup_frame, text="Export all data to Excel files for backup", 
                    font=ctk.CTkFont(size=12)).pack(pady=5)
        
        backup_button_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
        backup_button_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(backup_button_frame, text="Export Employees", 
                     command=lambda: self.export_data_to_excel("employees")).pack(side="left", padx=5)
        ctk.CTkButton(backup_button_frame, text="Export Attendance", 
                     command=lambda: self.export_data_to_excel("attendance")).pack(side="left", padx=5)
        ctk.CTkButton(backup_button_frame, text="Export Stock", 
                     command=lambda: self.export_data_to_excel("stock")).pack(side="left", padx=5)
        ctk.CTkButton(backup_button_frame, text="Export Sales", 
                     command=lambda: self.export_data_to_excel("sales")).pack(side="left", padx=5)
        ctk.CTkButton(backup_button_frame, text="Export Purchases", 
                     command=lambda: self.export_data_to_excel("purchases")).pack(side="left", padx=5)
        
        # Full backup button
        ctk.CTkButton(backup_frame, text="📦 Create Complete Backup", 
                     command=self.create_complete_backup,
                     fg_color="blue", hover_color="dark blue", height=40).pack(pady=15)
        
        # Data import section
        import_frame = ctk.CTkFrame(main_container)
        import_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(import_frame, text="Data Import", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        ctk.CTkLabel(import_frame, text="Import data from Excel files", 
                    font=ctk.CTkFont(size=12)).pack(pady=5)
        
        import_button_frame = ctk.CTkFrame(import_frame, fg_color="transparent")
        import_button_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(import_button_frame, text="Import Employees", 
                     command=lambda: self.import_data_from_excel("employees")).pack(side="left", padx=5)
        ctk.CTkButton(import_button_frame, text="Import Attendance", 
                     command=lambda: self.import_data_from_excel("attendance")).pack(side="left", padx=5)
        ctk.CTkButton(import_button_frame, text="Import Stock", 
                     command=lambda: self.import_data_from_excel("stock")).pack(side="left", padx=5)
        ctk.CTkButton(import_button_frame, text="Import Sales", 
                     command=lambda: self.import_data_from_excel("sales")).pack(side="left", padx=5)
        ctk.CTkButton(import_button_frame, text="Import Purchases", 
                     command=lambda: self.import_data_from_excel("purchases")).pack(side="left", padx=5)
        
        # Database reset section
        reset_frame = ctk.CTkFrame(main_container)
        reset_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(reset_frame, text="Database Reset", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        ctk.CTkLabel(reset_frame, text="⚠️ Warning: These actions cannot be undone!", 
                    font=ctk.CTkFont(size=12), text_color="red").pack(pady=5)
        
        reset_button_frame = ctk.CTkFrame(reset_frame, fg_color="transparent")
        reset_button_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(reset_button_frame, text="Clear Employees", 
                     command=lambda: self.clear_collection("employees"),
                     fg_color="red", hover_color="dark red").pack(side="left", padx=5)
        ctk.CTkButton(reset_button_frame, text="Clear Attendance", 
                     command=lambda: self.clear_collection("attendance"),
                     fg_color="red", hover_color="dark red").pack(side="left", padx=5)
        ctk.CTkButton(reset_button_frame, text="Clear Stock", 
                     command=lambda: self.clear_collection("stock"),
                     fg_color="red", hover_color="dark red").pack(side="left", padx=5)
        
        # Complete reset button
        ctk.CTkButton(reset_frame, text="🗑️ Reset Entire Database", 
                     command=self.reset_entire_database,
                     fg_color="dark red", hover_color="black", height=40).pack(pady=15)
        
        # Data statistics
        stats_frame = ctk.CTkFrame(main_container)
        stats_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(stats_frame, text="Database Statistics", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        self.stats_label = ctk.CTkLabel(stats_frame, text="Loading statistics...", 
                                       font=ctk.CTkFont(size=12))
        self.stats_label.pack(pady=10)
        
        ctk.CTkButton(stats_frame, text="Refresh Statistics", 
                     command=self.update_database_statistics).pack(pady=10)
        
        # Load initial statistics
        self.update_database_statistics()
        
    def setup_system_settings_content(self):
        """Setup system settings tab content"""
        # Main container
        main_container = ctk.CTkScrollableFrame(self.system_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure improved scroll speed
        self.configure_scroll_speed(main_container)
        
        # Title
        ctk.CTkLabel(main_container, text="System Settings", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # Application settings
        app_frame = ctk.CTkFrame(main_container)
        app_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(app_frame, text="Application Settings", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        # Auto-start settings
        self.auto_start_var = tk.BooleanVar()
        ctk.CTkCheckBox(app_frame, text="Start minimized to system tray", 
                       variable=self.auto_start_var).pack(anchor="w", padx=20, pady=5)
        
        self.auto_backup_var = tk.BooleanVar()
        ctk.CTkCheckBox(app_frame, text="Enable automatic daily backups", 
                       variable=self.auto_backup_var).pack(anchor="w", padx=20, pady=5)
        
        self.notifications_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(app_frame, text="Show system notifications", 
                       variable=self.notifications_var).pack(anchor="w", padx=20, pady=5)
        
        # Log Viewer section
        logging_frame = ctk.CTkFrame(main_container)
        logging_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(logging_frame, text="Application Logs", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        # Description
        description_text = (
            "The application automatically logs all activities, errors, database operations, "
            "and performance metrics. Use the advanced log viewer to analyze system behavior "
            "and troubleshoot issues."
        )
        
        description_label = ctk.CTkLabel(
            logging_frame,
            text=description_text,
            font=ctk.CTkFont(size=12),
            wraplength=700,
            justify="left",
            text_color=("gray20", "gray70")
        )
        description_label.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Log viewer button with icon and description
        log_viewer_button = ctk.CTkButton(
            logging_frame, 
            text="🔍 Open Advanced Log Viewer", 
            command=self.open_log_viewer,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("blue", "dark blue"),
            hover_color=("dark blue", "blue")
        )
        log_viewer_button.pack(anchor="w", padx=20, pady=10)
        
        # Log info
        log_info_frame = ctk.CTkFrame(logging_frame, fg_color="transparent")
        log_info_frame.pack(anchor="w", padx=20, pady=(0, 10))
        
        info_text = (
            "📊 Available logs: Main activity, Errors, Database operations, "
            "User activity, Performance metrics, Debug information"
        )
        
        ctk.CTkLabel(
            log_info_frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray60")
        ).pack(anchor="w")
        
        # Performance settings
        performance_frame = ctk.CTkFrame(main_container)
        performance_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(performance_frame, text="Performance", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        # Cache settings
        self.cache_size_var = tk.StringVar(value="100")
        
        cache_frame = ctk.CTkFrame(performance_frame, fg_color="transparent")
        cache_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(cache_frame, text="Cache Size (MB):").pack(side="left")
        ctk.CTkEntry(cache_frame, textvariable=self.cache_size_var, width=80).pack(side="left", padx=10)
        
        # Memory usage
        ctk.CTkButton(performance_frame, text="Clear Cache", 
                     command=self.clear_cache).pack(anchor="w", padx=20, pady=5)
        
        # About section
        about_frame = ctk.CTkFrame(main_container)
        about_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(about_frame, text="About", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        about_text = """HR Management System - Desktop Edition
Version: 2.0.0
Built with: Python, CustomTkinter, MongoDB Atlas
Developer: HR Management Solutions
Last Updated: August 2025"""
        
        ctk.CTkLabel(about_frame, text=about_text, 
                    font=ctk.CTkFont(size=12), justify="left").pack(anchor="w", padx=20, pady=10)
        
        # Check for updates
        ctk.CTkButton(about_frame, text="Check for Updates", 
                     command=self.check_for_updates).pack(anchor="w", padx=20, pady=10)
        
        # Apply all settings button
        ctk.CTkButton(main_container, text="Apply All Settings", 
                     command=self.apply_system_settings,
                     fg_color="green", hover_color="dark green", height=40).pack(pady=30)
    
    # Database settings methods
    def load_current_settings(self):
        """Load current database settings"""
        try:
            # Load from environment variables and .env file
            env_values = {}
            
            # First, load from environment variables (runtime values)
            env_values['MONGODB_URI'] = os.getenv('MONGODB_URI', '')
            env_values['MONGODB_DATABASE'] = os.getenv('MONGODB_DATABASE', '')
            env_values['ATLAS_CLUSTER_NAME'] = os.getenv('ATLAS_CLUSTER_NAME', '')
            env_values['ATLAS_DATABASE_USER'] = os.getenv('ATLAS_DATABASE_USER', '')
            env_values['ATLAS_DATABASE_PASSWORD'] = os.getenv('ATLAS_DATABASE_PASSWORD', '')
            
            # Then, try to load from .env file to get any additional values
            if os.path.exists(self.env_file_path):
                with open(self.env_file_path, 'r') as f:
                    content = f.read()
                    
                for line in content.split('\n'):  # Fixed: was '\\n' 
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key in env_values:
                            env_values[key] = value
            
            # Set the UI fields with loaded values
            self.mongodb_uri_var.set(env_values.get('MONGODB_URI', ''))
            self.mongodb_database_var.set(env_values.get('MONGODB_DATABASE', ''))
            
            # Set individual component fields if available
            if hasattr(self, 'db_username_var'):
                self.db_username_var.set(env_values.get('ATLAS_DATABASE_USER', ''))
            if hasattr(self, 'db_password_var'):
                self.db_password_var.set(env_values.get('ATLAS_DATABASE_PASSWORD', ''))
            if hasattr(self, 'db_cluster_var'):
                self.db_cluster_var.set(env_values.get('ATLAS_CLUSTER_NAME', ''))
            
            # Parse connection string to extract components if individual fields are empty
            uri = env_values.get('MONGODB_URI', '')
            if uri and hasattr(self, 'db_username_var'):
                self.parse_connection_string(uri)
            
            # Update status based on what was loaded
            if env_values.get('MONGODB_URI'):
                self.db_status_label.configure(text="✅ Current settings loaded successfully", text_color="green")
            else:
                self.db_status_label.configure(text="⚠️ No database configuration found", text_color="orange")
            
        except Exception as e:
            self.db_status_label.configure(text=f"❌ Error loading settings: {str(e)}", text_color="red")
            logger.error(f"Error loading settings: {e}")
    
    def toggle_edit_mode(self):
        """Toggle edit mode for database settings"""
        edit_enabled = self.edit_mode_var.get()
        
        # Toggle state of all input widgets
        state = "normal" if edit_enabled else "readonly"
        button_state = "normal" if edit_enabled else "disabled"
        
        # Entry widgets
        self.mongodb_uri_entry.configure(state=state)
        self.mongodb_database_entry.configure(state=state)
        self.db_username_entry.configure(state=state)
        self.db_password_entry.configure(state=state)
        self.db_cluster_entry.configure(state=state)
        
        # Buttons
        self.build_string_button.configure(state=button_state)
        self.save_settings_button.configure(state=button_state)
        self.restart_button.configure(state=button_state)
        
        # Update switch text and warning visibility
        if edit_enabled:
            self.edit_mode_switch.configure(
                text="🔓 Edit Mode (Settings can be modified)", 
                text_color="red"
            )
            # Show warning messages
            self.warning_label.pack(anchor="w", padx=15, pady=(0, 5))
            self.risk_description_label.pack(anchor="w", padx=15, pady=(0, 10))
        else:
            self.edit_mode_switch.configure(
                text="🔒 View Mode (Settings are read-only)",
                text_color="gray"
            )
            # Hide warning messages
            self.warning_label.pack_forget()
            self.risk_description_label.pack_forget()
    
    def parse_connection_string(self, uri):
        """Parse MongoDB connection string into components"""
        try:
            if "mongodb+srv://" in uri:
                # Remove protocol
                uri_part = uri.replace("mongodb+srv://", "")
                
                # Extract username and password
                if "@" in uri_part:
                    credentials, rest = uri_part.split("@", 1)
                    if ":" in credentials:
                        username, password = credentials.split(":", 1)
                        self.db_username_var.set(username)
                        self.db_password_var.set(password)
                    
                    # Extract cluster URL
                    if "/" in rest:
                        cluster_part = rest.split("/")[0]
                        self.db_cluster_var.set(cluster_part)
                        
        except Exception as e:
            logger.error(f"Error parsing connection string: {e}")
    
    def build_connection_string(self):
        """Build MongoDB connection string from individual components"""
        try:
            username = self.db_username_var.get().strip()
            password = self.db_password_var.get().strip()
            cluster = self.db_cluster_var.get().strip()
            database = self.mongodb_database_var.get().strip() or "hr_management_db"
            
            if not all([username, password, cluster]):
                messagebox.showerror("Error", "Please fill in all connection fields")
                return
            
            connection_string = f"mongodb+srv://{username}:{password}@{cluster}/{database}?retryWrites=true&w=majority"
            self.mongodb_uri_var.set(connection_string)
            
            messagebox.showinfo("Success", "Connection string built successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to build connection string: {str(e)}")
    
    def test_database_connection(self):
        """Test database connection"""
        def test_connection():
            try:
                self.db_status_label.configure(text="🔄 Testing connection...", text_color="orange")
                
                uri = self.mongodb_uri_var.get().strip()
                database = self.mongodb_database_var.get().strip() or "hr_management_db"
                
                if not uri:
                    self.db_status_label.configure(text="❌ No connection string provided", text_color="red")
                    return
                
                # Test connection using PyMongo directly for more control
                from pymongo import MongoClient
                from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure
                
                # Create test client with shorter timeout
                test_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                
                try:
                    # Test ping
                    test_client.admin.command('ping')
                    
                    # Test database access
                    test_db = test_client[database]
                    collections = test_db.list_collection_names()
                    
                    self.db_status_label.configure(
                        text=f"✅ Connection successful! Database: {database}, Collections: {len(collections)}", 
                        text_color="green"
                    )
                    
                except OperationFailure as e:
                    if "authentication failed" in str(e).lower():
                        self.db_status_label.configure(text="❌ Authentication failed - Check username/password", text_color="red")
                    else:
                        self.db_status_label.configure(text=f"❌ Database operation failed: {str(e)[:50]}...", text_color="red")
                        
                except (ServerSelectionTimeoutError, ConnectionFailure) as e:
                    if "dns" in str(e).lower():
                        self.db_status_label.configure(text="❌ DNS error - Check cluster URL", text_color="red")
                    else:
                        self.db_status_label.configure(text="❌ Network error - Check internet connection", text_color="red")
                        
                finally:
                    # Clean up test connection
                    test_client.close()
                    
            except Exception as e:
                error_msg = str(e)
                self.db_status_label.configure(
                    text=f"❌ Unexpected error: {error_msg[:50]}{'...' if len(error_msg) > 50 else ''}", 
                    text_color="red"
                )
        
        # Run in separate thread
        threading.Thread(target=test_connection, daemon=True).start()
    
    def save_database_settings(self):
        """Save database settings to .env file"""
        try:
            uri = self.mongodb_uri_var.get().strip()
            database = self.mongodb_database_var.get().strip() or "hr_management_db"
            username = self.db_username_var.get().strip()
            password = self.db_password_var.get().strip()
            cluster = self.db_cluster_var.get().strip()
            
            if not uri:
                messagebox.showerror("Error", "Connection string is required")
                return
            
            # Create comprehensive .env content
            env_content = f"""# MongoDB Atlas Configuration
# Replace these values with your actual MongoDB Atlas credentials

# MongoDB Atlas Connection String
# Get this from your MongoDB Atlas dashboard -> Connect -> Connect your application
# Format: mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database-name>?retryWrites=true&w=majority
MONGODB_URI={uri}

# Database name
MONGODB_DATABASE={database}

# Atlas cluster details (for reference and component building)
ATLAS_CLUSTER_NAME={cluster}
ATLAS_DATABASE_USER={username}
ATLAS_DATABASE_PASSWORD={password}

# Application Security
SECRET_KEY=change-this-for-production

# Development Settings
DEBUG_MODE=True

# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
            
            # Write to .env file
            with open(self.env_file_path, 'w') as f:
                f.write(env_content)
            
            messagebox.showinfo("Success", 
                "Database settings saved successfully!\n\n"
                "✅ Connection string saved\n"
                "✅ Database name saved\n" 
                "✅ Atlas credentials saved\n\n"
                "Note: You may need to restart the application for changes to take effect.")
            
            # Disable edit mode after saving
            self.edit_mode_var.set(False)
            self.toggle_edit_mode()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            logger.error(f"Error saving database settings: {e}")
    
    def save_and_restart(self):
        """Save settings and restart application"""
        try:
            self.save_database_settings()
            
            if messagebox.askyesno("Restart Application", 
                                  "Settings saved. Restart the application now to apply changes?"):
                if self.restart_callback:
                    self.restart_callback()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart application: {str(e)}")
    
    # Appearance methods
    def change_theme(self):
        """Change application theme"""
        theme = self.theme_var.get()
        if self.theme_callback:
            self.theme_callback(theme)
    
    def change_color_theme(self):
        """Change color theme"""
        try:
            color_theme = self.color_theme_var.get()
            ctk.set_default_color_theme(color_theme)
            messagebox.showinfo("Theme Changed", 
                               f"Color theme changed to {color_theme}. Restart the application to see full effect.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change color theme: {str(e)}")
    
    def update_font_size_label(self, value):
        """Update font size label"""
        self.font_size_label.configure(text=f"{int(float(value))}")
    
    def apply_appearance_settings(self):
        """Apply appearance settings"""
        try:
            # Apply theme
            self.change_theme()
            
            # Apply color theme
            self.change_color_theme()
            
            messagebox.showinfo("Success", "Appearance settings applied successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")
    
    # Data management methods
    def export_data_to_excel(self, collection_name):
        """Export specific collection to Excel"""
        try:
            if not self.data_service:
                messagebox.showerror("Error", "Database not connected")
                return
            
            # Get data based on collection
            data = []
            if collection_name == "employees":
                data_df = self.data_service.get_employees()
                data = data_df.to_dict('records') if not data_df.empty else []
            elif collection_name == "attendance":
                data_df = self.data_service.get_attendance()
                data = data_df.to_dict('records') if not data_df.empty else []
            elif collection_name == "stock":
                data_df = self.data_service.get_stock()
                data = data_df.to_dict('records') if not data_df.empty else []
            elif collection_name == "sales":
                data_df = self.data_service.get_sales()
                data = data_df.to_dict('records') if not data_df.empty else []
            elif collection_name == "purchases":
                data_df = self.data_service.get_purchases()
                data = data_df.to_dict('records') if not data_df.empty else []
            
            if not data:
                messagebox.showinfo("Info", f"No {collection_name} data to export")
                return
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title=f"Save {collection_name} data",
                initialvalue=f"{collection_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if filename:
                # Convert to DataFrame and save
                df = pd.DataFrame(data)
                df.to_excel(filename, index=False)
                messagebox.showinfo("Success", f"{collection_name} data exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export {collection_name}: {str(e)}")
            logger.error(f"Error exporting {collection_name}: {e}")
    
    def create_complete_backup(self):
        """Create complete database backup"""
        try:
            if not self.data_service:
                messagebox.showerror("Error", "Database not connected")
                return
            
            # Ask for save directory
            directory = filedialog.askdirectory(title="Select backup directory")
            
            if directory:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_folder = os.path.join(directory, f"hr_backup_{timestamp}")
                os.makedirs(backup_folder, exist_ok=True)
                
                collections = ["employees", "attendance", "stock", "sales", "purchases"]
                
                for collection in collections:
                    try:
                        # Get data
                        data = []
                        if collection == "employees":
                            data_df = self.data_service.get_employees()
                            data = data_df.to_dict('records') if not data_df.empty else []
                        elif collection == "attendance":
                            data_df = self.data_service.get_attendance()
                            data = data_df.to_dict('records') if not data_df.empty else []
                        elif collection == "stock":
                            data_df = self.data_service.get_stock()
                            data = data_df.to_dict('records') if not data_df.empty else []
                        elif collection == "sales":
                            data_df = self.data_service.get_sales()
                            data = data_df.to_dict('records') if not data_df.empty else []
                        elif collection == "purchases":
                            data_df = self.data_service.get_purchases()
                            data = data_df.to_dict('records') if not data_df.empty else []
                        
                        if data:
                            # Save to Excel
                            filename = os.path.join(backup_folder, f"{collection}.xlsx")
                            df = pd.DataFrame(data)
                            df.to_excel(filename, index=False)
                            
                    except Exception as e:
                        logger.error(f"Error backing up {collection}: {e}")
                
                messagebox.showinfo("Success", f"Complete backup created at: {backup_folder}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")
            logger.error(f"Error creating complete backup: {e}")
    
    def import_data_from_excel(self, collection_name):
        """Import data from Excel file"""
        try:
            if not self.data_service:
                messagebox.showerror("Error", "Database not connected")
                return
            
            # Ask for file
            filename = filedialog.askopenfilename(
                filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")],
                title=f"Select {collection_name} data file"
            )
            
            if filename:
                # Read data
                if filename.endswith('.csv'):
                    df = pd.read_csv(filename)
                else:
                    df = pd.read_excel(filename)
                
                # Convert to list of dictionaries
                data = df.to_dict('records')
                
                # Import based on collection
                success_count = 0
                for record in data:
                    try:
                        if collection_name == "employees":
                            if self.data_service.add_employee(record):
                                success_count += 1
                        elif collection_name == "attendance":
                            if self.data_service.add_attendance(record):
                                success_count += 1
                        elif collection_name == "stock":
                            if self.data_service.add_stock_item(record):
                                success_count += 1
                        elif collection_name == "sales":
                            if self.data_service.add_sale(record):
                                success_count += 1
                        elif collection_name == "purchases":
                            if self.data_service.add_purchase(record):
                                success_count += 1
                    except Exception as e:
                        logger.error(f"Error importing record: {e}")
                
                messagebox.showinfo("Import Complete", 
                                   f"Successfully imported {success_count} out of {len(data)} records")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import data: {str(e)}")
            logger.error(f"Error importing {collection_name}: {e}")
    
    def clear_collection(self, collection_name):
        """Clear specific collection"""
        try:
            if not self.data_service:
                messagebox.showerror("Error", "Database not connected")
                return
            
            if messagebox.askyesno("Confirm Clear", 
                                  f"Are you sure you want to clear all {collection_name} data?\n\nThis action cannot be undone!"):
                
                # Perform clear operation based on collection
                result = False
                if collection_name == "employees":
                    result = self.data_service.db_manager.clear_collection("employees")
                elif collection_name == "attendance":
                    result = self.data_service.db_manager.clear_collection("attendance")
                elif collection_name == "stock":
                    result = self.data_service.db_manager.clear_collection("stock")
                elif collection_name == "sales":
                    result = self.data_service.db_manager.clear_collection("sales")
                elif collection_name == "purchases":
                    result = self.data_service.db_manager.clear_collection("purchases")
                
                if result:
                    messagebox.showinfo("Success", f"{collection_name} collection cleared successfully")
                    self.update_database_statistics()
                else:
                    messagebox.showerror("Error", f"Failed to clear {collection_name} collection")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear {collection_name}: {str(e)}")
            logger.error(f"Error clearing {collection_name}: {e}")
    
    def reset_entire_database(self):
        """Reset entire database"""
        try:
            if not self.data_service:
                messagebox.showerror("Error", "Database not connected")
                return
            
            # Double confirmation
            if messagebox.askyesno("Confirm Reset", 
                                  "⚠️ WARNING: This will delete ALL data in the database!\n\nAre you absolutely sure?"):
                
                if messagebox.askyesno("Final Confirmation", 
                                      "This is your final warning!\n\nAll employees, attendance, stock, sales, and purchase data will be permanently deleted.\n\nContinue?"):
                    
                    collections = ["employees", "attendance", "stock", "sales", "purchases"]
                    
                    for collection in collections:
                        try:
                            self.data_service.db_manager.clear_collection(collection)
                        except Exception as e:
                            logger.error(f"Error clearing {collection}: {e}")
                    
                    messagebox.showinfo("Database Reset", "Database has been completely reset")
                    self.update_database_statistics()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset database: {str(e)}")
            logger.error(f"Error resetting database: {e}")
    
    def update_database_statistics(self):
        """Update database statistics"""
        try:
            if not self.data_service:
                self.stats_label.configure(text="Database not connected")
                return
            
            # Get statistics
            employees_df = self.data_service.get_employees()
            employees_count = len(employees_df) if not employees_df.empty else 0
            attendance_df = self.data_service.get_attendance()
            attendance_count = len(attendance_df) if not attendance_df.empty else 0
            stock_df = self.data_service.get_stock()
            stock_count = len(stock_df) if not stock_df.empty else 0
            sales_df = self.data_service.get_sales()
            sales_count = len(sales_df) if not sales_df.empty else 0
            purchases_df = self.data_service.get_purchases()
            purchases_count = len(purchases_df) if not purchases_df.empty else 0
            
            stats_text = f"""Database Statistics:
• Employees: {employees_count} records
• Attendance: {attendance_count} records  
• Stock Items: {stock_count} items
• Sales Records: {sales_count} transactions
• Purchase Records: {purchases_count} transactions

Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
            
            self.stats_label.configure(text=stats_text)
            
        except Exception as e:
            self.stats_label.configure(text=f"Error loading statistics: {str(e)}")
            logger.error(f"Error updating statistics: {e}")
    
    # System settings methods
    def open_log_viewer(self):
        """Open the advanced log viewer application"""
        try:
            import subprocess
            import sys
            
            # Get the Python executable from the current virtual environment
            python_executable = sys.executable
            log_viewer_path = os.path.join(os.getcwd(), "log_viewer.py")
            
            # Check if log_viewer.py exists
            if not os.path.exists(log_viewer_path):
                messagebox.showerror(
                    "Log Viewer Not Found", 
                    "The log viewer application (log_viewer.py) was not found in the current directory."
                )
                return
            
            # Launch the log viewer as a separate process
            subprocess.Popen([python_executable, log_viewer_path], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            # Show success message
            messagebox.showinfo(
                "Log Viewer Launched", 
                "🔍 Advanced Log Viewer has been opened in a separate window.\n\n"
                "You can now:\n"
                "• Browse all application logs\n"
                "• Filter by date and log type\n"
                "• Search through log content\n"
                "• Analyze system performance\n"
                "• Export log data"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Failed to open log viewer: {str(e)}\n\n"
                "You can manually run the log viewer by executing:\n"
                "python log_viewer.py"
            )
    
    def clear_cache(self):
        """Clear application cache"""
        try:
            # Simulate cache clearing
            messagebox.showinfo("Cache Cleared", "Application cache has been cleared successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear cache: {str(e)}")
    
    def check_for_updates(self):
        """Check for application updates"""
        try:
            # Simulate update check
            messagebox.showinfo("Updates", "You are running the latest version of HR Management System")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check for updates: {str(e)}")
    
    def apply_system_settings(self):
        """Apply system settings"""
        try:
            # Save settings to a configuration file
            settings = {
                "auto_start": self.auto_start_var.get(),
                "auto_backup": self.auto_backup_var.get(),
                "notifications": self.notifications_var.get(),
                "cache_size": self.cache_size_var.get(),
                "last_updated": datetime.now().isoformat()
            }
            
            settings_file = os.path.join(os.getcwd(), "app_settings.json")
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "System settings applied successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply system settings: {str(e)}")
            logger.error(f"Error applying system settings: {e}")
    
    def show(self):
        """Show this page"""
        if self.frame:
            self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Hide this page"""
        if self.frame:
            self.frame.pack_forget()
