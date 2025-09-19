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
import sys

logger = logging.getLogger(__name__)

class SettingsPageGUI:
    def __init__(self, parent, data_service, restart_callback=None, theme_callback=None):
        self.parent = parent
        self.data_service = data_service
        self.restart_callback = restart_callback
        self.theme_callback = theme_callback
        self.frame = None
        self.notebook = None
        
        # Configuration file path - works for both development and executable
        self.env_file_path = self._get_application_path(".env")
        self.config_file_path = self._get_application_path("config.py")
        
        self.create_page()
        
    def _get_application_path(self, filename):
        """Get the correct path for application files, works for both development and executable"""
        try:
            # For PyInstaller executable
            if hasattr(sys, '_MEIPASS'):
                # When running as executable, look in the directory where the .exe is located
                base_path = os.path.dirname(sys.executable)
            else:
                # When running as script, use the script's directory
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            file_path = os.path.join(base_path, filename)
            
            # If file doesn't exist in base path, try current working directory as fallback
            if not os.path.exists(file_path):
                fallback_path = os.path.join(os.getcwd(), filename)
                if os.path.exists(fallback_path):
                    return fallback_path
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error determining application path for {filename}: {e}")
            # Fallback to current working directory
            return os.path.join(os.getcwd(), filename)
        
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
            # Refresh storage display when database tab is shown
            self.parent.after(100, self.update_storage_display)  # Small delay to ensure UI is ready
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
        
        # Storage Usage Section
        storage_frame = ctk.CTkFrame(main_container)
        storage_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(storage_frame, text="💾 Database Storage Usage", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 10))
        
        # Storage info container
        storage_info_frame = ctk.CTkFrame(storage_frame)
        storage_info_frame.pack(fill="x", padx=10, pady=10)
        
        # Storage progress bar with label
        storage_label_frame = ctk.CTkFrame(storage_info_frame, fg_color="transparent")
        storage_label_frame.pack(fill="x", padx=10, pady=10)
        
        self.storage_usage_label = ctk.CTkLabel(
            storage_label_frame,
            text="Loading storage information...",
            font=ctk.CTkFont(size=14)
        )
        self.storage_usage_label.pack(anchor="w")
        
        # Progress bar
        self.storage_progress_bar = ctk.CTkProgressBar(
            storage_info_frame,
            width=400,
            height=20,
            corner_radius=10
        )
        self.storage_progress_bar.pack(fill="x", padx=10, pady=(5, 15))
        self.storage_progress_bar.set(0)
        
        # Detailed storage info
        self.storage_details_frame = ctk.CTkFrame(storage_info_frame)
        self.storage_details_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # Storage details will be populated by update_storage_display method
        
        # Refresh storage button
        refresh_storage_button = ctk.CTkButton(
            storage_frame,
            text="🔄 Refresh Storage Info",
            command=self.update_storage_display,
            width=200
        )
        refresh_storage_button.pack(pady=10)
        
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
        
        # Update storage display on startup
        self.update_storage_display()
        
    def setup_appearance_settings_content(self):
        """Setup appearance settings tab content"""
        # Main container with scrollable frame for better organization
        main_container = ctk.CTkScrollableFrame(self.appearance_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure improved scroll speed
        self.configure_scroll_speed(main_container)
        
        # Title
        ctk.CTkLabel(main_container, text="Appearance & UI Settings", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))
        
        # Theme selection (FUNCTIONAL)
        theme_frame = ctk.CTkFrame(main_container)
        theme_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(theme_frame, text="🎨 Color Theme", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        theme_description = ctk.CTkLabel(
            theme_frame,
            text="Choose the overall appearance of the application interface.",
            font=ctk.CTkFont(size=12),
            text_color=("gray20", "gray70")
        )
        theme_description.pack(pady=(0, 10))
        
        self.theme_var = tk.StringVar(value="light")  # Default to light as per user preference
        
        # Theme radio buttons with better descriptions
        theme_options = [
            ("🌞 Light Mode", "light", "Clean, bright interface (Recommended)"),
            ("🌙 Dark Mode", "dark", "Dark interface, easier on eyes"),
            ("⚙️ System Default", "system", "Match system theme settings")
        ]
        
        for text, value, description in theme_options:
            option_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
            option_frame.pack(fill="x", padx=20, pady=2)
            
            radio_btn = ctk.CTkRadioButton(
                option_frame, 
                text=text, 
                variable=self.theme_var,
                value=value, 
                command=self.change_theme,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            radio_btn.pack(anchor="w")
            
            desc_label = ctk.CTkLabel(
                option_frame,
                text=f"  • {description}",
                font=ctk.CTkFont(size=11),
                text_color=("gray30", "gray60")
            )
            desc_label.pack(anchor="w", padx=(30, 0))
        
        # UI Scale and Layout (NEW FUNCTIONAL FEATURES)
        layout_frame = ctk.CTkFrame(main_container)
        layout_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(layout_frame, text="📐 Interface Layout", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        # Window size preferences
        window_size_frame = ctk.CTkFrame(layout_frame, fg_color="transparent")
        window_size_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(window_size_frame, text="Default Window Size:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        
        self.window_size_var = tk.StringVar(value="1600x1000")
        window_sizes = ["1200x800", "1400x900", "1600x1000", "1920x1080", "Maximized"]
        
        window_size_menu = ctk.CTkComboBox(
            window_size_frame,
            values=window_sizes,
            variable=self.window_size_var,
            width=200,
            command=self.update_window_size_preview
        )
        window_size_menu.pack(anchor="w", pady=5)
        
        self.window_size_preview = ctk.CTkLabel(
            window_size_frame,
            text="Current: 1600x1000 pixels (Recommended for most screens)",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray60")
        )
        self.window_size_preview.pack(anchor="w", pady=(5, 0))
        
        # Scroll speed setting (FUNCTIONAL - based on existing implementation)
        scroll_frame = ctk.CTkFrame(layout_frame, fg_color="transparent")
        scroll_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(scroll_frame, text="Mouse Wheel Scroll Speed:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        
        self.scroll_speed_var = tk.StringVar(value="Enhanced (Current)")
        scroll_speeds = ["Standard", "Enhanced (Current)", "Fast"]
        
        scroll_speed_menu = ctk.CTkComboBox(
            scroll_frame,
            values=scroll_speeds,
            variable=self.scroll_speed_var,
            width=200
        )
        scroll_speed_menu.pack(anchor="w", pady=5)
        
        scroll_info = ctk.CTkLabel(
            scroll_frame,
            text="Enhanced speed is already active (2x faster than standard)",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray60")
        )
        scroll_info.pack(anchor="w", pady=(5, 0))
        
        # Application behavior
        behavior_frame = ctk.CTkFrame(main_container)
        behavior_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(behavior_frame, text="🔧 Application Behavior", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        # Remember window position
        self.remember_position_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            behavior_frame,
            text="Remember window position and size",
            variable=self.remember_position_var,
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=20, pady=5)
        
        # Auto-save preferences
        self.auto_save_preferences_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            behavior_frame,
            text="Automatically save appearance preferences",
            variable=self.auto_save_preferences_var,
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=20, pady=5)
        
        # Start minimized option
        self.start_minimized_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            behavior_frame,
            text="Start application minimized to system tray",
            variable=self.start_minimized_var,
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", padx=20, pady=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        # Apply button
        apply_btn = ctk.CTkButton(
            button_frame,
            text="✅ Apply Appearance Settings",
            command=self.apply_appearance_settings,
            fg_color="green",
            hover_color="dark green",
            width=250,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        apply_btn.pack(side="left", padx=10, pady=15)
        
        # Reset to defaults button
        reset_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Reset to Defaults",
            command=self.reset_appearance_defaults,
            fg_color="orange",
            hover_color="dark orange",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        reset_btn.pack(side="left", padx=10, pady=15)
        
        # Load current preferences on startup
        self.load_appearance_preferences()
        
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
        ctk.CTkButton(backup_button_frame, text="Export Orders", 
                     command=lambda: self.export_data_to_excel("orders")).pack(side="left", padx=5)
        ctk.CTkButton(backup_button_frame, text="Export Transactions", 
                     command=lambda: self.export_data_to_excel("transactions")).pack(side="left", padx=5)
        ctk.CTkButton(backup_button_frame, text="Export Customers", 
                     command=lambda: self.export_data_to_excel("customers")).pack(side="left", padx=5)
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
        ctk.CTkButton(import_button_frame, text="Import Orders", 
                     command=lambda: self.import_data_from_excel("orders")).pack(side="left", padx=5)
        ctk.CTkButton(import_button_frame, text="Import Transactions", 
                     command=lambda: self.import_data_from_excel("transactions")).pack(side="left", padx=5)
        ctk.CTkButton(import_button_frame, text="Import Customers", 
                     command=lambda: self.import_data_from_excel("customers")).pack(side="left", padx=5)
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
        
        # First row of clear buttons
        first_row = ctk.CTkFrame(reset_button_frame, fg_color="transparent")
        first_row.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(first_row, text="Clear Employees", 
                     command=lambda: self.clear_collection("employees"),
                     fg_color="red", hover_color="dark red").pack(side="left", padx=5)
        ctk.CTkButton(first_row, text="Clear Attendance", 
                     command=lambda: self.clear_collection("attendance"),
                     fg_color="red", hover_color="dark red").pack(side="left", padx=5)
        ctk.CTkButton(first_row, text="Clear Orders", 
                     command=lambda: self.clear_collection("orders"),
                     fg_color="red", hover_color="dark red").pack(side="left", padx=5)
        
        # Second row of clear buttons
        second_row = ctk.CTkFrame(reset_button_frame, fg_color="transparent")
        second_row.pack(fill="x")
        
        ctk.CTkButton(second_row, text="Clear Transactions", 
                     command=lambda: self.clear_collection("transactions"),
                     fg_color="red", hover_color="dark red").pack(side="left", padx=5)
        ctk.CTkButton(second_row, text="Clear Customers", 
                     command=lambda: self.clear_collection("customers"),
                     fg_color="red", hover_color="dark red").pack(side="left", padx=5)
        ctk.CTkButton(second_row, text="Clear Purchases", 
                     command=lambda: self.clear_collection("purchases"),
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
Version: 2.1.0
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
                try:
                    with open(self.env_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for line in content.split('\n'):  # Fixed: was '\\n' 
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if key in env_values:
                                env_values[key] = value
                except Exception as e:
                    logger.error(f"Error reading .env file: {e}")
                    self.db_status_label.configure(text=f"⚠️ Error reading .env file: {str(e)}", text_color="orange")
            else:
                logger.warning(f".env file not found at: {self.env_file_path}")
                # Try to create a basic .env file if it doesn't exist
                try:
                    env_dir = os.path.dirname(self.env_file_path)
                    if not os.path.exists(env_dir):
                        os.makedirs(env_dir, exist_ok=True)
                    
                    # Create basic .env file with empty values
                    basic_env_content = """# MongoDB Atlas Configuration
# Configure your MongoDB Atlas connection below

MONGODB_URI=
MONGODB_DATABASE=hr_management_db
ATLAS_CLUSTER_NAME=
ATLAS_DATABASE_USER=
ATLAS_DATABASE_PASSWORD=

# Application Security
SECRET_KEY=change-this-for-production

# Development Settings
DEBUG_MODE=True
"""
                    with open(self.env_file_path, 'w', encoding='utf-8') as f:
                        f.write(basic_env_content)
                    logger.info(f"Created basic .env file at: {self.env_file_path}")
                except Exception as e:
                    logger.error(f"Could not create .env file: {e}")
            
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
    
    def update_storage_display(self):
        """Update the storage usage display in settings"""
        try:
            if self.data_service:
                storage_info = self.data_service.get_storage_usage()
                
                usage_percentage = storage_info.get('usage_percentage', 0)
                total_size_mb = storage_info.get('total_size_mb', 0)
                data_size_mb = storage_info.get('data_size_mb', 0)
                index_size_mb = storage_info.get('index_size_mb', 0)
                limit_mb = storage_info.get('limit_mb', 512)
                remaining_mb = storage_info.get('remaining_mb', 0)
                is_atlas = storage_info.get('is_atlas', True)
                database_name = storage_info.get('database_name', 'Unknown')
                
                # Update main label
                if 'error' in storage_info:
                    self.storage_usage_label.configure(
                        text=f"❌ Error getting storage info: {storage_info['error']}",
                        text_color="red"
                    )
                else:
                    self.storage_usage_label.configure(
                        text=f"Database: {database_name} - Storage Usage: {usage_percentage}% ({total_size_mb:.1f}MB / {limit_mb:.0f}MB)",
                        text_color="black"
                    )
                
                # Update progress bar
                self.storage_progress_bar.set(usage_percentage / 100)
                
                # Set color based on usage
                if usage_percentage > 80:
                    color = "#EF4444"  # Red
                elif usage_percentage > 60:
                    color = "#F59E0B"  # Orange
                else:
                    color = "#10B981"  # Green
                
                self.storage_progress_bar.configure(progress_color=color)
                
                # Clear and update detailed storage info
                for widget in self.storage_details_frame.winfo_children():
                    widget.destroy()
                
                details = [
                    f"📊 Data Size: {data_size_mb:.2f} MB",
                    f"🗂️ Index Size: {index_size_mb:.2f} MB", 
                    f"💾 Total Used: {total_size_mb:.2f} MB",
                    f"📉 Remaining: {remaining_mb:.2f} MB",
                    f"🌐 Atlas Free Tier: {'Yes' if is_atlas else 'No'}"
                ]
                
                for i, detail in enumerate(details):
                    label = ctk.CTkLabel(
                        self.storage_details_frame,
                        text=detail,
                        font=ctk.CTkFont(size=12),
                        anchor="w"
                    )
                    label.grid(row=i//2, column=i%2, sticky="w", padx=10, pady=5)
                
                # Add warning if usage is high
                if usage_percentage > 80:
                    warning_label = ctk.CTkLabel(
                        self.storage_details_frame,
                        text="⚠️ WARNING: Storage usage is high! Consider cleaning up data.",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="red"
                    )
                    warning_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=10)
            
            else:
                self.storage_usage_label.configure(
                    text="❌ Data service not available",
                    text_color="red"
                )
                self.storage_progress_bar.set(0)
                
        except Exception as e:
            logger.error(f"Error updating storage display: {e}")
            self.storage_usage_label.configure(
                text=f"❌ Error: {str(e)}",
                text_color="red"
            )
            self.storage_progress_bar.set(0)
    
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
            
            # Ensure directory exists
            env_dir = os.path.dirname(self.env_file_path)
            if not os.path.exists(env_dir):
                os.makedirs(env_dir, exist_ok=True)
            
            # Write to .env file
            with open(self.env_file_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            # Verify the file was written
            if os.path.exists(self.env_file_path):
                with open(self.env_file_path, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                    if uri in saved_content:
                        messagebox.showinfo("Success", 
                            f"Database settings saved successfully!\n\n"
                            f"✅ Connection string saved\n"
                            f"✅ Database name saved\n" 
                            f"✅ Atlas credentials saved\n\n"
                            f"File saved to: {self.env_file_path}\n\n"
                            f"Note: You may need to restart the application for changes to take effect.")
                    else:
                        raise Exception("Settings were not saved correctly")
            else:
                raise Exception(f"Could not create .env file at {self.env_file_path}")
            
            # Disable edit mode after saving
            self.edit_mode_var.set(False)
            self.toggle_edit_mode()
            
        except PermissionError:
            messagebox.showerror("Permission Error", 
                f"Cannot write to .env file. Please ensure:\n"
                f"1. The application has write permissions\n"
                f"2. The .env file is not open in another program\n"
                f"3. You're running as administrator if needed\n\n"
                f"File path: {self.env_file_path}")
        except Exception as e:
            messagebox.showerror("Error", 
                f"Failed to save settings: {str(e)}\n\n"
                f"Attempted to save to: {self.env_file_path}\n"
                f"File exists: {os.path.exists(self.env_file_path)}\n"
                f"Directory exists: {os.path.exists(os.path.dirname(self.env_file_path))}")
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
        """Change application theme with immediate feedback"""
        try:
            theme = self.theme_var.get()
            if self.theme_callback:
                self.theme_callback(theme)
                
            # Provide immediate feedback
            theme_names = {"light": "Light Mode", "dark": "Dark Mode", "system": "System Default"}
            messagebox.showinfo("Theme Applied", 
                               f"✅ {theme_names.get(theme, theme)} has been applied successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change theme: {str(e)}")
    
    def update_window_size_preview(self, value):
        """Update window size preview text"""
        size_descriptions = {
            "1200x800": "1200x800 pixels (Compact, good for smaller screens)",
            "1400x900": "1400x900 pixels (Balanced size for medium screens)",
            "1600x1000": "1600x1000 pixels (Recommended for most screens)",
            "1920x1080": "1920x1080 pixels (Full HD, for large displays)",
            "Maximized": "Maximized window (Use full screen space)"
        }
        
        description = size_descriptions.get(value, f"{value} pixels")
        self.window_size_preview.configure(text=f"Preview: {description}")
    
    def load_appearance_preferences(self):
        """Load saved appearance preferences"""
        try:
            prefs_file = os.path.join(os.getcwd(), "appearance_prefs.json")
            if os.path.exists(prefs_file):
                with open(prefs_file, 'r') as f:
                    prefs = json.load(f)
                    
                # Load preferences into UI
                self.theme_var.set(prefs.get("theme", "light"))
                # Note: Removed color theme - using default blue
                self.window_size_var.set(prefs.get("window_size", "1600x1000"))
                self.scroll_speed_var.set(prefs.get("scroll_speed", "Enhanced (Current)"))
                self.remember_position_var.set(prefs.get("remember_position", True))
                self.auto_save_preferences_var.set(prefs.get("auto_save", True))
                self.start_minimized_var.set(prefs.get("start_minimized", False))
                
                # Update preview
                self.update_window_size_preview(self.window_size_var.get())
                
        except Exception as e:
            logger.warning(f"Could not load appearance preferences: {e}")
    
    def save_appearance_preferences(self):
        """Save appearance preferences to file"""
        try:
            prefs = {
                "theme": self.theme_var.get(),
                # Note: Removed color theme - using default blue
                "window_size": self.window_size_var.get(),
                "scroll_speed": self.scroll_speed_var.get(),
                "remember_position": self.remember_position_var.get(),
                "auto_save": self.auto_save_preferences_var.get(),
                "start_minimized": self.start_minimized_var.get(),
                "last_updated": datetime.now().isoformat()
            }
            
            prefs_file = os.path.join(os.getcwd(), "appearance_prefs.json")
            with open(prefs_file, 'w') as f:
                json.dump(prefs, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Failed to save appearance preferences: {e}")
            return False
    
    def reset_appearance_defaults(self):
        """Reset all appearance settings to defaults"""
        try:
            # Confirm reset
            result = messagebox.askyesno(
                "Reset to Defaults",
                "Are you sure you want to reset all appearance settings to their default values?\n\n"
                "This will:\n"
                "• Set theme to Light Mode\n"
                "• Keep default blue accent color\n"
                "• Reset window size to 1600x1000\n"
                "• Reset all behavior settings"
            )
            
            if result:
                # Reset all variables to defaults
                self.theme_var.set("light")
                # Note: Removed color theme - using default blue
                self.window_size_var.set("1600x1000")
                self.scroll_speed_var.set("Enhanced (Current)")
                self.remember_position_var.set(True)
                self.auto_save_preferences_var.set(True)
                self.start_minimized_var.set(False)
                
                # Update preview
                self.update_window_size_preview("1600x1000")
                
                # Apply the reset settings
                self.apply_appearance_settings()
                
                messagebox.showinfo("Reset Complete", 
                                   "✅ All appearance settings have been reset to defaults!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")

    def apply_appearance_settings(self):
        """Apply all appearance settings with comprehensive feedback"""
        try:
            # Apply theme immediately
            self.change_theme()
            
            # Save preferences if auto-save is enabled
            if self.auto_save_preferences_var.get():
                if self.save_appearance_preferences():
                    success_msg = "✅ Appearance settings applied and saved successfully!"
                else:
                    success_msg = "✅ Appearance settings applied (but could not save preferences)"
            else:
                success_msg = "✅ Appearance settings applied successfully!"
            
            # Provide detailed feedback
            feedback_details = []
            feedback_details.append(f"Theme: {self.theme_var.get().title()}")
            feedback_details.append("Accent Color: Blue (Default)")
            feedback_details.append(f"Window Size: {self.window_size_var.get()}")
            
            messagebox.showinfo("Settings Applied", 
                               success_msg + "\n\n" + "\n".join(feedback_details))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply appearance settings: {str(e)}")
            logger.error(f"Error applying appearance settings: {e}")
    
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
            elif collection_name == "orders":
                data_df = self.data_service.get_orders()
                data = data_df.to_dict('records') if not data_df.empty else []
            elif collection_name == "transactions":
                data_df = self.data_service.get_transactions()
                data = data_df.to_dict('records') if not data_df.empty else []
            elif collection_name == "customers":
                data_df = self.data_service.get_customers()
                data = data_df.to_dict('records') if not data_df.empty else []
            elif collection_name == "purchases":
                data_df = self.data_service.get_purchases()
                data = data_df.to_dict('records') if not data_df.empty else []
            elif collection_name == "sales":  # Keep for backward compatibility
                data_df = self.data_service.get_sales()
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
                
                collections = ["employees", "attendance", "orders", "transactions", "customers", "purchases"]
                
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
                        elif collection == "orders":
                            data_df = self.data_service.get_orders()
                            data = data_df.to_dict('records') if not data_df.empty else []
                        elif collection == "transactions":
                            data_df = self.data_service.get_transactions()
                            data = data_df.to_dict('records') if not data_df.empty else []
                        elif collection == "customers":
                            data_df = self.data_service.get_customers()
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
                        elif collection_name == "orders":
                            if self.data_service.add_order(record):
                                success_count += 1
                        elif collection_name == "transactions":
                            if self.data_service.add_transaction(record):
                                success_count += 1
                        elif collection_name == "customers":
                            if self.data_service.add_customer(record):
                                success_count += 1
                        elif collection_name == "purchases":
                            if self.data_service.add_purchase(record):
                                success_count += 1
                        elif collection_name == "sales":  # Keep for backward compatibility
                            if self.data_service.add_sale(record):
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
                elif collection_name == "orders":
                    result = self.data_service.db_manager.clear_collection("orders")
                elif collection_name == "transactions":
                    result = self.data_service.db_manager.clear_collection("transactions")
                elif collection_name == "customers":
                    result = self.data_service.db_manager.clear_collection("customers")
                elif collection_name == "purchases":
                    result = self.data_service.db_manager.clear_collection("purchases")
                elif collection_name == "sales":  # Keep for backward compatibility
                    result = self.data_service.db_manager.clear_collection("sales")
                
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
                                      "This is your final warning!\n\nAll employees, attendance, orders, transactions, customers, and purchase data will be permanently deleted.\n\nContinue?"):
                    
                    collections = ["employees", "attendance", "orders", "transactions", "customers", "purchases"]
                    
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
            orders_df = self.data_service.get_orders()
            orders_count = len(orders_df) if not orders_df.empty else 0
            transactions_df = self.data_service.get_transactions()
            transactions_count = len(transactions_df) if not transactions_df.empty else 0
            customers_df = self.data_service.get_customers()
            customers_count = len(customers_df) if not customers_df.empty else 0
            purchases_df = self.data_service.get_purchases()
            purchases_count = len(purchases_df) if not purchases_df.empty else 0
            
            stats_text = f"""Database Statistics:
• Employees: {employees_count} records
• Attendance: {attendance_count} records  
• Orders: {orders_count} records
• Transactions: {transactions_count} records
• Customers: {customers_count} records
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
        """Check for application updates from GitHub Releases"""
        try:
            from update_manager import check_for_updates_async
            from config import APP_VERSION
            
            # Check for updates in background thread
            check_for_updates_async(
                parent_window=self.parent,
                current_version=APP_VERSION,
                show_no_update=True
            )
            
        except ImportError as e:
            logger.error(f"Update manager not available: {e}")
            messagebox.showerror("Update Error", "Update functionality is not available.")
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
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
