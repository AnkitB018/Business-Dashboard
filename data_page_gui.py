"""
Enhanced Data Management GUI Page with Web-like Design
Modern interface that mimics the quality of the original web application
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class ModernDataPageGUI:
    def __init__(self, parent, data_service):
        self.parent = parent
        self.data_service = data_service
        self.frame = None
        
        # Color scheme (modern web-like colors)
        self.colors = {
            'primary': '#3B82F6',      # Blue
            'success': '#10B981',      # Green  
            'warning': '#F59E0B',      # Orange
            'danger': '#EF4444',       # Red
            'light': '#F8FAFC',        # Light gray
            'dark': '#1E293B',         # Dark gray
            'card_bg': '#FFFFFF',      # Card background
            'border': '#E2E8F0'        # Border color
        }
        
        self.create_page()
        
    def darken_color(self, color, factor=0.8):
        """Darken a hex color by a factor"""
        # Remove # if present
        color = color.lstrip('#')
        # Convert to RGB
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        # Darken
        darkened = tuple(int(c * factor) for c in rgb)
        # Convert back to hex
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        
    def create_page(self):
        """Create the enhanced data management page"""
        # Main frame with modern styling
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color="transparent")
        
        # Create header section
        self.create_header()
        
        # Create main content area with cards
        self.create_main_content()
        
        # Create status bar at bottom
        self.create_status_bar()
        
    def create_status_bar(self):
        """Create enhanced status bar for showing messages"""
        self.status_frame = ctk.CTkFrame(self.frame, height=50, corner_radius=10)
        self.status_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.status_frame.pack_propagate(False)
        
        # Status icon and text container
        status_container = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        status_container.pack(expand=True, fill="both", padx=15, pady=8)
        
        # Status icon
        self.status_icon = ctk.CTkLabel(
            status_container,
            text="ℹ️",
            font=ctk.CTkFont(size=16)
        )
        self.status_icon.pack(side="left", padx=(0, 10))
        
        # Status message
        self.status_label = ctk.CTkLabel(
            status_container,
            text="Ready - Select a module to start managing your data",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(side="left", expand=True, fill="x")
        
        # Status timestamp
        self.status_time = ctk.CTkLabel(
            status_container,
            text="",
            font=ctk.CTkFont(size=10),
            anchor="e"
        )
        self.status_time.pack(side="right", padx=(10, 0))
        
    def show_status_message(self, message, message_type="info"):
        """Show enhanced status message with icon and timestamp"""
        icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        # Update components
        self.status_icon.configure(text=icons.get(message_type, "ℹ️"))
        self.status_label.configure(text=message)
        
        # Add timestamp
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.status_time.configure(text=current_time)
        
        # Clear message after 5 seconds
        self.parent.after(5000, lambda: self.reset_status())
        
    def reset_status(self):
        """Reset status to default"""
        self.status_icon.configure(text="ℹ️")
        self.status_label.configure(text="Ready - Select a module to start managing your data")
        self.status_time.configure(text="")
        
    def create_header(self):
        """Create modern header section"""
        header_frame = ctk.CTkFrame(self.frame, height=80, corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Title and subtitle
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="📊 Data Management",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Manage employees, attendance, inventory, and transactions",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(anchor="w")
        
        # Quick stats cards
        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(side="right", fill="y", padx=20, pady=10)
        
        self.create_quick_stats(stats_frame)
        
    def create_quick_stats(self, parent):
        """Create quick statistics cards"""
        try:
            if not self.data_service:
                return
                
            # Get quick stats using the correct method names
            employees_df = self.data_service.get_employees()
            stock_df = self.data_service.get_stock()
            
            employees_count = len(employees_df) if not employees_df.empty else 0
            stock_count = len(stock_df) if not stock_df.empty else 0
            
            stats = [
                ("👥", str(employees_count), "Employees"),
                ("📦", str(stock_count), "Items in Stock")
            ]
            
            for icon, count, label in stats:
                stat_card = ctk.CTkFrame(parent, width=120, height=50, corner_radius=8)
                stat_card.pack(side="left", padx=5)
                stat_card.pack_propagate(False)
                
                # Icon and count
                count_label = ctk.CTkLabel(
                    stat_card, 
                    text=f"{icon} {count}",
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                count_label.pack(pady=(8, 2))
                
                # Label
                label_widget = ctk.CTkLabel(
                    stat_card,
                    text=label,
                    font=ctk.CTkFont(size=10)
                )
                label_widget.pack()
                
        except Exception as e:
            logger.error(f"Error creating quick stats: {e}")
    
    def create_main_content(self):
        """Create main content area with modern card layout"""
        # Main container with scrollable frame
        main_container = ctk.CTkScrollableFrame(
            self.frame,
            corner_radius=10,
            fg_color=("gray95", "gray10")
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create module cards
        self.create_module_cards(main_container)
        
    def create_module_cards(self, parent):
        """Create modern cards for each module"""
        modules = [
            {
                "title": "👥 Employee Management",
                "description": "Manage employee records, positions, and contact information",
                "color": self.colors['primary'],
                "action": self.open_employee_module
            },
            {
                "title": "📅 Attendance Tracking", 
                "description": "Record and monitor daily attendance and working hours",
                "color": self.colors['success'],
                "action": self.open_attendance_module
            },
            {
                "title": "📦 Inventory Management",
                "description": "Control stock levels, suppliers, and product categories",
                "color": self.colors['warning'],
                "action": self.open_stock_module
            },
            {
                "title": "💰 Sales Records",
                "description": "Track sales transactions and customer information",
                "color": self.colors['success'],
                "action": self.open_sales_module
            },
            {
                "title": "🛒 Purchase Management",
                "description": "Manage purchase orders and supplier transactions",
                "color": self.colors['danger'],
                "action": self.open_purchases_module
            }
        ]
        
        # Create cards in a grid layout
        for i, module in enumerate(modules):
            self.create_module_card(parent, module, i)
    
    def create_module_card(self, parent, module, index):
        """Create individual module card"""
        # Card frame
        card_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            height=200,
            fg_color=("white", "gray20")
        )
        card_frame.pack(fill="x", pady=15, padx=10)
        card_frame.pack_propagate(False)
        
        # Card header
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=module["title"],
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Status indicator
        status_frame = ctk.CTkFrame(header_frame, width=80, height=30, corner_radius=15)
        status_frame.pack(side="right")
        status_frame.pack_propagate(False)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Active",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white"
        )
        status_label.pack(expand=True)
        
        # Description
        desc_label = ctk.CTkLabel(
            card_frame,
            text=module["description"],
            font=ctk.CTkFont(size=14),
            anchor="w",
            justify="left"
        )
        desc_label.pack(fill="x", padx=20, pady=(0, 15))
        
        # Action button
        action_btn = ctk.CTkButton(
            card_frame,
            text=f"Open {module['title'].split(' ')[1]} Module",
            command=module["action"],
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=module["color"],
            hover_color=self.darken_color(module["color"])
        )
        action_btn.pack(side="bottom", fill="x", padx=20, pady=(0, 20))
        
    def darken_color(self, color):
        """Darken a hex color for hover effect"""
        # Simple color darkening - remove # and convert
        color = color.lstrip('#')
        # Convert to RGB, darken by 20%, convert back
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    # Module window creators
    def open_employee_module(self):
        """Open employee management module"""
        self.create_data_module_window("Employee Management", "employees")
        
    def open_attendance_module(self):
        """Open attendance tracking module"""
        self.create_data_module_window("Attendance Tracking", "attendance")
        
    def open_stock_module(self):
        """Open stock management module"""
        self.create_data_module_window("Stock Management", "stock")
        
    def open_sales_module(self):
        """Open sales management module"""
        self.create_data_module_window("Sales Management", "sales")
        
    def open_purchases_module(self):
        """Open purchases management module"""
        self.create_data_module_window("Purchase Management", "purchases")
    
    def create_data_module_window(self, title, module_type):
        """Create a modern data management window"""
        # Create new window
        module_window = ctk.CTkToplevel(self.frame)
        module_window.title(f"HR System - {title}")
        module_window.geometry("1200x700")
        module_window.grab_set()  # Make it modal
        
        # Window header
        header_frame = ctk.CTkFrame(module_window, height=80, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"📋 {title}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # Close button
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕ Close",
            command=module_window.destroy,
            width=80,
            height=35,
            fg_color="red",
            hover_color="dark red"
        )
        close_btn.pack(side="right", padx=20, pady=20)
        
        # Main content area
        content_frame = ctk.CTkFrame(module_window, corner_radius=0, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create two-panel layout (form + data table)
        self.create_two_panel_layout(content_frame, module_type)
        
    def create_two_panel_layout(self, parent, module_type):
        """Create modern two-panel layout"""
        # Left panel - Form
        left_panel = ctk.CTkFrame(parent, width=400, corner_radius=10)
        left_panel.pack(side="left", fill="y", padx=(20, 10), pady=20)
        left_panel.pack_propagate(False)
        
        # Right panel - Data table
        right_panel = ctk.CTkFrame(parent, corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=20)
        
        # Create form based on module type
        if module_type == "employees":
            self.create_employee_form(left_panel, right_panel)
        elif module_type == "attendance":
            self.create_attendance_form(left_panel, right_panel)
        elif module_type == "stock":
            self.create_stock_form(left_panel, right_panel)
        elif module_type == "sales":
            self.create_sales_form(left_panel, right_panel)
        elif module_type == "purchases":
            self.create_purchases_form(left_panel, right_panel)
    
    def create_employee_form(self, form_panel, data_panel):
        """Create enhanced employee form with department and position dropdowns"""
        # Form header
        form_header = ctk.CTkFrame(form_panel, height=60, corner_radius=8)
        form_header.pack(fill="x", padx=15, pady=(15, 10))
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="👤 Employee Details",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Scrollable form area
        form_scroll = ctk.CTkScrollableFrame(form_panel)
        form_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Form fields with enhanced controls
        self.emp_vars = {}
        
        # Basic info fields
        self.create_form_field(form_scroll, "Employee ID", "employee_id", "text", self.emp_vars,
                              placeholder="e.g., EMP001")
        self.create_form_field(form_scroll, "Full Name", "name", "text", self.emp_vars,
                              placeholder="Enter full name")
        self.create_form_field(form_scroll, "Email Address", "email", "text", self.emp_vars,
                              placeholder="employee@company.com")
        self.create_form_field(form_scroll, "Phone Number", "phone", "text", self.emp_vars,
                              placeholder="+91 98765 43210")
        
        # Department dropdown
        departments = [
            "Human Resources", "Information Technology", "Finance", "Marketing", 
            "Sales", "Operations", "Customer Service", "Research & Development",
            "Quality Assurance", "Administration"
        ]
        self.create_combo_field(form_scroll, "Department", "department", departments, self.emp_vars)
        
        # Position dropdown
        positions = [
            "Manager", "Senior Manager", "Team Lead", "Senior Developer", "Developer",
            "Junior Developer", "Business Analyst", "Data Analyst", "Designer",
            "Sales Executive", "Customer Support", "HR Executive", "Accountant",
            "Marketing Executive", "Operations Executive", "Intern"
        ]
        self.create_combo_field(form_scroll, "Position", "position", positions, self.emp_vars)
        
        # Salary field
        self.create_form_field(form_scroll, "Monthly Salary (₹)", "salary", "number", self.emp_vars,
                              placeholder="50000")
        
        # Join date
        self.create_date_picker(form_scroll, "Join Date", "join_date", self.emp_vars)
        
        # Form buttons
        self.create_form_buttons(form_scroll, "employee")
        
        # Data table
        self.create_data_table(data_panel, "employees")
    
    def create_attendance_form(self, form_panel, data_panel):
        """Create simplified and accessible attendance form"""
        # Form header
        form_header = ctk.CTkFrame(form_panel, height=60, corner_radius=8)
        form_header.pack(fill="x", padx=15, pady=(15, 10))
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="📅 Attendance Record",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Scrollable form area with better spacing
        form_scroll = ctk.CTkScrollableFrame(form_panel)
        form_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Form fields with simplified layout
        self.att_vars = {}
        
        # Employee selection dropdown
        self.create_employee_dropdown(form_scroll, "Employee", "employee_id", self.att_vars)
        
        # Date picker
        self.create_date_picker(form_scroll, "Date", "date", self.att_vars)
        
        # Time pickers with improved layout
        self.create_time_picker(form_scroll, "Time In", "time_in", self.att_vars)
        self.create_time_picker(form_scroll, "Time Out", "time_out", self.att_vars)
        
        # Status dropdown with simplified options
        self.create_combo_field(form_scroll, "Status", "status", 
                               ["Present", "Absent", "Late", "Half Day"], self.att_vars)
        
        # Notes field (optional)
        self.create_form_field(form_scroll, "Notes (Optional)", "notes", "text", self.att_vars, 
                              placeholder="Any additional notes...")
        
        # Form buttons
        self.create_form_buttons(form_scroll, "attendance")
        
        # Data table
        self.create_data_table(data_panel, "attendance")
        
    def create_employee_dropdown(self, parent, label, key, vars_dict):
        """Create employee selection dropdown"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)
        
        # Label
        label_widget = ctk.CTkLabel(
            field_frame,
            text=f"{label}*",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_widget.pack(anchor="w", pady=(0, 5))
        
        # Load employees for dropdown
        try:
            employees_df = self.data_service.get_employees()
            if not employees_df.empty:
                employee_options = [
                    f"{row['employee_id']} - {row['name']}" 
                    for _, row in employees_df.iterrows()
                ]
            else:
                employee_options = ["No employees found"]
        except Exception as e:
            employee_options = ["Error loading employees"]
            logger.error(f"Error loading employees: {e}")
        
        # Dropdown
        vars_dict[key] = tk.StringVar()
        dropdown = ctk.CTkComboBox(
            field_frame,
            variable=vars_dict[key],
            values=employee_options,
            width=300,
            height=35,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=12)
        )
        dropdown.pack(fill="x", pady=(0, 5))
        
        # Helper text
        helper_text = ctk.CTkLabel(
            field_frame,
            text="Select an employee from the list",
            font=ctk.CTkFont(size=10)
        )
        helper_text.pack(anchor="w")
        
    def create_date_picker(self, parent, label, key, vars_dict):
        """Create date picker with calendar-like interface"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)
        
        # Label
        label_widget = ctk.CTkLabel(
            field_frame,
            text=f"{label}*",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#374151"
        )
        label_widget.pack(anchor="w", pady=(0, 5))
        
        # Date input frame
        date_frame = ctk.CTkFrame(field_frame, fg_color="transparent")
        date_frame.pack(fill="x")
        
        # Date entry
        vars_dict[key] = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        date_entry = ctk.CTkEntry(
            date_frame,
            textvariable=vars_dict[key],
            width=200,
            height=35,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=12),
            placeholder_text="YYYY-MM-DD"
        )
        date_entry.pack(side="left", padx=(0, 10))
        
        # Today button
        today_btn = ctk.CTkButton(
            date_frame,
            text="Today",
            command=lambda: vars_dict[key].set(date.today().strftime("%Y-%m-%d")),
            width=80,
            height=35,
            corner_radius=6
        )
        today_btn.pack(side="left")
        
        # Helper text
        helper_text = ctk.CTkLabel(
            field_frame,
            text="Format: YYYY-MM-DD (e.g., 2024-08-30)",
            font=ctk.CTkFont(size=10)
        )
        helper_text.pack(anchor="w", pady=(5, 0))
    
    def create_time_picker(self, parent, label, key, vars_dict):
        """Create simplified and more accessible time picker"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)
        
        # Label
        label_widget = ctk.CTkLabel(
            field_frame,
            text=f"{label}*",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_widget.pack(anchor="w", pady=(0, 5))
        
        # Main time container with better spacing
        time_container = ctk.CTkFrame(field_frame, fg_color="transparent")
        time_container.pack(fill="x")
        
        # Time input section
        time_input_frame = ctk.CTkFrame(time_container, fg_color="transparent")
        time_input_frame.pack(anchor="w")
        
        # Hour dropdown
        ctk.CTkLabel(time_input_frame, text="Hour:", font=ctk.CTkFont(size=11)).pack(side="left")
        hour_var = tk.StringVar(value="09")
        hour_combo = ctk.CTkComboBox(
            time_input_frame,
            variable=hour_var,
            values=[f"{i:02d}" for i in range(24)],
            width=70,
            height=35,
            corner_radius=6
        )
        hour_combo.pack(side="left", padx=(5, 10))
        
        # Minute dropdown
        ctk.CTkLabel(time_input_frame, text="Min:", font=ctk.CTkFont(size=11)).pack(side="left")
        minute_var = tk.StringVar(value="00")
        minute_combo = ctk.CTkComboBox(
            time_input_frame,
            variable=minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 15)],  # 15-minute intervals
            width=70,
            height=35,
            corner_radius=6
        )
        minute_combo.pack(side="left", padx=(5, 20))
        
        # Quick time buttons - arranged in a more accessible way
        quick_times_frame = ctk.CTkFrame(time_container, fg_color="transparent")
        quick_times_frame.pack(anchor="w", pady=(10, 0))
        
        ctk.CTkLabel(quick_times_frame, text="Quick Select:", font=ctk.CTkFont(size=11)).pack(anchor="w")
        
        # Row of time buttons with better spacing
        buttons_frame = ctk.CTkFrame(quick_times_frame, fg_color="transparent")
        buttons_frame.pack(anchor="w", pady=(5, 0))
        
        quick_times = [
            ("9:00 AM", "09:00"),
            ("12:00 PM", "12:00"), 
            ("5:00 PM", "17:00"),
            ("Now", datetime.now().strftime("%H:%M"))
        ]
        
        for btn_text, time_val in quick_times:
            time_btn = ctk.CTkButton(
                buttons_frame,
                text=btn_text,
                command=lambda t=time_val, h_var=hour_var, m_var=minute_var: self.set_time(t, h_var, m_var),
                width=80,
                height=32,
                corner_radius=6,
                font=ctk.CTkFont(size=11)
            )
            time_btn.pack(side="left", padx=(0, 8))
        
        # Combine hour and minute into time string
        vars_dict[key] = tk.StringVar()
        
        def update_time(*args):
            vars_dict[key].set(f"{hour_var.get()}:{minute_var.get()}")
        
        hour_var.trace("w", update_time)
        minute_var.trace("w", update_time)
        update_time()  # Initial value
        
        # Helper text
        helper_text = ctk.CTkLabel(
            field_frame,
            text="Select time using dropdowns or quick buttons",
            font=ctk.CTkFont(size=10)
        )
        helper_text.pack(anchor="w", pady=(8, 0))
    
    def set_time(self, time_str, hour_var, minute_var):
        """Set time from button click"""
        try:
            if ":" in time_str:
                hour, minute = time_str.split(":")
                hour_var.set(hour)
                minute_var.set(minute)
        except Exception as e:
            logger.error(f"Error setting time: {e}")
    
    def darken_color(self, color):
        """Darken a hex color for hover effect"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    def create_stock_form(self, form_panel, data_panel):
        """Create modern stock form"""
        # Form header
        form_header = ctk.CTkFrame(form_panel, height=60, corner_radius=8)
        form_header.pack(fill="x", padx=15, pady=(15, 10))
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="📦 Stock Item",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Scrollable form area
        form_scroll = ctk.CTkScrollableFrame(form_panel)
        form_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Form fields
        self.stock_vars = {}
        fields = [
            ("Item Name", "item_name", "text"),
            ("Category", "category", "text"),
            ("Quantity", "quantity", "number"),
            ("Price per Unit (₹)", "price_per_unit", "number"),
            ("Supplier", "supplier", "text")
        ]
        
        for label, key, field_type in fields:
            self.create_form_field(form_scroll, label, key, field_type, self.stock_vars)
        
        # Form buttons
        self.create_form_buttons(form_scroll, "stock")
        
        # Data table
        self.create_data_table(data_panel, "stock")
    
    def create_sales_form(self, form_panel, data_panel):
        """Create modern sales form"""
        # Form header
        form_header = ctk.CTkFrame(form_panel, height=60, corner_radius=8)
        form_header.pack(fill="x", padx=15, pady=(15, 10))
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="💰 Sales Record",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Scrollable form area
        form_scroll = ctk.CTkScrollableFrame(form_panel)
        form_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Form fields
        self.sales_vars = {}
        fields = [
            ("Item Name", "item_name", "text"),
            ("Quantity Sold", "quantity", "number"),
            ("Sale Price (₹)", "price_per_unit", "number"),
            ("Customer Name", "customer", "text"),
            ("Sale Date", "date", "date")
        ]
        
        for label, key, field_type in fields:
            if field_type == "date":
                self.create_form_field(form_scroll, label, key, "text", self.sales_vars, placeholder=date.today().strftime("%Y-%m-%d"))
            else:
                self.create_form_field(form_scroll, label, key, field_type, self.sales_vars)
        
        # Form buttons
        self.create_form_buttons(form_scroll, "sales")
        
        # Data table
        self.create_data_table(data_panel, "sales")
    
    def create_purchases_form(self, form_panel, data_panel):
        """Create modern purchases form"""
        # Form header
        form_header = ctk.CTkFrame(form_panel, height=60, corner_radius=8)
        form_header.pack(fill="x", padx=15, pady=(15, 10))
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="🛒 Purchase Record",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Scrollable form area
        form_scroll = ctk.CTkScrollableFrame(form_panel)
        form_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Form fields
        self.purchase_vars = {}
        fields = [
            ("Item Name", "item_name", "text"),
            ("Quantity", "quantity", "number"),
            ("Purchase Price (₹)", "price_per_unit", "number"),
            ("Supplier", "supplier", "text"),
            ("Purchase Date", "date", "date")
        ]
        
        for label, key, field_type in fields:
            if field_type == "date":
                self.create_form_field(form_scroll, label, key, "text", self.purchase_vars, placeholder=date.today().strftime("%Y-%m-%d"))
            else:
                self.create_form_field(form_scroll, label, key, field_type, self.purchase_vars)
        
        # Form buttons
        self.create_form_buttons(form_scroll, "purchases")
        
        # Data table
        self.create_data_table(data_panel, "purchases")
    
    def create_form_field(self, parent, label, key, field_type, var_dict, placeholder=""):
        """Create a modern form field"""
        # Field container
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)
        
        # Label
        label_widget = ctk.CTkLabel(
            field_frame,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.pack(anchor="w", pady=(0, 5))
        
        # Entry field
        var_dict[key] = tk.StringVar()
        
        entry = ctk.CTkEntry(
            field_frame,
            textvariable=var_dict[key],
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            placeholder_text=placeholder if placeholder else f"Enter {label.lower()}"
        )
        entry.pack(fill="x")
        
        return entry
    
    def create_combo_field(self, parent, label, key, values, var_dict):
        """Create a modern combo box field"""
        # Field container
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)
        
        # Label
        label_widget = ctk.CTkLabel(
            field_frame,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.pack(anchor="w", pady=(0, 5))
        
        # Combo box
        var_dict[key] = tk.StringVar(value=values[0] if values else "")
        
        combo = ctk.CTkComboBox(
            field_frame,
            values=values,
            variable=var_dict[key],
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        combo.pack(fill="x")
        
        return combo
    
    def create_form_buttons(self, parent, module_type):
        """Create modern form buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        # Add button
        add_btn = ctk.CTkButton(
            button_frame,
            text="✅ Add Record",
            command=lambda: self.add_record(module_type),
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['success'],
            hover_color=self.darken_color(self.colors['success'])
        )
        add_btn.pack(fill="x", pady=2)
        
        # Update button
        update_btn = ctk.CTkButton(
            button_frame,
            text="📝 Update Record",
            command=lambda: self.update_record(module_type),
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary'])
        )
        update_btn.pack(fill="x", pady=2)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete Record",
            command=lambda: self.delete_record(module_type),
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['danger'],
            hover_color=self.darken_color(self.colors['danger'])
        )
        delete_btn.pack(fill="x", pady=2)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Clear Form",
            command=lambda: self.clear_form(module_type),
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['warning'],
            hover_color=self.darken_color(self.colors['warning'])
        )
        clear_btn.pack(fill="x", pady=2)
    
    def create_data_table(self, parent, table_type):
        """Create modern data table"""
        # Table header
        table_header = ctk.CTkFrame(parent, height=60, corner_radius=8)
        table_header.pack(fill="x", padx=15, pady=(15, 10))
        table_header.pack_propagate(False)
        
        ctk.CTkLabel(
            table_header,
            text=f"📋 {table_type.title()} Data",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", pady=15, padx=15)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            table_header,
            text="🔄 Refresh",
            command=lambda: self.refresh_table(table_type),
            width=80,
            height=35,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary'])
        )
        refresh_btn.pack(side="right", pady=15, padx=15)
        
        # Table frame
        table_frame = ctk.CTkFrame(parent, corner_radius=8)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create treeview with modern styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure treeview colors
        style.configure("Treeview",
                       background="#F8FAFC",
                       foreground="#1E293B",
                       rowheight=35,
                       fieldbackground="#F8FAFC",
                       font=('Segoe UI', 10))
        
        style.configure("Treeview.Heading",
                       background="#3B82F6",
                       foreground="white",
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Treeview',
                 background=[('selected', '#3B82F6')])
        
        # Define columns based on table type
        columns = self.get_table_columns(table_type)
        
        # Create treeview
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=120, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))
        
        # Store reference for updates
        setattr(self, f"{table_type}_tree", tree)
        
        # Bind selection event
        tree.bind("<<TreeviewSelect>>", lambda e: self.on_table_select(table_type, tree))
        
        # Load initial data
        self.refresh_table(table_type)
    
    def get_table_columns(self, table_type):
        """Get table columns based on type"""
        columns_map = {
            "employees": ["Employee_ID", "Name", "Email", "Phone", "Department", "Position", "Salary"],
            "attendance": ["Employee_ID", "Date", "Time_In", "Time_Out", "Status", "Hours"],
            "stock": ["Item_Name", "Category", "Quantity", "Price", "Supplier", "Total_Value"],
            "sales": ["Item_Name", "Quantity", "Price", "Customer", "Date", "Total"],
            "purchases": ["Item_Name", "Quantity", "Price", "Supplier", "Date", "Total"]
        }
        return columns_map.get(table_type, ["ID", "Name", "Value"])
    
    # Data operations
    def add_record(self, module_type):
        """Add new record with proper data conversion"""
        try:
            if not self.data_service:
                self.show_status_message("Database not connected", "error")
                return
            
            if module_type == "employee":
                data = {key: var.get().strip() for key, var in self.emp_vars.items()}
                if data.get("salary"):
                    data["salary"] = float(data["salary"])
                # Add joining date as datetime
                if data.get("joining_date"):
                    data["joining_date"] = datetime.strptime(data["joining_date"], "%Y-%m-%d")
                result = self.data_service.add_employee(data)
                
            elif module_type == "attendance":
                data = {key: var.get().strip() for key, var in self.att_vars.items()}
                # Convert date string to datetime object
                if data.get("date"):
                    data["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
                # Get employee name from dropdown
                emp_id = data.get("employee_id")
                if emp_id:
                    employees = self.data_service.get_employees({"employee_id": emp_id})
                    if not employees.empty:
                        data["employee_name"] = employees.iloc[0]["name"]
                result = self.data_service.add_attendance(data)
                
            elif module_type == "stock":
                data = {key: var.get().strip() for key, var in self.stock_vars.items()}
                if data.get("current_quantity"):
                    data["current_quantity"] = int(data["current_quantity"])
                if data.get("unit_cost_average"):
                    data["unit_cost_average"] = float(data["unit_cost_average"])
                if data.get("minimum_stock"):
                    data["minimum_stock"] = int(data["minimum_stock"])
                result = self.data_service.add_stock_item(data)
                
            elif module_type == "sales":
                data = {key: var.get().strip() for key, var in self.sales_vars.items()}
                if data.get("quantity"):
                    data["quantity"] = int(data["quantity"])
                if data.get("price_per_unit"):
                    # Rename to match database schema
                    data["unit_price"] = float(data.pop("price_per_unit"))
                if data.get("customer"):
                    # Rename to match database schema
                    data["customer_name"] = data.pop("customer")
                # Convert date string to datetime object
                if data.get("date"):
                    data["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
                # Calculate total price
                if data.get("quantity") and data.get("unit_price"):
                    data["total_price"] = data["quantity"] * data["unit_price"]
                result = self.data_service.add_sale(data)
                
            elif module_type == "purchases":
                data = {key: var.get().strip() for key, var in self.purchase_vars.items()}
                if data.get("quantity"):
                    data["quantity"] = int(data["quantity"])
                if data.get("price_per_unit"):
                    # Rename to match database schema
                    data["unit_price"] = float(data.pop("price_per_unit"))
                # Convert date string to datetime object
                if data.get("date"):
                    data["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
                # Calculate total price
                if data.get("quantity") and data.get("unit_price"):
                    data["total_price"] = data["quantity"] * data["unit_price"]
                result = self.data_service.add_purchase(data)
            
            if result:
                # Clear form and refresh all tables with status message
                self.clear_form(module_type)
                # Refresh all tables immediately after successful operation
                self.refresh_all_tables()
                self.show_status_message(f"{module_type.capitalize()} added successfully", "success")
            else:
                self.show_status_message(f"Failed to add {module_type} record", "error")
                
        except Exception as e:
            self.show_status_message(f"Failed to add record: {str(e)}", "error")
    
    def update_record(self, module_type):
        """Update existing record"""
        # Update functionality placeholder - no popup
        pass
    
    def delete_record(self, module_type):
        """Delete selected records from table"""
        try:
            # Get the appropriate tree widget - fix the naming issue
            tree_name = f"{module_type}s_tree"
            tree = getattr(self, tree_name, None)
            if not tree:
                self.show_status_message(f"Table not found: {tree_name}", "error")
                return
                
            # Get selected items
            selected_items = tree.selection()
            if not selected_items:
                self.show_status_message("Please select rows to delete", "warning")
                return
            
            # Delete each selected record
            deleted_count = 0
            for item in selected_items:
                values = tree.item(item, 'values')
                if not values:
                    continue
                    
                # Build filter for deletion based on module type
                result = False
                if module_type == "employee":
                    result = self.data_service.delete_employee(values[0])
                elif module_type == "attendance":
                    # Parse date properly for attendance deletion
                    date_str = str(values[1])
                    try:
                        # Convert date string to datetime for filtering
                        if len(date_str) == 10:  # YYYY-MM-DD format
                            filter_date = datetime.strptime(date_str, '%Y-%m-%d')
                        else:
                            filter_date = date_str
                        filter_dict = {"employee_id": values[0], "date": filter_date}
                        result = self.data_service.delete_attendance(filter_dict)
                    except Exception as e:
                        logger.error(f"Error parsing date for deletion: {e}")
                        continue
                elif module_type == "stock":
                    result = self.data_service.delete_stock_item(values[0])
                elif module_type == "sale":  # Note: singular form
                    # Parse date properly for sales deletion
                    date_str = str(values[4])
                    try:
                        if len(date_str) == 10:
                            filter_date = datetime.strptime(date_str, '%Y-%m-%d')
                        else:
                            filter_date = date_str
                        filter_dict = {"item_name": values[0], "date": filter_date}
                        result = self.data_service.delete_sale(filter_dict)
                    except Exception as e:
                        logger.error(f"Error parsing date for sales deletion: {e}")
                        continue
                elif module_type == "purchase":  # Note: singular form
                    # Parse date properly for purchase deletion  
                    date_str = str(values[4])
                    try:
                        if len(date_str) == 10:
                            filter_date = datetime.strptime(date_str, '%Y-%m-%d')
                        else:
                            filter_date = date_str
                        filter_dict = {"item_name": values[0], "date": filter_date}
                        result = self.data_service.delete_purchase(filter_dict)
                    except Exception as e:
                        logger.error(f"Error parsing date for purchase deletion: {e}")
                        continue
                
                if result:
                    deleted_count += 1
            
            # Refresh all tables and show status
            self.refresh_all_tables()
            if deleted_count > 0:
                self.show_status_message(f"Deleted {deleted_count} {module_type} record(s)", "success")
            else:
                self.show_status_message("No records were deleted", "warning")
                
        except Exception as e:
            self.show_status_message(f"Failed to delete records: {str(e)}", "error")
    
    def clear_form(self, module_type):
        """Clear form fields"""
        try:
            var_dict = getattr(self, f"{module_type}_vars", {})
            for var in var_dict.values():
                if hasattr(var, 'set'):
                    var.set("")
            self.show_status_message(f"{module_type.capitalize()} form cleared", "info")
        except Exception as e:
            self.show_status_message(f"Failed to clear form: {str(e)}", "error")
    
    def refresh_all_tables(self):
        """Refresh all tables across all tabs"""
        try:
            table_types = ["employees", "attendance", "stock", "sales", "purchases"]
            for table_type in table_types:
                tree = getattr(self, f"{table_type}_tree", None)
                if tree:
                    self.refresh_table(table_type)
            
            # Force UI update
            self.parent.update_idletasks()
            self.show_status_message("All tables refreshed", "success")
                
        except Exception as e:
            self.show_status_message(f"Error refreshing tables: {str(e)}", "error")

    def refresh_table(self, table_type):
        """Refresh table data"""
        try:
            if not self.data_service:
                return
                
            tree = getattr(self, f"{table_type}_tree", None)
            if not tree:
                return
                
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            # Get fresh data using correct method names
            data_df = None
            if table_type == "employees":
                data_df = self.data_service.get_employees()
            elif table_type == "attendance":
                data_df = self.data_service.get_attendance()
            elif table_type == "stock":
                data_df = self.data_service.get_stock()
            elif table_type == "sales":
                data_df = self.data_service.get_sales()
            elif table_type == "purchases":
                data_df = self.data_service.get_purchases()
            
            # Convert DataFrame to list of dictionaries
            if data_df is not None and not data_df.empty:
                data = data_df.to_dict('records')
                
                # Populate table
                for record in data:
                    values = self.extract_table_values(record, table_type)
                    tree.insert("", "end", values=values)
                
        except Exception as e:
            logger.error(f"Error refreshing {table_type} table: {e}")
    
    def extract_table_values(self, record, table_type):
        """Extract values for table display"""
        if table_type == "employees":
            return [
                record.get("employee_id", ""),
                record.get("name", ""),
                record.get("email", ""),
                record.get("phone", ""),
                record.get("department", ""),
                record.get("position", ""),
                f"₹{record.get('salary', 0):,.2f}"
            ]
        elif table_type == "attendance":
            # Format date properly
            date_str = record.get("date", "")
            if hasattr(date_str, 'strftime'):
                date_str = date_str.strftime('%Y-%m-%d')
            elif isinstance(date_str, str) and len(date_str) > 10:
                # Handle datetime string format
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d')
                except:
                    pass
            
            hours = self.calculate_hours(record.get("time_in"), record.get("time_out"))
            return [
                record.get("employee_id", ""),
                date_str,
                record.get("time_in", ""),
                record.get("time_out", ""),
                record.get("status", ""),
                f"{hours:.1f}h"
            ]
        elif table_type == "stock":
            quantity = record.get("current_quantity", 0)
            price = record.get("unit_cost_average", 0)
            total = quantity * price
            return [
                record.get("item_name", ""),
                record.get("category", ""),
                str(quantity),
                f"₹{price:.2f}",
                record.get("supplier", ""),
                f"₹{total:.2f}"
            ]
        elif table_type == "sales":
            # Format date properly
            date_str = record.get("date", "")
            if hasattr(date_str, 'strftime'):
                date_str = date_str.strftime('%Y-%m-%d')
            elif isinstance(date_str, str) and len(date_str) > 10:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d')
                except:
                    pass
            
            quantity = record.get("quantity", 0)
            price = record.get("unit_price", 0)
            total = record.get("total_price", quantity * price)
            return [
                record.get("item_name", ""),
                str(quantity),
                f"₹{price:.2f}",
                record.get("customer_name", ""),
                date_str,
                f"₹{total:.2f}"
            ]
        elif table_type == "purchases":
            # Format date properly
            date_str = record.get("date", "")
            if hasattr(date_str, 'strftime'):
                date_str = date_str.strftime('%Y-%m-%d')
            elif isinstance(date_str, str) and len(date_str) > 10:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d')
                except:
                    pass
            
            quantity = record.get("quantity", 0)
            price = record.get("unit_price", 0)
            total = record.get("total_price", quantity * price)
            return [
                record.get("item_name", ""),
                str(quantity),
                f"₹{price:.2f}",
                record.get("supplier", ""),
                date_str,
                f"₹{total:.2f}"
            ]
        
        return []
    
    def calculate_hours(self, time_in, time_out):
        """Calculate working hours"""
        try:
            if not time_in or not time_out:
                return 0.0
            
            # Convert to string if not already
            time_in_str = str(time_in)
            time_out_str = str(time_out)
            
            time_in_obj = datetime.strptime(time_in_str, "%H:%M")
            time_out_obj = datetime.strptime(time_out_str, "%H:%M")
            
            if time_out_obj > time_in_obj:
                diff = time_out_obj - time_in_obj
                return diff.total_seconds() / 3600
            else:
                return 0.0
                
        except Exception as e:
            logger.debug(f"Error calculating hours for {time_in} to {time_out}: {e}")
            return 0.0
    
    def on_table_select(self, table_type, tree):
        """Handle table row selection"""
        try:
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                values = item['values']
                
                # Populate form with selected values
                var_dict = getattr(self, f"{table_type.rstrip('s')}_vars", {})
                
                if table_type == "employees" and var_dict:
                    var_dict["employee_id"].set(values[0])
                    var_dict["name"].set(values[1])
                    var_dict["email"].set(values[2])
                    var_dict["phone"].set(values[3])
                    var_dict["department"].set(values[4])
                    var_dict["position"].set(values[5])
                    # Remove currency formatting for salary
                    salary_str = str(values[6]).replace("₹", "").replace(",", "")
                    var_dict["salary"].set(salary_str)
                
                # Add similar logic for other table types
                
        except Exception as e:
            logger.error(f"Error in table selection: {e}")
    
    def show(self):
        """Show this page"""
        if self.frame:
            self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Hide this page"""
        if self.frame:
            self.frame.pack_forget()

# Alias for compatibility
DataPageGUI = ModernDataPageGUI
