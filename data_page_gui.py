"""
Enhanced Data Management GUI Page with Web-like Design
Modern interface that mimics the quality of the original web application
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from datetime import datetime, date
import re
import logging

logger = logging.getLogger(__name__)

class ModernDataPageGUI:
    def __init__(self, parent, data_service):
        self.parent = parent
        self.data_service = data_service
        self.frame = None
        
        # Navigation system
        self.navigation_stack = []
        self.current_view = 'main'
        self.main_frame = None
        self.content_frames = {}  # Store different content frames
        
        # Enhanced modern color scheme
        self.colors = {
            'primary': '#2563EB',      # Modern blue
            'primary_light': '#3B82F6', # Light blue
            'success': '#059669',      # Modern green  
            'success_light': '#10B981', # Light green
            'warning': '#D97706',      # Modern orange
            'warning_light': '#F59E0B', # Light orange
            'danger': '#DC2626',       # Modern red
            'danger_light': '#EF4444', # Light red
            'purple': '#7C3AED',       # Modern purple
            'purple_light': '#8B5CF6', # Light purple
            'gray': '#6B7280',         # Modern gray
            'gray_light': '#9CA3AF',   # Light gray
            'surface': '#F8FAFC',      # Surface
            'card': '#FFFFFF',         # Card background
            'border': '#E5E7EB',       # Border
            'text_primary': '#111827', # Primary text
            'text_secondary': '#6B7280', # Secondary text
            'button_uniform': '#2563EB', # Uniform button color (modern blue)
            'button_hover': '#1D4ED8',   # Uniform button hover color (darker blue)
            'title_green': '#059669'     # Green color for module titles
        }
        
        # Edit mode tracking
        self.edit_mode = False
        self.editing_employee_id = None
        self.editing_attendance_id = None
        self.editing_sale_id = None
        self.editing_purchase_id = None
        self.editing_stock_item = None
        self.edit_module_type = None
        
        # Module filtering - by default show all modules
        self.enabled_modules = ["employees", "attendance", "stock", "sales", "purchases"]
        
        self.create_page()
    
    def configure_modules(self, modules_list):
        """Configure which modules to show in this instance
        modules_list: list of module names to show ['employees', 'attendance'] or ['stock', 'sales', 'purchases']
        """
        self.enabled_modules = modules_list
        # Recreate the page with the filtered modules
        if hasattr(self, 'frame') and self.frame:
            self.frame.destroy()
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
    
    def validate_employee_data(self, data):
        """
        Comprehensive validation for employee data
        Returns (is_valid, error_message)
        """
        try:
            # Employee ID validation
            if not self.validate_employee_id(data.get("employee_id", "")):
                return False, "Employee ID must be in format: EMP001, HR001, IT001, etc. (3 letters + 3 digits)"
            
            # Name validation
            if not self.validate_name(data.get("name", "")):
                return False, "Name must be 2-50 characters, letters and spaces only"
            
            # Email validation
            if not self.validate_email(data.get("email", "")):
                return False, "Email must be valid format (e.g., user@company.com, .org, .in, .net allowed)"
            
            # Phone validation
            if not self.validate_phone(data.get("phone", "")):
                return False, "Phone must be 10 digits (e.g., 9876543210) or with country code (+91 9876543210)"
            
            # Salary validation
            if not self.validate_salary(data.get("salary", "")):
                return False, "Salary must be a positive number between 1,000 and 10,00,000"
            
            # Department and position validation
            if not data.get("department", "").strip():
                return False, "Please select a department"
            
            if not data.get("position", "").strip():
                return False, "Please select a position"
            
            return True, "Valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def validate_employee_id(self, emp_id):
        """Validate employee ID format: 3 letters + 3 digits (e.g., EMP001, HR001)"""
        if not emp_id or len(emp_id.strip()) == 0:
            return False
        
        # Pattern: 3 letters followed by 3 digits
        pattern = r'^[A-Z]{2,4}\d{3,4}$'
        return bool(re.match(pattern, emp_id.strip().upper()))
    
    def validate_name(self, name):
        """Validate employee name: 2-50 characters, letters and spaces only"""
        if not name or len(name.strip()) < 2:
            return False
        
        name = name.strip()
        if len(name) > 50:
            return False
        
        # Allow letters, spaces, apostrophes, hyphens
        pattern = r"^[A-Za-z\s\'\-\.]+$"
        return bool(re.match(pattern, name))
    
    def validate_email(self, email):
        """Validate email format with common domains"""
        if not email or len(email.strip()) == 0:
            return False
        
        email = email.strip().lower()
        
        # Basic email pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False
        
        # Check for valid domain extensions
        valid_domains = ['.com', '.org', '.net', '.edu', '.gov', '.in', '.co.in', '.ac.in', '.co.uk']
        return any(email.endswith(domain) for domain in valid_domains)
    
    def validate_phone(self, phone):
        """Validate phone number: 10 digits or with country code"""
        if not phone or len(phone.strip()) == 0:
            return False
        
        # Remove all non-digit characters except +
        phone_clean = re.sub(r'[^\d+]', '', phone.strip())
        
        # Case 1: 10 digits (Indian mobile)
        if len(phone_clean) == 10 and phone_clean.isdigit():
            # Should start with 6, 7, 8, or 9
            return phone_clean[0] in ['6', '7', '8', '9']
        
        # Case 2: With country code +91
        if phone_clean.startswith('+91') and len(phone_clean) == 13:
            mobile_part = phone_clean[3:]
            return mobile_part.isdigit() and mobile_part[0] in ['6', '7', '8', '9']
        
        # Case 3: Without + but with 91
        if phone_clean.startswith('91') and len(phone_clean) == 12:
            mobile_part = phone_clean[2:]
            return mobile_part.isdigit() and mobile_part[0] in ['6', '7', '8', '9']
        
        return False
    
    def validate_salary(self, salary):
        """Validate salary: positive number between 1,000 and 10,00,000"""
        if not salary:
            return False
        
        try:
            salary_val = float(str(salary).replace(',', ''))
            return 1000 <= salary_val <= 1000000
        except (ValueError, TypeError):
            return False
    
    def validate_field_realtime(self, field_key):
        """Real-time validation for individual fields"""
        if not hasattr(self, 'field_widgets') or field_key not in self.field_widgets:
            return
        
        if not hasattr(self, 'emp_vars') or field_key not in self.emp_vars:
            return
        
        value = self.emp_vars[field_key].get()
        error_label = self.field_widgets[field_key]['error_label']
        entry = self.field_widgets[field_key]['entry']
        
        # Clear previous error state
        self.clear_field_error(field_key)
        
        # Don't validate empty fields in real-time (will be caught during submit)
        if not value.strip():
            return
        
        # Validate based on field type
        is_valid = True
        error_msg = ""
        
        if field_key == "employee_id":
            if not self.validate_employee_id(value):
                is_valid = False
                error_msg = "Format: 3-4 letters + 3-4 digits (e.g., EMP001)"
        elif field_key == "name":
            if not self.validate_name(value):
                is_valid = False
                error_msg = "2-50 characters, letters and spaces only"
        elif field_key == "email":
            if not self.validate_email(value):
                is_valid = False
                error_msg = "Valid email with .com/.org/.net/.in domain required"
        elif field_key == "phone":
            if not self.validate_phone(value):
                is_valid = False
                error_msg = "10 digits starting with 6,7,8,9 or +91 format"
        elif field_key == "salary":
            if not self.validate_salary(value):
                is_valid = False
                error_msg = "Amount between ₹1,000 and ₹10,00,000"
        
        # Show error if validation failed
        if not is_valid:
            self.show_field_error(field_key, error_msg)
    
    def show_field_error(self, field_key, error_msg):
        """Show error message under a specific field"""
        try:
            if not hasattr(self, 'field_widgets') or field_key not in self.field_widgets:
                return
            
            widgets = self.field_widgets[field_key]
            if 'error_label' not in widgets or 'entry' not in widgets:
                return
                
            error_label = widgets['error_label']
            entry = widgets['entry']
            
            # Update error message and show
            error_label.configure(text=f"❌ {error_msg}")
            error_label.pack(anchor="w", pady=(2, 0))
            
            # Change entry border color to red (if supported)
            try:
                entry.configure(border_color="red")
            except:
                pass
        except Exception as e:
            # Don't raise the exception, just log it
            pass
    
    def clear_field_error(self, field_key):
        """Clear error message for a specific field"""
        try:
            if not hasattr(self, 'field_widgets') or field_key not in self.field_widgets:
                return
            
            widgets = self.field_widgets[field_key]
            if 'error_label' not in widgets or 'entry' not in widgets:
                return
                
            error_label = widgets['error_label']
            entry = widgets['entry']
            
            # Hide error label
            error_label.pack_forget()
            
            # Reset entry border color
            try:
                entry.configure(border_color=("gray80", "gray20"))
            except:
                pass
        except Exception as e:
            # Don't raise the exception, just log it
            pass
    
    def clear_all_field_errors(self):
        """Clear all field errors"""
        if not hasattr(self, 'field_widgets'):
            return
        
        for field_key in self.field_widgets.keys():
            self.clear_field_error(field_key)
    
    def validate_employee_data_with_feedback(self, data):
        """
        Enhanced validation with field-specific error feedback
        Returns (is_valid, error_message)
        """
        try:
            self.clear_all_field_errors()
            is_valid = True
            error_fields = []
            
            # Employee ID validation
            emp_id_valid = self.validate_employee_id(data.get("employee_id", ""))
            if not emp_id_valid:
                self.show_field_error("employee_id", "Format: 3-4 letters + 3-4 digits (e.g., EMP001)")
                is_valid = False
                error_fields.append("Employee ID")
            
            # Name validation
            name_valid = self.validate_name(data.get("name", ""))
            if not name_valid:
                self.show_field_error("name", "2-50 characters, letters and spaces only")
                is_valid = False
                error_fields.append("Name")
            
            # Email validation
            email_valid = self.validate_email(data.get("email", ""))
            if not email_valid:
                self.show_field_error("email", "Valid email with .com/.org/.net/.in domain required")
                is_valid = False
                error_fields.append("Email")
            
            # Phone validation
            phone_valid = self.validate_phone(data.get("phone", ""))
            if not phone_valid:
                self.show_field_error("phone", "10 digits starting with 6,7,8,9 or +91 format")
                is_valid = False
                error_fields.append("Phone")
            
            # Salary validation
            salary_valid = self.validate_salary(data.get("salary", ""))
            if not salary_valid:
                self.show_field_error("salary", "Amount between ₹1,000 and ₹10,00,000")
                is_valid = False
                error_fields.append("Salary")
            
            # Department and position validation (no field-level errors for dropdowns)
            dept_valid = bool(data.get("department", "").strip())
            if not dept_valid:
                is_valid = False
                error_fields.append("Department")
            
            pos_valid = bool(data.get("position", "").strip())
            if not pos_valid:
                is_valid = False
                error_fields.append("Position")
            
            if is_valid:
                return True, "Valid"
            else:
                return False, f"Please fix errors in: {', '.join(error_fields)}"
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Validation error: {str(e)}"

    def show_validation_summary(self):
        """Show a summary of validation rules to help users"""
        validation_info = """
📋 Employee Data Validation Rules:

🆔 Employee ID:
   • Format: 3-4 letters + 3-4 digits (e.g., EMP001, HR001, IT123)
   • Case insensitive (emp001 = EMP001)

👤 Full Name:
   • 2-50 characters long
   • Letters, spaces, apostrophes, hyphens allowed
   • No numbers or special characters

📧 Email Address:
   • Valid email format (user@domain.extension)
   • Allowed domains: .com, .org, .net, .edu, .gov, .in, .co.in, .ac.in, .co.uk

📱 Phone Number:
   • 10 digits: 9876543210 (must start with 6, 7, 8, or 9)
   • With country code: +91 9876543210 or 919876543210

💰 Salary:
   • Range: ₹1,000 to ₹10,00,000
   • Numbers only (commas will be removed automatically)

🏢 Department & Position:
   • Must be selected from dropdown options
        """
        
        # Create info popup
        info_window = ctk.CTkToplevel(self.parent)
        info_window.title("Validation Rules")
        info_window.geometry("600x500")
        info_window.transient(self.parent)
        info_window.grab_set()
        
        # Center the window
        info_window.update_idletasks()
        x = (info_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (info_window.winfo_screenheight() // 2) - (500 // 2)
        info_window.geometry(f"600x500+{x}+{y}")
        
        # Content
        content_frame = ctk.CTkScrollableFrame(info_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_label = ctk.CTkLabel(
            content_frame,
            text=validation_info,
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="nw"
        )
        info_label.pack(fill="both", expand=True)
        
        # Close button
        close_btn = ctk.CTkButton(
            info_window,
            text="Got it!",
            command=info_window.destroy,
            width=100,
            height=35
        )
        close_btn.pack(pady=10)
        
    def create_page(self):
        """Create the enhanced data management page with navigation support"""
        # Main frame with modern styling
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color="transparent")
        
        # Create navigation header (will show breadcrumbs and back button when in sub-views)
        self.create_navigation_header()
        
        # Create header section (always visible)
        self.create_header()
        
        # Create main content container that will hold different views
        self.main_container = ctk.CTkFrame(self.frame, corner_radius=0, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create main dashboard view
        self.create_main_dashboard()
        
        # Create status bar at bottom
        self.create_status_bar()
        
    def create_navigation_header(self):
        """Create navigation header with breadcrumbs and back button"""
        self.nav_frame = ctk.CTkFrame(
            self.frame, 
            height=60, 
            corner_radius=0,
            fg_color="transparent"
        )
        self.nav_frame.pack(fill="x", padx=0, pady=0)
        self.nav_frame.pack_propagate(False)
        
        # Initially hidden, will be shown when navigating to sub-views
        self.nav_frame.pack_forget()
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.nav_frame,
            text="← Back",
            command=self.navigate_back,
            width=100,
            height=35,
            fg_color=self.colors['button_uniform'],
            hover_color=self.colors['button_hover'],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.back_button.pack(side="left", padx=20, pady=15)
        
        # Breadcrumb
        self.breadcrumb_label = ctk.CTkLabel(
            self.nav_frame,
            text="Data Management",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.breadcrumb_label.pack(side="left", padx=(10, 0), pady=15)
        
    def create_main_dashboard(self):
        """Create the main dashboard view (grid of modules)"""
        # Create main dashboard frame
        self.main_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        
        # Create main content area with cards (no header here since it's already created)
        self.create_main_content()

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
        
    def navigate_to(self, view_name, title):
        """Navigate to a specific view"""
        # Add current view to navigation stack
        self.navigation_stack.append(self.current_view)
        self.current_view = view_name
        
        # Hide main frame
        self.main_frame.pack_forget()
        
        # Show navigation header
        self.nav_frame.pack(fill="x", padx=0, pady=0, before=self.main_container)
        
        # Update breadcrumb
        self.breadcrumb_label.configure(text=f"Data Management > {title}")
        
        # Show the specific module frame
        if view_name not in self.content_frames:
            self.create_module_frame(view_name, title)
        
        self.content_frames[view_name].pack(fill="both", expand=True)
        
    def navigate_back(self):
        """Navigate back to previous view"""
        if not self.navigation_stack:
            return
            
        # Hide current frame
        if self.current_view in self.content_frames:
            self.content_frames[self.current_view].pack_forget()
        
        # Get previous view
        previous_view = self.navigation_stack.pop()
        self.current_view = previous_view
        
        if previous_view == 'main':
            # Return to main dashboard
            self.nav_frame.pack_forget()
            self.main_frame.pack(fill="both", expand=True)
        else:
            # Navigate to previous sub-view (if any)
            self.content_frames[previous_view].pack(fill="both", expand=True)
        
    def create_module_frame(self, module_type, title):
        """Create a frame for a specific module"""
        module_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        
        # Create the module content based on type
        if module_type == "employees":
            self.create_employee_management_content(module_frame)
        elif module_type == "attendance":
            self.create_attendance_management_content(module_frame)
        elif module_type == "sales":
            self.create_sales_management_content(module_frame)
        elif module_type == "purchases":
            self.create_purchase_management_content(module_frame)
        elif module_type == "stock":
            self.create_stock_management_content(module_frame)
            
        self.content_frames[module_type] = module_frame
        
    def create_header(self):
        """Create modern header section with enhanced styling"""
        header_frame = ctk.CTkFrame(
            self.frame, 
            height=100, 
            corner_radius=20,
            fg_color=("white", "gray20"),
            border_width=1,
            border_color=self.colors['border']
        )
        header_frame.pack(fill="x", padx=25, pady=(25, 15))
        header_frame.pack_propagate(False)
        
        # Left side - Title and subtitle with modern typography
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left", fill="y", padx=30, pady=20)
        
        # Main title with gradient-like effect
        title_label = ctk.CTkLabel(
            title_container,
            text="📊 Data Management Center",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.pack(anchor="w")
        
        # Subtitle with modern styling
        subtitle_label = ctk.CTkLabel(
            title_container,
            text="Comprehensive business data management and analytics platform",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Right side - Modern quick stats with better layout
        stats_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_container.pack(side="right", fill="y", padx=30, pady=15)
        
        self.create_quick_stats(stats_container)
        
    def create_quick_stats(self, parent):
        """Create modern statistics cards with enhanced design"""
        try:
            if not self.data_service:
                return
                
            # Get quick stats using the correct method names
            employees_df = self.data_service.get_employees()
            stock_df = self.data_service.get_stock()
            
            employees_count = len(employees_df) if not employees_df.empty else 0
            stock_count = len(stock_df) if not stock_df.empty else 0
            
            # Modern stat cards with improved design
            stats = [
                ("👥", str(employees_count), "Employees", self.colors['primary']),
                ("📦", str(stock_count), "Stock Items", self.colors['success'])
            ]
            
            for i, (icon, count, label, color) in enumerate(stats):
                # Modern stat card with shadow effect
                stat_card = ctk.CTkFrame(
                    parent, 
                    width=140, 
                    height=65, 
                    corner_radius=15,
                    fg_color=("white", "gray25"),
                    border_width=1,
                    border_color=self.colors['border']
                )
                stat_card.pack(side="left", padx=8)
                stat_card.pack_propagate(False)
                
                # Content container
                content_frame = ctk.CTkFrame(stat_card, fg_color="transparent")
                content_frame.pack(expand=True, fill="both", padx=15, pady=12)
                
                # Icon and count on top
                top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                top_frame.pack(fill="x")
                
                icon_label = ctk.CTkLabel(
                    top_frame,
                    text=icon,
                    font=ctk.CTkFont(size=16)
                )
                icon_label.pack(side="left")
                
                count_label = ctk.CTkLabel(
                    top_frame, 
                    text=count,
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=color
                )
                count_label.pack(side="right")
                
                # Label at bottom
                label_widget = ctk.CTkLabel(
                    content_frame,
                    text=label,
                    font=ctk.CTkFont(size=11),
                    text_color=self.colors['text_secondary']
                )
                label_widget.pack(anchor="w", pady=(3, 0))
                
        except Exception as e:
            logger.error(f"Error creating quick stats: {e}")
    
    def create_main_content(self):
        """Create main content area with modern grid layout"""
        # Main container for grid layout
        main_container = ctk.CTkFrame(
            self.main_frame,
            corner_radius=15,
            fg_color=("gray95", "gray10"),
            border_width=1,
            border_color=self.colors['border']
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title for modules section
        modules_title = ctk.CTkLabel(
            main_container,
            text="📋 Data Management Modules",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors['primary']
        )
        modules_title.pack(pady=(20, 10))
        
        # Subtitle
        modules_subtitle = ctk.CTkLabel(
            main_container,
            text="Select a module to start managing your business data",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        modules_subtitle.pack(pady=(0, 20))
        
        # Create module cards in grid
        self.create_module_cards(main_container)
        
    def create_module_cards(self, parent):
        """Create modern cards for each module in a grid layout"""
        all_modules = [
            {
                "title": "👥 Employee Management",
                "description": "Manage employee records, positions, and contact information",
                "color": self.colors['primary'],
                "action": self.open_employee_module,
                "key": "employees"
            },
            {
                "title": "📅 Attendance Tracking", 
                "description": "Record and monitor daily attendance and working hours",
                "color": self.colors['success'],
                "action": self.open_attendance_module,
                "key": "attendance"
            },
            {
                "title": "📦 Inventory Management",
                "description": "Control stock levels, suppliers, and product categories",
                "color": self.colors['warning'],
                "action": self.open_stock_module,
                "key": "stock"
            },
            {
                "title": "💰 Sales Records",
                "description": "Track sales transactions and customer information",
                "color": self.colors['success'],
                "action": self.open_sales_module,
                "key": "sales"
            },
            {
                "title": "🛒 Purchase Management",
                "description": "Manage purchase orders and supplier transactions",
                "color": self.colors['danger'],
                "action": self.open_purchases_module,
                "key": "purchases"
            }
        ]
        
        # Filter modules based on enabled_modules
        modules = [module for module in all_modules if module["key"] in self.enabled_modules]
        
        # Create grid layout container
        grid_container = ctk.CTkFrame(parent, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=10, pady=20)
        
        # Create cards in a proper 2-column grid layout
        for i, module in enumerate(modules):
            row = i // 2  # 0, 0, 1, 1, 2
            col = i % 2   # 0, 1, 0, 1, 0
            self.create_grid_module_card(grid_container, module, row, col)
    
    def create_grid_module_card(self, parent, module, row, col):
        """Create individual module card in grid layout"""
        # Calculate position and configure grid with consistent sizing
        parent.grid_rowconfigure(row, weight=1, minsize=180)
        parent.grid_columnconfigure(col, weight=1, minsize=400)
        
        # Card frame with consistent design for all cards
        card_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            height=160,
            fg_color=("white", "gray20"),
            border_width=1,
            border_color=self.colors['border']
        )
        card_frame.grid(row=row, column=col, padx=15, pady=10, sticky="ew")
        card_frame.grid_propagate(False)
        
        # Main content container
        content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Header section (icon and title)
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent", height=50)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Extract icon and title parts
        title_parts = module["title"].split(" ", 1)
        icon = title_parts[0] if len(title_parts) > 0 else "📊"
        title_text = title_parts[1] if len(title_parts) > 1 else module["title"]
        
        # Icon
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=ctk.CTkFont(size=24),
            width=40
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
            text_color=self.colors['title_green']  # Green color for all titles
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Description (compact)
        desc_label = ctk.CTkLabel(
            content_frame,
            text=module["description"],
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
            wraplength=300,
            text_color=self.colors['text_secondary']
        )
        desc_label.pack(fill="x", pady=(0, 15))
        
        # Action button (compact) - uniform professional color
        action_btn = ctk.CTkButton(
            content_frame,
            text=f"Open {title_text}",
            command=module["action"],
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors['button_uniform'],
            hover_color=self.colors['button_hover'],
            text_color="white"
        )
        action_btn.pack(fill="x", side="bottom")
        
    def darken_color(self, color):
        """Darken a hex color for hover effect"""
        # Simple color darkening - remove # and convert
        color = color.lstrip('#')
        # Convert to RGB, darken by 20%, convert back
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    # Module navigation methods
    def open_employee_module(self):
        """Navigate to employee management module"""
        self.navigate_to("employees", "Employee Management")
        
    def open_attendance_module(self):
        """Navigate to attendance tracking module"""
        self.navigate_to("attendance", "Attendance Tracking")
        
    def open_stock_module(self):
        """Navigate to stock management module"""
        self.navigate_to("stock", "Stock Management")
        
    def open_sales_module(self):
        """Navigate to sales management module"""
        self.navigate_to("sales", "Sales Management")
        
    def open_purchases_module(self):
        """Navigate to purchase management module"""
        self.navigate_to("purchases", "Purchase Management")
    # Module content creation methods
    def create_employee_management_content(self, parent):
        """Create employee management content in the frame"""
        self.create_module_content(parent, "Employee Management", "employees")
        
    def create_attendance_management_content(self, parent):
        """Create attendance management content in the frame"""
        self.create_module_content(parent, "Attendance Tracking", "attendance")
        
    def create_sales_management_content(self, parent):
        """Create sales management content in the frame"""
        self.create_module_content(parent, "Sales Management", "sales")
        
    def create_purchase_management_content(self, parent):
        """Create purchase management content in the frame"""
        self.create_module_content(parent, "Purchase Management", "purchases")
        
    def create_stock_management_content(self, parent):
        """Create stock management content in the frame"""
        self.create_module_content(parent, "Stock Management", "stock")
        
    def create_module_content(self, parent, title, module_type):
        """Create module content within a frame (adapted from window version)"""
        # Module header
        header_frame = ctk.CTkFrame(parent, height=80, corner_radius=15)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"📋 {title}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # Main content area
        content_frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
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
    
    def create_form_section(self, parent, title):
        """Create a form section header"""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        section_frame.pack(fill="x", pady=(20, 10))
        section_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['primary']
        ).pack(anchor="w", pady=10)
        
        # Divider line
        divider = ctk.CTkFrame(section_frame, height=1, fg_color=("gray80", "gray30"))
        divider.pack(fill="x", pady=(5, 0))

    def create_enhanced_field(self, parent, label, key, field_type, vars_dict, placeholder="", required=True):
        """Create enhanced form field with modern styling"""
        field_container = ctk.CTkFrame(
            parent, 
            fg_color=("white", "gray20"),
            corner_radius=10,
            border_width=1,
            border_color=("gray90", "gray30")
        )
        field_container.pack(fill="x", pady=8, padx=5)
        
        field_frame = ctk.CTkFrame(field_container, fg_color="transparent")
        field_frame.pack(fill="x", padx=15, pady=12)
        
        # Label with required indicator
        required_indicator = " *" if required else ""
        label_widget = ctk.CTkLabel(
            field_frame,
            text=f"{label}{required_indicator}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray10", "gray90")
        )
        label_widget.pack(anchor="w", pady=(0, 6))
        
        # Input field
        vars_dict[key] = tk.StringVar()
        
        if field_type == "email":
            entry = ctk.CTkEntry(
                field_frame,
                textvariable=vars_dict[key],
                placeholder_text=placeholder,
                height=38,
                corner_radius=8,
                border_width=1,
                font=ctk.CTkFont(size=12)
            )
        else:
            entry = ctk.CTkEntry(
                field_frame,
                textvariable=vars_dict[key],
                placeholder_text=placeholder,
                height=38,
                corner_radius=8,
                border_width=1,
                font=ctk.CTkFont(size=12)
            )
        
        entry.pack(fill="x", pady=(0, 3))
        
        # Helper text
        if placeholder and field_type != "text":
            helper_text = ctk.CTkLabel(
                field_frame,
                text=f"Format: {placeholder}",
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray50")
            )
            helper_text.pack(anchor="w")
        
        return entry

    def create_enhanced_combo(self, parent, label, key, options, vars_dict, required=True):
        """Create enhanced combo box with modern styling"""
        field_container = ctk.CTkFrame(
            parent, 
            fg_color=("white", "gray20"),
            corner_radius=10,
            border_width=1,
            border_color=("gray90", "gray30")
        )
        field_container.pack(fill="x", pady=8, padx=5)
        
        field_frame = ctk.CTkFrame(field_container, fg_color="transparent")
        field_frame.pack(fill="x", padx=15, pady=12)
        
        # Label
        required_indicator = " *" if required else ""
        label_widget = ctk.CTkLabel(
            field_frame,
            text=f"{label}{required_indicator}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray10", "gray90")
        )
        label_widget.pack(anchor="w", pady=(0, 6))
        
        # Combo box
        vars_dict[key] = tk.StringVar(value=options[0] if options else "")
        combo = ctk.CTkComboBox(
            field_frame,
            values=options,
            variable=vars_dict[key],
            height=38,
            corner_radius=8,
            border_width=1,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=11)
        )
        combo.pack(fill="x")
        
        return combo

    def create_enhanced_form_buttons(self, parent, module_type):
        """Create enhanced form buttons with modern styling"""
        button_container = ctk.CTkFrame(parent, fg_color="transparent", height=80)
        button_container.pack(fill="x", pady=(30, 20))
        button_container.pack_propagate(False)
        
        button_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        button_frame.pack(expand=True)
        
        # Submit button
        submit_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Record",
            command=lambda: self.add_record(module_type),
            width=140,
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            hover_color=self.darken_color(self.colors['success'])
        )
        submit_btn.pack(side="left", padx=(0, 15))
        
        # Store button reference for dynamic text updates
        setattr(self, f'{module_type}_add_btn', submit_btn)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear Form",
            command=lambda: self.clear_form(module_type),
            width=140,
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['warning'],
            hover_color=self.darken_color(self.colors['warning'])
        )
        clear_btn.pack(side="left")

    def create_enhanced_data_table(self, parent, module_type):
        """Create enhanced data table with modern styling"""
        # Table header
        table_header = ctk.CTkFrame(
            parent, 
            height=60, 
            corner_radius=12,
            fg_color=self.colors['primary']
        )
        table_header.pack(fill="x", padx=15, pady=(15, 10))
        table_header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(table_header, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20, pady=15)
        
        ctk.CTkLabel(
            header_content,
            text=f"📊 {module_type.title()} Records",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_content,
            text="🔄 Refresh",
            command=lambda: self.refresh_table(module_type),
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="white",
            text_color=self.colors['primary'],
            hover_color="gray90"
        )
        refresh_btn.pack(side="right")
        
        # Table frame
        table_frame = ctk.CTkFrame(parent, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create the actual table
        self.create_data_table_content(table_frame, module_type)

    def create_data_table_content(self, parent, module_type):
        """Create the actual data table content"""
        # This will call the existing create_data_table method
        self.create_data_table(parent, module_type)

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
        
        # Scrollable form area with improved scroll speed
        form_scroll = ctk.CTkScrollableFrame(form_panel)
        form_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Configure improved scroll speed
        self.configure_scroll_speed(form_scroll)
        
        # Form fields with enhanced controls
        self.emp_vars = {}
        
        # Basic info fields with validation hints
        self.create_form_field(form_scroll, "Employee ID", "employee_id", "text", self.emp_vars,
                              placeholder="e.g., EMP001, HR001, IT001 (3-4 letters + 3-4 digits)")
        self.create_form_field(form_scroll, "Full Name", "name", "text", self.emp_vars,
                              placeholder="Enter full name (2-50 characters, letters only)")
        self.create_form_field(form_scroll, "Email Address", "email", "text", self.emp_vars,
                              placeholder="employee@company.com (.com/.org/.net/.in allowed)")
        self.create_form_field(form_scroll, "Phone Number", "phone", "text", self.emp_vars,
                              placeholder="9876543210 or +91 9876543210 (10 digits)")
        
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
        
        # Salary field with validation hint
        self.create_form_field(form_scroll, "Monthly Salary (₹)", "salary", "number", self.emp_vars,
                              placeholder="50000 (Range: 1,000 - 10,00,000)")
        
        # Join date
        self.create_date_picker(form_scroll, "Join Date", "join_date", self.emp_vars)
        
        # Form buttons
        self.create_form_buttons(form_scroll, "employees")
        
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
        
        # Configure improved scroll speed
        self.configure_scroll_speed(form_scroll)
        
        # Form fields with simplified layout
        self.att_vars = {}
        
        # Employee selection dropdown
        self.create_employee_dropdown(form_scroll, "Employee", "employee_id", self.att_vars)
        
        # Date picker
        self.create_date_picker(form_scroll, "Date", "date", self.att_vars)
        
        # Time pickers with improved layout (store references for dynamic control)
        self.time_in_widgets = self.create_time_picker(form_scroll, "Time In", "time_in", self.att_vars)
        self.time_out_widgets = self.create_time_picker(form_scroll, "Time Out", "time_out", self.att_vars)
        
        # Status dropdown with all valid options from reports
        self.create_attendance_status_dropdown(form_scroll, "Status", "status", 
                               ["Present", "Absent", "Late", "Half Day", "Leave", "Overtime", "Remote Work"], self.att_vars)
        
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
        
        # Store widget references for edit mode control
        if not hasattr(self, 'field_widgets'):
            self.field_widgets = {}
        if not hasattr(self, 'employee_field_widgets'):
            self.employee_field_widgets = {}
            
        widget_info = {
            'date_entry': date_entry,
            'today_btn': today_btn,
            'field_frame': field_frame,
            'type': 'date'
        }
        self.field_widgets[key] = widget_info
        
        # If this is an employee field, also store in employee-specific dict
        if hasattr(self, 'emp_vars') and key in self.emp_vars:
            self.employee_field_widgets[key] = widget_info
        
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
        
        # Return widgets for potential disabling
        return {
            'hour_combo': hour_combo,
            'minute_combo': minute_combo,
            'quick_buttons': buttons_frame
        }

    def create_attendance_status_dropdown(self, parent, label, key, options, vars_dict):
        """Create attendance status dropdown with time field control"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)

        # Label
        label_widget = ctk.CTkLabel(
            field_frame,
            text=f"{label}*",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_widget.pack(anchor="w", pady=(0, 5))

        # Dropdown
        vars_dict[key] = tk.StringVar()
        dropdown = ctk.CTkComboBox(
            field_frame,
            variable=vars_dict[key],
            values=options,
            width=300,
            height=35,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=12),
            command=self.on_status_change
        )
        dropdown.pack(fill="x", pady=(0, 5))

        # Helper text
        helper_text = ctk.CTkLabel(
            field_frame,
            text="Select attendance status",
            font=ctk.CTkFont(size=10)
        )
        helper_text.pack(anchor="w")

    def on_status_change(self, status):
        """Handle status change to enable/disable time fields"""
        try:
            if hasattr(self, 'time_in_widgets') and hasattr(self, 'time_out_widgets'):
                is_absent_or_leave = status.lower() in ["absent", "leave"]
                
                # Disable/enable time input widgets
                for widget_dict in [self.time_in_widgets, self.time_out_widgets]:
                    if widget_dict:
                        widget_dict['hour_combo'].configure(state="disabled" if is_absent_or_leave else "normal")
                        widget_dict['minute_combo'].configure(state="disabled" if is_absent_or_leave else "normal")
                        
                        # Disable quick buttons
                        for child in widget_dict['quick_buttons'].winfo_children():
                            if isinstance(child, ctk.CTkButton):
                                child.configure(state="disabled" if is_absent_or_leave else "normal")
                
                # Set default values for absent/leave
                if is_absent_or_leave:
                    if 'time_in' in self.att_vars:
                        self.att_vars['time_in'].set("--:--")
                    if 'time_out' in self.att_vars:
                        self.att_vars['time_out'].set("--:--")
        except Exception as e:
            logger.error(f"Error handling status change: {e}")
    
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
        
        # Configure improved scroll speed
        self.configure_scroll_speed(form_scroll)
        
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
        
        # Configure improved scroll speed
        self.configure_scroll_speed(form_scroll)
        
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
        
        # Configure improved scroll speed
        self.configure_scroll_speed(form_scroll)
        
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
        """Create a modern form field with validation error display"""
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
        
        # Error label (initially hidden)
        error_label = ctk.CTkLabel(
            field_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="red",
            anchor="w"
        )
        error_label.pack(anchor="w", pady=(2, 0))
        error_label.pack_forget()  # Initially hidden
        
        # Store references for validation feedback and edit mode control
        if not hasattr(self, 'field_widgets'):
            self.field_widgets = {}
        if not hasattr(self, 'employee_field_widgets'):
            self.employee_field_widgets = {}
            
        # Store in both general and employee-specific widgets for easy access
        widget_info = {
            'entry': entry,
            'error_label': error_label,
            'field_frame': field_frame,
            'type': 'entry'
        }
        self.field_widgets[key] = widget_info
        
        # If this is an employee field, also store in employee-specific dict
        if hasattr(self, 'emp_vars') and key in self.emp_vars:
            self.employee_field_widgets[key] = widget_info
        
        # Add real-time validation for employees
        if hasattr(self, 'emp_vars') and key in ['employee_id', 'name', 'email', 'phone', 'salary']:
            var_dict[key].trace('w', lambda *args, k=key: self.validate_field_realtime(k))
        
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
        
        # Store widget references for edit mode control
        if not hasattr(self, 'field_widgets'):
            self.field_widgets = {}
        if not hasattr(self, 'employee_field_widgets'):
            self.employee_field_widgets = {}
            
        widget_info = {
            'combo': combo,
            'field_frame': field_frame,
            'type': 'combo'
        }
        self.field_widgets[key] = widget_info
        
        # If this is an employee field, also store in employee-specific dict
        if hasattr(self, 'emp_vars') and key in self.emp_vars:
            self.employee_field_widgets[key] = widget_info
        
        return combo
    
    def create_form_buttons(self, parent, module_type):
        """Create modern form buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        # Add button (stores reference for dynamic text updates)
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
        
        # Store reference to add button for dynamic text updates
        setattr(self, f'{module_type}_add_btn', add_btn)
        
        # Edit/Update button - now functional for all modules
        edit_btn = ctk.CTkButton(
            button_frame,
            text=f"✏️ Edit {module_type.title()[:-1] if module_type.endswith('s') else module_type.title()}",
            command=lambda: self.edit_record(module_type),
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary'])
        )
        edit_btn.pack(fill="x", pady=2)
        
        # Update button (shown only in edit mode)
        update_text = f"💾 Update {module_type.title()[:-1] if module_type.endswith('s') else module_type.title()}"
        setattr(self, f'{module_type}_update_btn', ctk.CTkButton(
            button_frame,
            text=update_text,
            command=lambda: self.update_record(module_type),
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['warning'],
            hover_color=self.darken_color(self.colors['warning'])
        ))
        # Initially hidden
        
        # Cancel edit button (shown only in edit mode)
        setattr(self, f'{module_type}_cancel_edit_btn', ctk.CTkButton(
            button_frame,
            text="❌ Cancel Edit",
            command=lambda: self.cancel_edit_record(module_type),
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['gray'],
            hover_color=self.darken_color(self.colors['gray'])
        ))
        # Initially hidden
        
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
        
        # Validation help button - only for employees
        if module_type == "employees":
            help_btn = ctk.CTkButton(
                button_frame,
                text="❓ Validation Rules",
                command=self.show_validation_summary,
                height=40,
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.colors['purple'],
                hover_color=self.darken_color(self.colors['purple'])
            )
            help_btn.pack(fill="x", pady=2)
    
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
        """Add new record with proper data conversion or update if in edit mode"""
        try:
            if not self.data_service:
                self.show_status_message("Database not connected", "error")
                return
            
            # Check if we're in edit mode for this module
            if self.edit_mode and self.edit_module_type == module_type:
                # If in edit mode, call the update method instead
                self.update_record(module_type)
                return
            
            if module_type == "employees":
                data = {key: var.get().strip() for key, var in self.emp_vars.items()}
                
                # Validate employee data with field-specific feedback
                is_valid, error_message = self.validate_employee_data_with_feedback(data)
                if not is_valid:
                    self.show_status_message(f"Validation Error: {error_message}", "error")
                    return
                
                # Convert salary to float after validation
                if data.get("salary"):
                    data["salary"] = float(data["salary"])
                # Add joining date as datetime
                if data.get("join_date"):
                    data["hire_date"] = datetime.strptime(data["join_date"], "%Y-%m-%d")
                    del data["join_date"]  # Remove old key
                
                result = self.data_service.add_employee(data)
                
            elif module_type == "attendance":
                data = {key: var.get().strip() for key, var in self.att_vars.items()}
                # Convert date string to datetime object
                if data.get("date"):
                    data["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
                
                # Extract employee_id from dropdown (format: "EMP001 - John Doe")
                emp_selection = data.get("employee_id", "")
                if " - " in emp_selection:
                    emp_id = emp_selection.split(" - ")[0].strip()
                    data["employee_id"] = emp_id
                    # Get employee name
                    employees = self.data_service.get_employees({"employee_id": emp_id})
                    if not employees.empty:
                        data["employee_name"] = employees.iloc[0]["name"]
                else:
                    raise ValueError("Please select a valid employee")
                
                # Handle time fields based on status
                status = data.get("status", "").lower()
                if status in ["absent", "leave"]:
                    # For absent/leave, set meaningful default times or empty
                    data["time_in"] = ""
                    data["time_out"] = ""
                else:
                    # For other statuses, ensure times are provided
                    if not data.get("time_in") or data.get("time_in") == "--:--":
                        data["time_in"] = "09:00"
                    if not data.get("time_out") or data.get("time_out") == "--:--":
                        data["time_out"] = "17:00"
                
                result = self.data_service.add_attendance(data)
                
            elif module_type == "stock":
                data = {key: var.get().strip() for key, var in self.stock_vars.items()}
                if data.get("quantity"):
                    data["current_quantity"] = int(data["quantity"])
                    del data["quantity"]  # Remove old key
                if data.get("price_per_unit"):
                    data["unit_price"] = float(data["price_per_unit"])
                    del data["price_per_unit"]  # Remove old key
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
    
    def edit_employee(self):
        """Edit selected employee details"""
        try:
            # Get selected employee from the table
            if not hasattr(self, 'employees_tree'):
                self.show_status_message("Employee table not found", "error")
                return
                
            selected_items = self.employees_tree.selection()
            if not selected_items:
                self.show_status_message("Please select an employee to edit", "warning")
                return
                
            if len(selected_items) > 1:
                self.show_status_message("Please select only one employee to edit", "warning")
                return
            
            # Get employee data from selection
            item = self.employees_tree.item(selected_items[0])
            values = item['values']
            
            if not values:
                self.show_status_message("Invalid employee selection", "error")
                return
            
            employee_id = str(values[0])  # Ensure it's a string
            
            # Populate form with current employee data
            if hasattr(self, 'emp_vars'):
                self.emp_vars["employee_id"].set(values[0])  # Employee ID
                self.emp_vars["name"].set(values[1])          # Name
                self.emp_vars["email"].set(values[2])         # Email
                self.emp_vars["phone"].set(values[3])         # Phone
                self.emp_vars["department"].set(values[4])    # Department
                self.emp_vars["position"].set(values[5])      # Position
                # Remove currency formatting for salary
                salary_str = str(values[6]).replace("₹", "").replace(",", "")
                self.emp_vars["salary"].set(salary_str)
                
                # Enable editing mode
                self.edit_mode = True
                self.editing_employee_id = employee_id  # This is now guaranteed to be a string
                
                # Show update and cancel buttons, hide edit button
                if hasattr(self, 'update_btn'):
                    self.update_btn.pack(fill="x", pady=2)
                if hasattr(self, 'cancel_edit_btn'):
                    self.cancel_edit_btn.pack(fill="x", pady=2)
                
                self.show_status_message(f"Editing employee: {values[1]} ({employee_id}). Modify fields and click 'Update Employee'.", "info")
                
                # Create update button if it doesn't exist
                self.create_update_employee_button()
            else:
                self.show_status_message("Employee form not found", "error")
                
        except Exception as e:
            self.show_status_message(f"Failed to load employee for editing: {str(e)}", "error")
    
    def create_update_employee_button(self):
        """Create or show the update employee button"""
        try:
            # Store update button reference for easier management
            if not hasattr(self, 'employee_update_button'):
                # We'll create the button dynamically when needed
                # For now, just show a message to the user
                self.show_status_message("Employee loaded for editing. Modify the fields and click 'Add Record' to update, or use the form buttons.", "info")
        except Exception as e:
            print(f"Error with update button: {e}")

    def cancel_edit_employee(self):
        """Cancel employee editing mode"""
        try:
            # Reset edit mode
            self.edit_mode = False
            self.editing_employee_id = None
            
            # Hide update and cancel buttons
            if hasattr(self, 'update_btn'):
                self.update_btn.pack_forget()
            if hasattr(self, 'cancel_edit_btn'):
                self.cancel_edit_btn.pack_forget()
            
            # Clear the form
            self.clear_form("employees")
            
            self.show_status_message("Edit mode cancelled", "info")
            
        except Exception as e:
            self.show_status_message(f"Error cancelling edit: {str(e)}", "error")
    
    def update_employee_record(self):
        """Update the employee record with form data"""
        try:
            if not self.data_service:
                self.show_status_message("Database not connected", "error")
                return
            
            if not hasattr(self, 'emp_vars'):
                self.show_status_message("Employee form not found", "error")
                return
            
            if not self.edit_mode or not self.editing_employee_id:
                self.show_status_message("Not in edit mode. Please select an employee to edit first.", "warning")
                return
            
            # Get form data
            data = {key: var.get().strip() for key, var in self.emp_vars.items()}
            
            # For edit mode, ensure we have the original employee_id and join_date
            # since these fields might be disabled and empty
            data["employee_id"] = str(self.editing_employee_id)
            if not data.get("join_date"):
                # Get the original join_date from the current employee data if empty
                try:
                    original_employee = self.data_service.get_employees({"employee_id": str(self.editing_employee_id)})
                    if not original_employee.empty:
                        data["join_date"] = original_employee.iloc[0].get("join_date", "")
                except:
                    data["join_date"] = ""  # Default to empty if we can't get it
            
            # Validate employee data with field-specific feedback
            is_valid, error_message = self.validate_employee_data_with_feedback(data)
            if not is_valid:
                self.show_status_message(f"Validation Error: {error_message}", "error")
                return
            
            # Use the original employee ID for updating (in case it was changed in form)
            employee_id = str(self.editing_employee_id)  # Ensure it's a string
            
            # Remove employee_id from update data (we use it as filter)
            update_data = {k: v for k, v in data.items() if k != "employee_id"}
            
            # Convert salary to float after validation
            if update_data.get("salary"):
                update_data["salary"] = float(update_data["salary"])
            
            # Update employee record
            result = self.data_service.update_employee(employee_id, update_data)
            
            if result > 0:
                self.show_status_message(f"Employee {employee_id} updated successfully!", "success")
                # Refresh the table
                self.refresh_table("employees")
                # Exit edit mode
                self.cancel_edit_record("employees")
            else:
                self.show_status_message(f"Failed to update employee {employee_id}", "error")
                
        except Exception as e:
            self.show_status_message(f"Failed to update employee: {str(e)}", "error")
    
    def edit_record(self, module_type):
        """Generic edit method for all modules"""
        try:
            # Map module types to their tree widget names
            tree_mapping = {
                'employees': 'employees_tree',
                'attendance': 'attendance_tree',
                'stock': 'stock_tree',
                'sales': 'sales_tree',
                'purchases': 'purchases_tree'
            }
            
            tree_name = tree_mapping.get(module_type, f"{module_type}_tree")
            tree = getattr(self, tree_name, None)
            
            if not tree:
                self.show_status_message(f"Table not found for {module_type}", "error")
                return
                
            selected_items = tree.selection()
            if not selected_items:
                self.show_status_message(f"Please select a {module_type[:-1]} to edit", "warning")
                return
                
            if len(selected_items) > 1:
                self.show_status_message(f"Please select only one {module_type[:-1]} to edit", "warning")
                return
            
            # Get record data from selection
            item = tree.item(selected_items[0])
            values = item['values']
            
            # Get MongoDB document ID from the item tags
            tags = tree.item(selected_items[0], 'tags')
            mongo_id = tags[0] if tags else None
            
            if not values:
                self.show_status_message(f"Invalid {module_type[:-1]} selection", "error")
                return
            
            # Call specific edit method based on module type
            if module_type == "employees":
                self.edit_employee_data(values, mongo_id)
            elif module_type == "attendance":
                self.edit_attendance_data(values, mongo_id)
            elif module_type == "stock":
                self.edit_stock_data(values, mongo_id)
            elif module_type == "sales":
                self.edit_sales_data(values, mongo_id)
            elif module_type == "purchases":
                self.edit_purchases_data(values, mongo_id)
                
        except Exception as e:
            self.show_status_message(f"Failed to load {module_type[:-1]} for editing: {str(e)}", "error")
    
    def edit_employee_data(self, values, mongo_id=None):
        """Edit employee specific data"""
        employee_id = str(values[0])
        
        if hasattr(self, 'emp_vars'):
            self.emp_vars["employee_id"].set(values[0])
            self.emp_vars["name"].set(values[1])
            self.emp_vars["email"].set(values[2])
            self.emp_vars["phone"].set(values[3])
            self.emp_vars["department"].set(values[4])
            self.emp_vars["position"].set(values[5])
            salary_str = str(values[6]).replace("₹", "").replace(",", "")
            self.emp_vars["salary"].set(salary_str)
            
            self.edit_mode = True
            self.editing_employee_id = employee_id
            self.edit_module_type = "employees"
            
            # Disable employee ID and join date fields during edit
            self.disable_employee_fields(['employee_id', 'join_date'])
            
            self.show_edit_buttons("employees")
            self.show_status_message(f"Editing employee: {values[1]} ({employee_id}). Employee ID and Join Date are locked for security.", "info")
    
    def edit_attendance_data(self, values, mongo_id):
        """Edit attendance specific data"""
        if hasattr(self, 'att_vars'):
            # Find the employee in dropdown format
            employee_id = str(values[0])
            try:
                employees_df = self.data_service.get_employees({"employee_id": employee_id})
                if not employees_df.empty:
                    employee_name = employees_df.iloc[0]["name"]
                    self.att_vars["employee_id"].set(f"{employee_id} - {employee_name}")
                else:
                    self.att_vars["employee_id"].set(employee_id)
            except:
                self.att_vars["employee_id"].set(employee_id)
            
            self.att_vars["date"].set(values[1])
            if len(values) > 2:
                self.att_vars["time_in"].set(values[2] if values[2] != 'N/A' else '')
            if len(values) > 3:
                self.att_vars["time_out"].set(values[3] if values[3] != 'N/A' else '')
            if len(values) > 4:
                self.att_vars["status"].set(values[4])
            if len(values) > 6 and hasattr(self, 'att_vars') and "notes" in self.att_vars:
                self.att_vars["notes"].set(values[6] if len(values) > 6 else "")
            
            self.edit_mode = True
            self.editing_attendance_id = mongo_id  # Use MongoDB ID
            self.edit_module_type = "attendance"
            
            self.show_edit_buttons("attendance")
            self.show_status_message(f"Editing attendance: {employee_id} on {values[1]}", "info")
    
    def edit_stock_data(self, values, mongo_id):
        """Edit stock specific data"""
        item_name = str(values[0])
        
        if hasattr(self, 'stock_vars'):
            self.stock_vars["item_name"].set(values[0])
            if len(values) > 1:
                self.stock_vars["category"].set(values[1])
            if len(values) > 2:
                self.stock_vars["quantity"].set(values[2])
            if len(values) > 3:
                price_str = str(values[3]).replace("₹", "").replace(",", "")
                self.stock_vars["price_per_unit"].set(price_str)
            if len(values) > 4:
                self.stock_vars["supplier"].set(values[4])
            
            self.edit_mode = True
            self.editing_stock_item = item_name  # Keep item name for stock (using item_name as key)
            self.edit_module_type = "stock"
            
            self.show_edit_buttons("stock")
            self.show_status_message(f"Editing stock item: {item_name}", "info")
    
    def edit_sales_data(self, values, mongo_id):
        """Edit sales specific data"""
        if hasattr(self, 'sales_vars'):
            self.sales_vars["item_name"].set(values[0])
            if len(values) > 1:
                self.sales_vars["quantity"].set(values[1])
            if len(values) > 2:
                price_str = str(values[2]).replace("₹", "").replace(",", "")
                self.sales_vars["price_per_unit"].set(price_str)
            if len(values) > 3:
                self.sales_vars["customer"].set(values[3])
            if len(values) > 4:
                self.sales_vars["date"].set(values[4])
            
            self.edit_mode = True
            self.editing_sale_id = mongo_id  # Use MongoDB ID
            self.edit_module_type = "sales"
            
            self.show_edit_buttons("sales")
            self.show_status_message(f"Editing sale: {values[0]} to {values[3]}", "info")
    
    def edit_purchases_data(self, values, mongo_id):
        """Edit purchases specific data"""
        if hasattr(self, 'purchase_vars'):
            self.purchase_vars["item_name"].set(values[0])
            if len(values) > 1:
                self.purchase_vars["quantity"].set(values[1])
            if len(values) > 2:
                price_str = str(values[2]).replace("₹", "").replace(",", "")
                self.purchase_vars["price_per_unit"].set(price_str)
            if len(values) > 3:
                self.purchase_vars["supplier"].set(values[3])
            if len(values) > 4:
                self.purchase_vars["date"].set(values[4])
            
            self.edit_mode = True
            self.editing_purchase_id = mongo_id  # Use MongoDB ID
            self.edit_module_type = "purchases"
            
            self.show_edit_buttons("purchases")
            self.show_status_message(f"Editing purchase: {values[0]} from {values[3]}", "info")
    
    def show_edit_buttons(self, module_type):
        """Show update and cancel buttons for edit mode"""
        try:
            update_btn = getattr(self, f'{module_type}_update_btn', None)
            cancel_btn = getattr(self, f'{module_type}_cancel_edit_btn', None)
            add_btn = getattr(self, f'{module_type}_add_btn', None)
            
            if update_btn:
                update_btn.pack(fill="x", pady=2)
            if cancel_btn:
                cancel_btn.pack(fill="x", pady=2)
            
            # Change add button text to indicate update mode
            if add_btn:
                module_name = module_type.title()[:-1] if module_type.endswith('s') else module_type.title()
                add_btn.configure(text=f"💾 Update {module_name}")
                
        except Exception as e:
            print(f"Error showing edit buttons: {e}")
    
    def hide_edit_buttons(self, module_type):
        """Hide update and cancel buttons"""
        try:
            update_btn = getattr(self, f'{module_type}_update_btn', None)
            cancel_btn = getattr(self, f'{module_type}_cancel_edit_btn', None)
            add_btn = getattr(self, f'{module_type}_add_btn', None)
            
            if update_btn:
                update_btn.pack_forget()
            if cancel_btn:
                cancel_btn.pack_forget()
            
            # Restore add button text to normal
            if add_btn:
                add_btn.configure(text="💾 Save Record")
                
        except Exception as e:
            print(f"Error hiding edit buttons: {e}")
    
    def update_record(self, module_type):
        """Generic update method for all modules"""
        try:
            if not self.edit_mode or self.edit_module_type != module_type:
                self.show_status_message(f"Not in edit mode for {module_type}", "warning")
                return
            
            if module_type == "employees":
                self.update_employee_record()
            elif module_type == "attendance":
                self.update_attendance_record()
            elif module_type == "stock":
                self.update_stock_record()
            elif module_type == "sales":
                self.update_sales_record()
            elif module_type == "purchases":
                self.update_purchases_record()
                
        except Exception as e:
            self.show_status_message(f"Failed to update {module_type[:-1]}: {str(e)}", "error")
    
    def cancel_edit_record(self, module_type):
        """Generic cancel edit method for all modules"""
        try:
            self.edit_mode = False
            self.edit_module_type = None
            self.editing_employee_id = None
            self.editing_attendance_id = None
            self.editing_sale_id = None
            self.editing_purchase_id = None
            self.editing_stock_item = None
            
            # Re-enable employee fields if we were editing an employee
            if module_type in ['employee', 'employees']:
                self.enable_employee_fields(['employee_id', 'join_date'])
            
            self.hide_edit_buttons(module_type)
            self.clear_form(module_type)
            self.show_status_message("Edit mode cancelled", "info")
            
        except Exception as e:
            self.show_status_message(f"Error cancelling edit: {str(e)}", "error")
    
    def delete_record(self, module_type):
        """Delete selected records from table"""
        try:
            # Map module types to their tree widget names
            tree_mapping = {
                'employees': 'employees_tree',
                'employee': 'employees_tree',
                'attendance': 'attendance_tree',
                'stock': 'stock_tree',
                'sales': 'sales_tree',
                'sale': 'sales_tree',
                'purchases': 'purchases_tree',
                'purchase': 'purchases_tree'
            }
            
            tree_name = tree_mapping.get(module_type, f"{module_type}_tree")
            tree = getattr(self, tree_name, None)
            
            if not tree:
                self.show_status_message(f"Table not found for {module_type}", "error")
                return
                
            # Get selected items
            selected_items = tree.selection()
            if not selected_items:
                self.show_status_message("Please select rows to delete", "warning")
                return
            
            # Confirmation dialog
            from tkinter import messagebox
            if not messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete {len(selected_items)} record(s)?"):
                return
            
            # Delete each selected record
            deleted_count = 0
            for item in selected_items:
                values = tree.item(item, 'values')
                if not values:
                    continue
                    
                # Build filter for deletion based on module type
                result = False
                if module_type in ["employee", "employees"]:
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
                elif module_type in ["sale", "sales"]:
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
                elif module_type in ["purchase", "purchases"]:
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
        """Clear form fields for all module types"""
        try:
            # Map module types to their variable dictionaries
            var_mapping = {
                'employees': 'emp_vars',
                'employee': 'emp_vars',
                'attendance': 'att_vars',
                'stock': 'stock_vars',
                'sales': 'sales_vars',
                'purchases': 'purchase_vars',
                'purchase': 'purchase_vars'
            }
            
            var_attr_name = var_mapping.get(module_type, f"{module_type}_vars")
            var_dict = getattr(self, var_attr_name, {})
            
            if not var_dict:
                self.show_status_message(f"No form fields found for {module_type}", "warning")
                return
                
            # Clear all form variables
            for var in var_dict.values():
                if hasattr(var, 'set'):
                    var.set("")
            
            # Clear validation errors and re-enable fields for employees
            if module_type in ["employees", "employee"]:
                self.clear_all_field_errors()
                # Re-enable employee fields in case they were disabled during edit
                self.enable_employee_fields(['employee_id', 'join_date'])
                    
            self.show_status_message(f"{module_type.capitalize()} form cleared successfully", "success")
            
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
            raw_records = []  # Store raw records with _id
            
            if table_type == "employees":
                data_df = self.data_service.get_employees()
                # Get raw records with _id for editing
                raw_records = self.data_service.db_manager.find_documents("employees")
            elif table_type == "attendance":
                data_df = self.data_service.get_attendance()
                raw_records = self.data_service.db_manager.find_documents("attendance")
            elif table_type == "stock":
                data_df = self.data_service.get_stock()
                raw_records = self.data_service.db_manager.find_documents("stock")
            elif table_type == "sales":
                data_df = self.data_service.get_sales()
                raw_records = self.data_service.db_manager.find_documents("sales")
            elif table_type == "purchases":
                data_df = self.data_service.get_purchases()
                raw_records = self.data_service.db_manager.find_documents("purchases")
            
            # Convert DataFrame to list of dictionaries and add MongoDB IDs
            if data_df is not None and not data_df.empty:
                # Create a mapping from display data to MongoDB IDs
                for i, (_, record) in enumerate(data_df.iterrows()):
                    values = self.extract_table_values(record, table_type)
                    # Store the MongoDB document ID as item data using tags
                    mongo_id = raw_records[i].get('_id', '') if i < len(raw_records) else ''
                    item_id = tree.insert("", "end", values=values, tags=(mongo_id,))
                
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
    
    def update_attendance_record(self):
        """Update attendance record with form data"""
        try:
            if not self.data_service or not hasattr(self, 'att_vars'):
                self.show_status_message("Database or form not available", "error")
                return
            
            if not self.editing_attendance_id:
                self.show_status_message("No attendance record selected for editing", "error")
                return
            
            # Get form data
            data = {key: var.get().strip() for key, var in self.att_vars.items()}
            
            # Extract employee_id from dropdown
            emp_selection = data.get("employee_id", "")
            if " - " in emp_selection:
                emp_id = emp_selection.split(" - ")[0].strip()
                data["employee_id"] = emp_id
            
            # Convert date to datetime
            if data.get("date"):
                data["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
            
            # Remove keys that shouldn't be updated or are used for identification
            update_data = {k: v for k, v in data.items() if k not in ["employee_id", "date"]}
            
            # Update attendance record using MongoDB ID
            result = self.data_service.update_attendance(self.editing_attendance_id, update_data)
            
            if result > 0:
                self.show_status_message("Attendance updated successfully!", "success")
                self.refresh_table("attendance")
                self.cancel_edit_record("attendance")
            else:
                self.show_status_message("Failed to update attendance", "error")
                
        except Exception as e:
            self.show_status_message(f"Failed to update attendance: {str(e)}", "error")
    
    def update_stock_record(self):
        """Update stock record with form data"""
        try:
            if not self.data_service or not hasattr(self, 'stock_vars'):
                self.show_status_message("Database or form not available", "error")
                return
            
            # Get form data
            data = {key: var.get().strip() for key, var in self.stock_vars.items()}
            
            # Convert numeric fields with correct field names
            if data.get("quantity"):
                data["current_quantity"] = int(data["quantity"])
            if data.get("price_per_unit"):
                data["unit_cost_average"] = float(data["price_per_unit"])
                data["total_value"] = data.get("current_quantity", 0) * float(data["price_per_unit"])
            
            # Use the original item name for updating
            item_name = self.editing_stock_item
            
            # Remove form field names from update data and add database field names
            update_data = {}
            for k, v in data.items():
                if k == "item_name":
                    continue  # Skip item_name as we use it for filtering
                elif k == "quantity":
                    update_data["current_quantity"] = int(v) if v else 0
                elif k == "price_per_unit":
                    update_data["unit_cost_average"] = float(v) if v else 0.0
                else:
                    update_data[k] = v
                    
            update_data["last_updated"] = datetime.now()
            
            # Update stock record
            result = self.data_service.update_stock(item_name, update_data)
            
            if result > 0:
                self.show_status_message(f"Stock item '{item_name}' updated successfully!", "success")
                self.refresh_table("stock")
                self.cancel_edit_record("stock")
            else:
                self.show_status_message(f"Failed to update stock item '{item_name}'", "error")
                
        except Exception as e:
            self.show_status_message(f"Failed to update stock: {str(e)}", "error")
    
    def update_sales_record(self):
        """Update sales record with form data"""
        try:
            if not self.data_service or not hasattr(self, 'sales_vars'):
                self.show_status_message("Database or form not available", "error")
                return
            
            if not self.editing_sale_id:
                self.show_status_message("No sales record selected for editing", "error")
                return
            
            # Get form data
            data = {key: var.get().strip() for key, var in self.sales_vars.items()}
            
            # Map form fields to database fields
            update_data = {}
            for k, v in data.items():
                if k == "customer":
                    update_data["customer_name"] = v
                elif k == "price_per_unit":
                    update_data["unit_price"] = float(v) if v else 0.0
                else:
                    update_data[k] = v
            
            # Convert numeric fields
            if update_data.get("quantity"):
                update_data["quantity"] = int(update_data["quantity"])
            
            # Calculate total
            if update_data.get("quantity") and update_data.get("unit_price"):
                update_data["total_price"] = update_data["quantity"] * update_data["unit_price"]
            
            # Convert date
            if update_data.get("date"):
                update_data["date"] = datetime.strptime(update_data["date"], "%Y-%m-%d")
            
            # Update sales record using MongoDB ID
            result = self.data_service.update_sale(self.editing_sale_id, update_data)
            
            if result > 0:
                self.show_status_message("Sales record updated successfully!", "success")
                self.refresh_table("sales")
                self.cancel_edit_record("sales")
            else:
                self.show_status_message("Failed to update sales record", "error")
                
        except Exception as e:
            self.show_status_message(f"Failed to update sales: {str(e)}", "error")
    
    def update_purchases_record(self):
        """Update purchases record with form data"""
        try:
            if not self.data_service or not hasattr(self, 'purchase_vars'):
                self.show_status_message("Database or form not available", "error")
                return
            
            if not self.editing_purchase_id:
                self.show_status_message("No purchase record selected for editing", "error")
                return
            
            # Get form data
            data = {key: var.get().strip() for key, var in self.purchase_vars.items()}
            
            # Convert numeric fields
            if data.get("quantity"):
                data["quantity"] = int(data["quantity"])
            if data.get("price_per_unit"):
                data["price_per_unit"] = float(data["price_per_unit"])
                data["total_amount"] = data["quantity"] * data["price_per_unit"]
            
            # Convert date
            if data.get("date"):
                data["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
            
            # Update purchase record using MongoDB ID
            result = self.data_service.update_purchase(self.editing_purchase_id, data)
            
            if result > 0:
                self.show_status_message("Purchase record updated successfully!", "success")
                self.refresh_table("purchases")
                self.cancel_edit_record("purchases")
            else:
                self.show_status_message("Failed to update purchase record", "error")
                
        except Exception as e:
            self.show_status_message(f"Failed to update purchase: {str(e)}", "error")
    
    def disable_employee_fields(self, field_keys):
        """Disable specific employee form fields"""
        try:
            if not hasattr(self, 'employee_field_widgets'):
                return
                
            for key in field_keys:
                widget_info = self.employee_field_widgets.get(key)
                if not widget_info:
                    continue
                    
                widget_type = widget_info.get('type', 'entry')
                
                if widget_type == 'entry':
                    entry = widget_info.get('entry')
                    if entry:
                        entry.configure(state='disabled')
                elif widget_type == 'combo':
                    combo = widget_info.get('combo')
                    if combo:
                        combo.configure(state='disabled')
                elif widget_type == 'date':
                    date_entry = widget_info.get('date_entry')
                    today_btn = widget_info.get('today_btn')
                    if date_entry:
                        date_entry.configure(state='disabled')
                    if today_btn:
                        today_btn.configure(state='disabled')
                        
        except Exception as e:
            print(f"Error disabling employee fields: {e}")
    
    def enable_employee_fields(self, field_keys):
        """Enable specific employee form fields"""
        try:
            if not hasattr(self, 'employee_field_widgets'):
                return
                
            for key in field_keys:
                widget_info = self.employee_field_widgets.get(key)
                if not widget_info:
                    continue
                    
                widget_type = widget_info.get('type', 'entry')
                
                if widget_type == 'entry':
                    entry = widget_info.get('entry')
                    if entry:
                        entry.configure(state='normal')
                elif widget_type == 'combo':
                    combo = widget_info.get('combo')
                    if combo:
                        combo.configure(state='readonly')  # combo boxes should be readonly, not normal
                elif widget_type == 'date':
                    date_entry = widget_info.get('date_entry')
                    today_btn = widget_info.get('today_btn')
                    if date_entry:
                        date_entry.configure(state='normal')
                    if today_btn:
                        today_btn.configure(state='normal')
                        
        except Exception as e:
            print(f"Error enabling employee fields: {e}")

# Alias for compatibility
DataPageGUI = ModernDataPageGUI
