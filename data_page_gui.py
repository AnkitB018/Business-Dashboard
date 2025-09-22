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
from calendar_widget import DateFieldWithCalendar, parse_date_from_display, format_date_for_display

logger = logging.getLogger(__name__)

class ModernDataPageGUI:
    def __init__(self, parent, data_service):
        self.parent = parent
        self.data_service = data_service  # This is HRDataService for basic operations
        
        # Import and create DataService for order management
        try:
            from data_service import DataService
            self.order_service = DataService()  # Create DataService for order operations
        except Exception as e:
            self.order_service = None
            
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
        self.edit_module_type = None
        
        # Module filtering - by default show all modules (removed stock)
        self.enabled_modules = ["employees", "attendance", "sales", "purchases"]
        
        self.create_page()
    
    def configure_modules(self, modules_list):
        """Configure which modules to show in this instance
        modules_list: list of module names to show ['employees', 'attendance'] or ['sales', 'purchases']
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
            
            # Aadhar validation (optional)
            if not self.validate_aadhar(data.get("aadhar_no", "")):
                return False, "Aadhar number must be 12 digits (optional)"
            
            # Phone validation
            if not self.validate_phone(data.get("phone", "")):
                return False, "Phone must be 10 digits (e.g., 9876543210) or with country code (+91 9876543210)"
            
            # Daily wage validation
            if not self.validate_daily_wage(data.get("daily_wage", "")):
                return False, "Daily wage must be a positive number between 1 and 50,000"
            
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
    
    def validate_aadhar(self, aadhar):
        """Validate Aadhar number: 12 digits, optional"""
        # Aadhar is optional, so empty is valid
        if not aadhar or len(aadhar.strip()) == 0:
            return True
        
        # Remove spaces and check if it's 12 digits
        aadhar_clean = aadhar.replace(" ", "").strip()
        
        # Must be exactly 12 digits
        if len(aadhar_clean) != 12:
            return False
        
        # Must be all digits
        return aadhar_clean.isdigit()

    def validate_daily_wage(self, daily_wage):
        """Validate daily wage: positive number between 1 and 50,000"""
        if not daily_wage:
            return False
        
        try:
            daily_wage_val = float(str(daily_wage).replace(',', ''))
            return 1 <= daily_wage_val <= 50000
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
            # Email is optional now, only validate if it exists and is not empty
            if value and value.strip():
                if not self.validate_email(value):
                    is_valid = False
                    error_msg = "Valid email with .com/.org/.net/.in domain required"
        elif field_key == "phone":
            if not self.validate_phone(value):
                is_valid = False
                error_msg = "10 digits starting with 6,7,8,9 or +91 format"
        elif field_key == "daily_wage":
            if not self.validate_daily_wage(value):
                is_valid = False
                error_msg = "Amount between ₹1 and ₹50,000"
        
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
            
            # Aadhar validation (optional)
            aadhar_valid = self.validate_aadhar(data.get("aadhar_no", ""))
            if not aadhar_valid:
                self.show_field_error("aadhar_no", "12 digits only, spaces allowed (optional)")
                is_valid = False
                error_fields.append("Aadhar No")
            
            # Phone validation
            phone_valid = self.validate_phone(data.get("phone", ""))
            if not phone_valid:
                self.show_field_error("phone", "10 digits starting with 6,7,8,9 or +91 format")
                is_valid = False
                error_fields.append("Phone")
            
            # Daily wage validation
            daily_wage_valid = self.validate_daily_wage(data.get("daily_wage", ""))
            if not daily_wage_valid:
                self.show_field_error("daily_wage", "Amount between ₹1 and ₹50,000")
                is_valid = False
                error_fields.append("Daily Wage")
            
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

💰 Daily Wage:
   • Range: ₹1 to ₹50,000
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
            height=40,  # Reduced from 60 to 40
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
            width=80,  # Reduced from 100 to 80
            height=28,  # Reduced from 35 to 28
            fg_color=self.colors['button_uniform'],
            hover_color=self.colors['button_hover'],
            font=ctk.CTkFont(size=12, weight="bold")  # Reduced from 14 to 12
        )
        self.back_button.pack(side="left", padx=15, pady=6)  # Reduced padding
        
        # Breadcrumb
        self.breadcrumb_label = ctk.CTkLabel(
            self.nav_frame,
            text="Data Management",
            font=ctk.CTkFont(size=14, weight="bold"),  # Reduced from 16 to 14
            text_color=self.colors['text_primary']
        )
        self.breadcrumb_label.pack(side="left", padx=(8, 0), pady=6)  # Reduced padding
        
    def create_main_dashboard(self):
        """Create the main dashboard view (grid of modules)"""
        # Create main dashboard frame
        self.main_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        
        # Create main content area with cards (no header here since it's already created)
        self.create_main_content()

    def create_status_bar(self):
        """Create enhanced status bar for showing messages"""
        self.status_frame = ctk.CTkFrame(self.frame, height=35, corner_radius=8)  # Reduced from 50 to 35
        self.status_frame.pack(fill="x", padx=15, pady=(0, 15))  # Reduced padding
        self.status_frame.pack_propagate(False)
        
        # Status icon and text container
        status_container = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        status_container.pack(expand=True, fill="both", padx=12, pady=6)  # Reduced padding
        
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
    
    def show_success_message(self, message):
        """Show success message with green color and checkmark"""
        self.show_status_message(message, "success")
        # Also show a popup for important success messages
        self.show_success_popup(message)
    
    def show_error_message(self, message):
        """Show error message with red color and X mark"""
        self.show_status_message(message, "error")
    
    def show_success_popup(self, message):
        """Show green success popup message"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            # Create a custom success popup
            popup = tk.Toplevel()
            popup.title("✅ Success!")
            popup.geometry("400x300")
            popup.resizable(False, False)
            popup.configure(bg="#e8f5e8")  # Light green background
            popup.grab_set()  # Make modal
            
            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
            y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            
            # Main frame
            main_frame = tk.Frame(popup, bg="#e8f5e8", padx=20, pady=20)
            main_frame.pack(fill="both", expand=True)
            
            # Success icon
            icon_label = tk.Label(main_frame, text="✅", font=("Arial", 24), bg="#e8f5e8", fg="#2e7d32")
            icon_label.pack(pady=(0, 10))
            
            # Success title
            title_label = tk.Label(main_frame, text="Success!", font=("Arial", 16, "bold"), bg="#e8f5e8", fg="#2e7d32")
            title_label.pack(pady=(0, 10))
            
            # Message text
            msg_label = tk.Label(main_frame, text=message, font=("Arial", 10), bg="#e8f5e8", fg="#1b5e20", 
                               wraplength=350, justify="left")
            msg_label.pack(pady=(0, 20))
            
            # OK button
            ok_button = tk.Button(main_frame, text="OK", font=("Arial", 12, "bold"), 
                                bg="#4caf50", fg="white", padx=30, pady=8,
                                command=popup.destroy)
            ok_button.pack()
            
            # Auto-close after 8 seconds
            popup.after(8000, popup.destroy)
            
        except Exception as e:
            print(f"Error showing success popup: {e}")
            # Fallback to simple messagebox
            try:
                import tkinter.messagebox as msgbox
                msgbox.showinfo("Success", message)
            except:
                pass
        
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
            
        self.content_frames[module_type] = module_frame
        
    def create_header(self):
        """Create modern header section with enhanced styling"""
        header_frame = ctk.CTkFrame(
            self.frame, 
            height=60,  # Reduced from 100 to 60
            corner_radius=15,  # Reduced corner radius
            fg_color=("white", "gray20"),
            border_width=1,
            border_color=self.colors['border']
        )
        header_frame.pack(fill="x", padx=20, pady=(15, 10))  # Reduced padding
        header_frame.pack_propagate(False)
        
        # Left side - Title and subtitle with modern typography
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left", fill="y", padx=20, pady=10)  # Reduced padding
        
        # Main title with gradient-like effect
        title_label = ctk.CTkLabel(
            title_container,
            text="📊 Data Management Center",
            font=ctk.CTkFont(size=20, weight="bold"),  # Reduced from 32 to 20
            text_color=self.colors['primary']
        )
        title_label.pack(anchor="w")
        
        # Subtitle with modern styling
        subtitle_label = ctk.CTkLabel(
            title_container,
            text="Comprehensive business data management and analytics platform",
            font=ctk.CTkFont(size=11),  # Reduced from 14 to 11
            text_color=self.colors['text_secondary']
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))  # Reduced padding
        
        # Right side - Modern quick stats with better layout
        stats_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_container.pack(side="right", fill="y", padx=20, pady=10)  # Reduced padding
        
        self.create_quick_stats(stats_container)
        
    def create_quick_stats(self, parent):
        """Create modern statistics cards with enhanced design"""
        try:
            if not self.data_service:
                return
                
            # Get quick stats using the correct method names
            employees_df = self.data_service.get_employees()
            
            employees_count = len(employees_df) if not employees_df.empty else 0
            
            # Modern stat cards with improved design
            stats = [
                ("👥", str(employees_count), "Employees", self.colors['primary'])
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
                "title": " Sales Records",
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
        """Create sales management content in the frame with orders and transactions"""
        self.create_sales_orders_content(parent)
        
    def create_purchase_management_content(self, parent):
        """Create purchase management content in the frame"""
        self.create_module_content(parent, "Purchase Management", "purchases")
        
    def create_module_content(self, parent, title, module_type):
        """Create module content within a frame (adapted from window version)"""
        # Module header
        header_frame = ctk.CTkFrame(parent, height=50, corner_radius=10)  # Reduced from 80 to 50, corner radius from 15 to 10
        header_frame.pack(fill="x", padx=15, pady=(10, 8))  # Reduced padding
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"📋 {title}",
            font=ctk.CTkFont(size=16, weight="bold"),  # Reduced from 24 to 16
            text_color=self.colors['primary']
        )
        title_label.pack(side="left", padx=15, pady=12)  # Reduced padding
        
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
        form_header = ctk.CTkFrame(form_panel, height=40, corner_radius=6)  # Reduced from 60 to 40, corner radius from 8 to 6
        form_header.pack(fill="x", padx=12, pady=(10, 8))  # Reduced padding
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="👤 Employee Details",
            font=ctk.CTkFont(size=14, weight="bold")  # Reduced from 18 to 14
        ).pack(pady=10)  # Reduced from 15 to 10
        
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
        self.create_form_field(form_scroll, "Aadhar No.", "aadhar_no", "text", self.emp_vars,
                              placeholder="1234 5678 9012 (12 digits, optional)")
        self.create_form_field(form_scroll, "Phone Number", "phone", "text", self.emp_vars,
                              placeholder="9876543210 or +91 9876543210 (10 digits)")
        
        # Department field (text input)
        self.create_form_field(form_scroll, "Department", "department", "text", self.emp_vars,
                              placeholder="e.g., Human Resources, IT, Finance, Sales, Marketing")
        
        # Position field (text input)
        self.create_form_field(form_scroll, "Position", "position", "text", self.emp_vars,
                              placeholder="e.g., Manager, Developer, Analyst, Executive")
        
        # Salary field with validation hint
        self.create_form_field(form_scroll, "Daily Wage (₹)", "daily_wage", "number", self.emp_vars,
                              placeholder="500 (Range: 1 - 50,000)")
        
        # Join date
        self.create_date_picker(form_scroll, "Join Date", "join_date", self.emp_vars)
        
        # Form buttons
        self.create_form_buttons(form_scroll, "employees")
        
        # Data table
        self.create_data_table(data_panel, "employees")
    
    def create_attendance_form(self, form_panel, data_panel):
        """Create simplified and accessible attendance form"""
        # Form header
        form_header = ctk.CTkFrame(form_panel, height=40, corner_radius=6)  # Reduced from 60 to 40
        form_header.pack(fill="x", padx=12, pady=(10, 8))  # Reduced padding
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="📅 Attendance Record",
            font=ctk.CTkFont(size=14, weight="bold")  # Reduced from 18 to 14
        ).pack(pady=10)  # Reduced from 15 to 10
        
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
        self.create_attendance_date_picker(form_scroll, "Date", "date", self.att_vars)
        
        # Time pickers with improved layout (store references for dynamic control)
        self.time_in_widgets = self.create_time_picker(form_scroll, "Time In", "time_in", self.att_vars)
        self.time_out_widgets = self.create_time_picker(form_scroll, "Time Out", "time_out", self.att_vars)
        
        # Status dropdown with simplified options
        self.create_attendance_status_dropdown(form_scroll, "Status", "status", 
                               ["Present", "Absent", "Leave"], self.att_vars)
        
        # Exception hour field (always enabled, default 1)
        self.create_exception_hour_field(form_scroll, "Exception Hours", "exception_hours", self.att_vars)
        
        # Notes field (optional)
        self.create_form_field(form_scroll, "Notes (Optional)", "notes", "text", self.att_vars, 
                              placeholder="Any additional notes...")
        
        # Form buttons
        self.create_form_buttons(form_scroll, "attendance")
        
        # Data table
        self.create_data_table(data_panel, "attendance")
        
    def create_sales_form(self, form_panel, data_panel):
        """Create modern sales form"""
        # Form header
        form_header = ctk.CTkFrame(form_panel, height=40, corner_radius=6)  # Reduced from 60 to 40
        form_header.pack(fill="x", padx=12, pady=(10, 8))  # Reduced padding
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="💰 Sales Record",
            font=ctk.CTkFont(size=14, weight="bold")  # Reduced from 18 to 14
        ).pack(pady=10)  # Reduced from 15 to 10
        
        # Scrollable form area
        form_scroll = ctk.CTkScrollableFrame(form_panel)
        form_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Configure improved scroll speed
        self.configure_scroll_speed(form_scroll)
        
        # Form fields
        self.sales_vars = {}
        fields = [
            ("Item Name", "item_name", "text"),
            ("Quantity", "quantity", "number"),
            ("Sale Price (₹)", "price_per_unit", "number"),
            ("Customer Name", "customer", "text"),
            ("Sale Date", "date", "date")
        ]
        
        for label, key, field_type in fields:
            if field_type == "date":
                self.create_date_picker(form_scroll, label, key, self.sales_vars)
            else:
                self.create_form_field(form_scroll, label, key, field_type, self.sales_vars)
        
        # Form buttons
        self.create_form_buttons(form_scroll, "sales")
        
        # Data table
        self.create_data_table(data_panel, "sales")
        
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
        """Create date picker with calendar interface using dd/mm/yy format"""
        # Field container
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
        
        # Initialize variable with today's date in dd/mm/yy format
        vars_dict[key] = tk.StringVar()
        vars_dict[key].set(date.today().strftime("%d/%m/%y"))
        
        # Date entry
        date_entry = ctk.CTkEntry(
            date_frame,
            textvariable=vars_dict[key],
            width=200,
            height=35,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=12),
            placeholder_text="dd/mm/yy"
        )
        date_entry.pack(side="left", padx=(0, 10))
        
        # Calendar button
        calendar_btn = ctk.CTkButton(
            date_frame,
            text="📅",
            width=35,
            height=35,
            corner_radius=6,
            command=lambda: self.show_sales_calendar(vars_dict[key])
        )
        calendar_btn.pack(side="left", padx=(0, 10))
        
        # Today button
        today_btn = ctk.CTkButton(
            date_frame,
            text="Today",
            command=lambda: vars_dict[key].set(date.today().strftime("%d/%m/%y")),
            width=80,
            height=35,
            corner_radius=6
        )
        today_btn.pack(side="left")
        
        # Helper text
        helper_text = ctk.CTkLabel(
            field_frame,
            text="Format: dd/mm/yy (e.g., 15/09/25)",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        helper_text.pack(anchor="w", pady=(5, 0))
        
        # Store reference for validation
        if not hasattr(self, 'field_widgets'):
            self.field_widgets = {}
        self.field_widgets[f'employee_{key}'] = {
            'entry': date_entry,
            'var': vars_dict[key],
            'type': 'date'
        }
    
    def show_employee_calendar(self, date_var):
        """Show a calendar popup specifically for employee date selection"""
        try:
            import tkinter as tk
            from tkinter import ttk
            import calendar
            
            # Create popup window
            popup = tk.Toplevel(self.parent)
            popup.title("Select Date")
            popup.geometry("300x250")
            popup.resizable(False, False)
            popup.transient(self.parent)
            popup.grab_set()
            
            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (150)
            y = (popup.winfo_screenheight() // 2) - (125)
            popup.geometry(f"300x250+{x}+{y}")
            
            # Current date
            current_date = date.today()
            current_year = current_date.year
            current_month = current_date.month
            
            # Try to parse existing date from entry
            try:
                existing_date = date_var.get().strip()
                if existing_date and "/" in existing_date:
                    day, month, year = existing_date.split("/")
                    # Handle 2-digit year
                    if len(year) == 2:
                        year = "20" + year if int(year) < 50 else "19" + year
                    current_year = int(year)
                    current_month = int(month)
            except:
                pass  # Use current date if parsing fails
            
            # Header frame
            header_frame = tk.Frame(popup, bg="#f0f0f0")
            header_frame.pack(fill="x", padx=5, pady=5)
            
            # Previous month button
            prev_btn = tk.Button(header_frame, text="<", width=3, 
                               command=lambda: change_month(-1))
            prev_btn.pack(side="left")
            
            # Month/Year label
            month_label = tk.Label(header_frame, 
                                 text=f"{calendar.month_name[current_month]} {current_year}",
                                 font=("Arial", 12, "bold"), bg="#f0f0f0")
            month_label.pack(side="left", expand=True)
            
            # Next month button
            next_btn = tk.Button(header_frame, text=">", width=3,
                               command=lambda: change_month(1))
            next_btn.pack(side="right")
            
            # Calendar frame
            cal_frame = tk.Frame(popup)
            cal_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            def change_month(delta):
                nonlocal current_month, current_year
                current_month += delta
                if current_month > 12:
                    current_month = 1
                    current_year += 1
                elif current_month < 1:
                    current_month = 12
                    current_year -= 1
                
                month_label.config(text=f"{calendar.month_name[current_month]} {current_year}")
                create_calendar()
            
            def create_calendar():
                # Clear existing calendar
                for widget in cal_frame.winfo_children():
                    widget.destroy()
                
                # Days of week header
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                for i, day in enumerate(days):
                    label = tk.Label(cal_frame, text=day, font=("Arial", 9, "bold"))
                    label.grid(row=0, column=i, padx=1, pady=1)
                
                # Calendar days
                cal = calendar.monthcalendar(current_year, current_month)
                for week_num, week in enumerate(cal, start=1):
                    for day_num, day in enumerate(week):
                        if day == 0:
                            # Empty cell
                            label = tk.Label(cal_frame, text="")
                            label.grid(row=week_num, column=day_num, padx=1, pady=1)
                        else:
                            # Day button
                            btn = tk.Button(cal_frame, text=str(day), width=3, height=1,
                                          command=lambda d=day: select_date(d))
                            btn.grid(row=week_num, column=day_num, padx=1, pady=1)
            
            def select_date(day):
                # Format as dd/mm/yy
                formatted_date = f"{day:02d}/{current_month:02d}/{str(current_year)[2:]}"
                date_var.set(formatted_date)
                popup.destroy()
            
            # Button frame
            button_frame = tk.Frame(popup)
            button_frame.pack(fill="x", padx=5, pady=5)
            
            today_btn = tk.Button(button_frame, text="Today",
                                command=lambda: (
                                    date_var.set(date.today().strftime("%d/%m/%y")),
                                    popup.destroy()
                                ))
            today_btn.pack(side="left", padx=5)
            
            cancel_btn = tk.Button(button_frame, text="Cancel",
                                 command=popup.destroy)
            cancel_btn.pack(side="right", padx=5)
            
            # Create initial calendar
            create_calendar()
            
        except Exception as e:
            # Fallback to simple date input
            self.show_status_message(f"Calendar error: {str(e)}", "warning")
            date_var.set(date.today().strftime("%d/%m/%y"))

    def show_purchase_calendar(self, date_var):
        """Show calendar popup specifically for purchase date selection"""
        try:
            import tkinter as tk
            from tkinter import ttk
            import calendar
            
            # Create popup window
            popup = tk.Toplevel()
            popup.title("Select Purchase Date")
            popup.geometry("300x250")
            popup.resizable(False, False)
            
            # Make sure popup appears on top
            popup.lift()
            popup.focus_force()
            popup.grab_set()
            
            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (150)
            y = (popup.winfo_screenheight() // 2) - (125)
            popup.geometry(f"300x250+{x}+{y}")
            
            # Current date
            current_date = date.today()
            current_year = current_date.year
            current_month = current_date.month
            
            # Try to parse existing date from entry
            try:
                existing_date = date_var.get().strip()
                if existing_date and "/" in existing_date:
                    day, month, year = existing_date.split("/")
                    # Handle 2-digit year
                    if len(year) == 2:
                        year = "20" + year if int(year) < 50 else "19" + year
                    current_year = int(year)
                    current_month = int(month)
            except:
                pass  # Use current date if parsing fails
            
            # Header frame with purchase styling
            header_frame = tk.Frame(popup, bg="#e8f4f8")
            header_frame.pack(fill="x", padx=5, pady=5)
            
            # Previous month button
            prev_btn = tk.Button(header_frame, text="◄", width=3, 
                               command=lambda: change_month(-1))
            prev_btn.pack(side="left")
            
            # Month/Year label
            month_label = tk.Label(header_frame, 
                                 text=f"{calendar.month_name[current_month]} {current_year}",
                                 font=("Arial", 12, "bold"), bg="#e8f4f8")
            month_label.pack(side="left", expand=True)
            
            # Next month button
            next_btn = tk.Button(header_frame, text="►", width=3,
                               command=lambda: change_month(1))
            next_btn.pack(side="right")
            
            # Calendar frame
            cal_frame = tk.Frame(popup, bg="white")
            cal_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            def change_month(delta):
                nonlocal current_month, current_year
                current_month += delta
                if current_month > 12:
                    current_month = 1
                    current_year += 1
                elif current_month < 1:
                    current_month = 12
                    current_year -= 1
                
                month_label.config(text=f"{calendar.month_name[current_month]} {current_year}")
                create_calendar()
            
            def create_calendar():
                # Clear existing calendar
                for widget in cal_frame.winfo_children():
                    widget.destroy()
                
                # Days of week header
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                for i, day in enumerate(days):
                    label = tk.Label(cal_frame, text=day, font=("Arial", 9, "bold"), 
                                   bg="lightblue", fg="darkblue")
                    label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
                
                # Calendar days
                cal = calendar.monthcalendar(current_year, current_month)
                for week_num, week in enumerate(cal, start=1):
                    for day_num, day in enumerate(week):
                        if day == 0:
                            # Empty cell
                            label = tk.Label(cal_frame, text="", bg="white")
                            label.grid(row=week_num, column=day_num, padx=1, pady=1)
                        else:
                            # Day button
                            btn = tk.Button(cal_frame, text=str(day), width=3, height=1,
                                          bg="lightgreen", fg="darkgreen",
                                          command=lambda d=day: select_date(d))
                            btn.grid(row=week_num, column=day_num, padx=1, pady=1)
                
                # Configure grid weights
                for i in range(7):
                    cal_frame.grid_columnconfigure(i, weight=1)
            
            def select_date(day):
                # Format as dd/mm/yy
                formatted_date = f"{day:02d}/{current_month:02d}/{str(current_year)[2:]}"
                date_var.set(formatted_date)
                popup.destroy()
            
            # Button frame
            button_frame = tk.Frame(popup, bg="#f0f0f0")
            button_frame.pack(fill="x", padx=5, pady=5)
            
            today_btn = tk.Button(button_frame, text="📅 Today", bg="orange", fg="white",
                                command=lambda: (
                                    date_var.set(date.today().strftime("%d/%m/%y")),
                                    popup.destroy()
                                ))
            today_btn.pack(side="left", padx=5)
            
            cancel_btn = tk.Button(button_frame, text="❌ Cancel", bg="red", fg="white",
                                 command=popup.destroy)
            cancel_btn.pack(side="right", padx=5)
            
            # Create initial calendar
            create_calendar()
            
            # Ensure popup stays on top and focused
            popup.after(10, lambda: popup.focus_force())
            
        except Exception as e:
            # Fallback to simple date input
            self.show_status_message(f"Purchase calendar error: {str(e)}", "warning")
            date_var.set(date.today().strftime("%d/%m/%y"))

    def show_sales_calendar(self, date_var):
        """Show calendar popup specifically for sales date selection - Improved Layout"""
        try:
            import tkinter as tk
            from tkinter import ttk
            import calendar
            
            # Create popup window with better size
            popup = tk.Toplevel(self.parent)
            popup.title("Select Sales Date")
            popup.geometry("380x420")  # Larger size
            popup.resizable(False, False)
            popup.transient(self.parent)
            popup.grab_set()
            
            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (190)
            y = (popup.winfo_screenheight() // 2) - (210)
            popup.geometry(f"380x420+{x}+{y}")
            
            # Current date
            current_date = date.today()
            current_year = current_date.year
            current_month = current_date.month
            
            # Try to parse existing date from entry
            try:
                existing_date = date_var.get().strip()
                if existing_date and "/" in existing_date:
                    day, month, year = existing_date.split("/")
                    # Handle 2-digit year
                    if len(year) == 2:
                        year = "20" + year if int(year) < 50 else "19" + year
                    current_year = int(year)
                    current_month = int(month)
            except:
                pass  # Use current date if parsing fails
            
            # Header frame
            header_frame = tk.Frame(popup, bg="#2563EB", height=60)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            
            # Month/Year display
            month_year_var = tk.StringVar()
            month_year_label = tk.Label(header_frame, textvariable=month_year_var, 
                                      bg="#2563EB", fg="white", font=("Arial", 16, "bold"))
            month_year_label.pack(expand=True)
            
            # Navigation frame
            nav_frame = tk.Frame(popup, bg="#f8f9fa", height=50)
            nav_frame.pack(fill="x")
            nav_frame.pack_propagate(False)
            
            # Calendar frame - larger and properly sized
            cal_frame = tk.Frame(popup, bg="white")
            cal_frame.pack(fill="both", expand=True, padx=15, pady=10)
            
            def create_calendar():
                # Clear existing calendar
                for widget in cal_frame.winfo_children():
                    widget.destroy()
                
                # Update month/year display
                month_year_var.set(f"{calendar.month_name[current_month]} {current_year}")
                
                # Clear navigation frame
                for widget in nav_frame.winfo_children():
                    widget.destroy()
                
                # Navigation buttons in nav_frame
                prev_btn = tk.Button(nav_frame, text="◀ Previous", 
                                   command=prev_month, bg="#3B82F6", fg="white",
                                   font=("Arial", 11), width=12, height=2)
                prev_btn.pack(side="left", padx=20, pady=10)
                
                next_btn = tk.Button(nav_frame, text="Next ▶", 
                                   command=next_month, bg="#3B82F6", fg="white",
                                   font=("Arial", 11), width=12, height=2)
                next_btn.pack(side="right", padx=20, pady=10)
                
                # Day headers with better spacing
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                for i, day in enumerate(days):
                    day_label = tk.Label(cal_frame, text=day, font=("Arial", 11, "bold"), 
                                       bg="#e9ecef", fg="#495057", width=5, height=2,
                                       relief="solid", bd=1)
                    day_label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
                
                # Configure grid weights for proper sizing
                for i in range(7):
                    cal_frame.grid_columnconfigure(i, weight=1)
                for i in range(7):  # 6 weeks max + header
                    cal_frame.grid_rowconfigure(i, weight=1)
                
                # Get calendar for the month
                cal = calendar.monthcalendar(current_year, current_month)
                
                # Create day buttons with proper sizing
                for week_num, week in enumerate(cal):
                    for day_num, day in enumerate(week):
                        if day == 0:
                            # Empty cell for days from other months
                            empty_label = tk.Label(cal_frame, text="", width=5, height=3,
                                                 bg="white", relief="flat")
                            empty_label.grid(row=week_num + 1, column=day_num, padx=1, pady=1, sticky="nsew")
                        else:
                            # Create button for each day
                            btn = tk.Button(cal_frame, text=str(day), width=5, height=3,
                                          command=lambda d=day: select_date(d),
                                          bg="white", fg="black", font=("Arial", 10),
                                          relief="solid", bd=1, cursor="hand2")
                            btn.grid(row=week_num + 1, column=day_num, padx=1, pady=1, sticky="nsew")
                            
                            # Highlight today
                            if (current_year == date.today().year and 
                                current_month == date.today().month and 
                                day == date.today().day):
                                btn.config(bg="#059669", fg="white", font=("Arial", 10, "bold"))
                            
                            # Hover effects
                            def on_enter(e, button=btn):
                                if button['bg'] != "#059669":
                                    button.config(bg="#e3f2fd")
                            
                            def on_leave(e, button=btn):
                                if button['bg'] != "#059669":
                                    button.config(bg="white")
                            
                            btn.bind("<Enter>", on_enter)
                            btn.bind("<Leave>", on_leave)
            
            def prev_month():
                nonlocal current_month, current_year
                if current_month == 1:
                    current_month = 12
                    current_year -= 1
                else:
                    current_month -= 1
                create_calendar()
            
            def next_month():
                nonlocal current_month, current_year
                if current_month == 12:
                    current_month = 1
                    current_year += 1
                else:
                    current_month += 1
                create_calendar()
            
            def select_date(day):
                # Set the date in dd/mm/yy format
                selected_date = f"{day:02d}/{current_month:02d}/{str(current_year)[2:]}"
                date_var.set(selected_date)
                popup.destroy()
            
            # Button frame at bottom
            button_frame = tk.Frame(popup, bg="#f8f9fa", height=60)
            button_frame.pack(fill="x")
            button_frame.pack_propagate(False)
            
            today_btn = tk.Button(button_frame, text="🗓️ Today", 
                                command=lambda: (date_var.set(date.today().strftime("%d/%m/%y")), popup.destroy()),
                                bg="#059669", fg="white", font=("Arial", 11), 
                                width=12, height=2, cursor="hand2")
            today_btn.pack(side="left", padx=20, pady=15)
            
            cancel_btn = tk.Button(button_frame, text="❌ Cancel", bg="#DC2626", fg="white",
                                 command=popup.destroy, font=("Arial", 11),
                                 width=12, height=2, cursor="hand2")
            cancel_btn.pack(side="right", padx=20, pady=15)
            
            # Create initial calendar
            create_calendar()
            
        except Exception as e:
            # Fallback to simple date input
            self.show_status_message(f"Sales calendar error: {str(e)}", "warning")
            date_var.set(date.today().strftime("%d/%m/%y"))
    
    def create_attendance_date_picker(self, parent, label, key, vars_dict):
        """Create date picker for attendance with dd/mm/yy format and calendar"""
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
        
        # Date entry in dd/mm/yy format (but store as YYYY-MM-DD internally)
        vars_dict[key] = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))  # Internal storage
        display_var = tk.StringVar(value=date.today().strftime("%d/%m/%y"))  # Display format
        
        date_entry = ctk.CTkEntry(
            date_frame,
            textvariable=display_var,
            width=120,
            height=35,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=12),
            placeholder_text="dd/mm/yy"
        )
        date_entry.pack(side="left", padx=(0, 10))
        
        # Calendar button
        cal_btn = ctk.CTkButton(
            date_frame,
            text="📅",
            command=lambda: self.open_attendance_calendar(vars_dict[key], display_var),
            width=40,
            height=35,
            corner_radius=6,
            font=ctk.CTkFont(size=14)
        )
        cal_btn.pack(side="left", padx=(0, 10))
        
        # Today button
        today_btn = ctk.CTkButton(
            date_frame,
            text="Today",
            command=lambda: self.set_attendance_date_today(vars_dict[key], display_var),
            width=80,
            height=35,
            corner_radius=6,
            font=ctk.CTkFont(size=11)
        )
        today_btn.pack(side="left")
        
        # Sync display format with internal format when user types
        def sync_date_formats(*args):
            try:
                user_input = display_var.get().strip()
                if user_input:
                    # Try to parse user input in dd/mm/yy format
                    if '/' in user_input:
                        parts = user_input.split('/')
                        if len(parts) == 3:
                            day, month, year = parts
                            # Handle 2-digit year
                            if len(year) == 2:
                                year = f"20{year}" if int(year) < 50 else f"19{year}"
                            # Create date object to validate
                            date_obj = datetime(int(year), int(month), int(day))
                            # Store in internal format
                            vars_dict[key].set(date_obj.strftime("%Y-%m-%d"))
                        else:
                            # Invalid format, reset to today
                            self.set_attendance_date_today(vars_dict[key], display_var)
                    else:
                        # Try other formats or reset to today
                        self.set_attendance_date_today(vars_dict[key], display_var)
            except (ValueError, TypeError):
                # Invalid date, reset to today
                self.set_attendance_date_today(vars_dict[key], display_var)
        
        display_var.trace("w", sync_date_formats)
        
        # Helper text
        helper_text = ctk.CTkLabel(
            field_frame,
            text="Format: dd/mm/yy (e.g., 13/09/25) - Click 📅 for calendar or type date",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        helper_text.pack(anchor="w", pady=(5, 0))
        
        # Store display variable for later access
        if not hasattr(self, 'attendance_display_vars'):
            self.attendance_display_vars = {}
        self.attendance_display_vars[key] = display_var
    
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
        
        # Hour dropdown (12-hour format) - Start with placeholder
        ctk.CTkLabel(time_input_frame, text="Hour:", font=ctk.CTkFont(size=11)).pack(side="left")
        hour_var = tk.StringVar(value="--")
        hour_combo = ctk.CTkComboBox(
            time_input_frame,
            variable=hour_var,
            values=["--"] + [f"{i:02d}" for i in range(1, 13)],  # Add placeholder option
            width=70,
            height=35,
            corner_radius=6
        )
        hour_combo.pack(side="left", padx=(5, 10))
        
        # Minute dropdown - Start with placeholder
        ctk.CTkLabel(time_input_frame, text="Min:", font=ctk.CTkFont(size=11)).pack(side="left")
        minute_var = tk.StringVar(value="--")
        minute_combo = ctk.CTkComboBox(
            time_input_frame,
            variable=minute_var,
            values=["--"] + [f"{i:02d}" for i in range(0, 60, 15)],  # Add placeholder option
            width=70,
            height=35,
            corner_radius=6
        )
        minute_combo.pack(side="left", padx=(5, 10))
        
        # AM/PM dropdown - Start with placeholder
        ctk.CTkLabel(time_input_frame, text="AM/PM:", font=ctk.CTkFont(size=11)).pack(side="left")
        ampm_var = tk.StringVar(value="--")
        ampm_combo = ctk.CTkComboBox(
            time_input_frame,
            variable=ampm_var,
            values=["--", "AM", "PM"],  # Add placeholder option
            width=70,
            height=35,
            corner_radius=6
        )
        ampm_combo.pack(side="left", padx=(5, 20))
        
        # Quick time buttons - arranged in a more accessible way
        quick_times_frame = ctk.CTkFrame(time_container, fg_color="transparent")
        quick_times_frame.pack(anchor="w", pady=(10, 0))
        
        ctk.CTkLabel(quick_times_frame, text="Quick Select:", font=ctk.CTkFont(size=11)).pack(anchor="w")
        
        # Row of time buttons with better spacing
        buttons_frame = ctk.CTkFrame(quick_times_frame, fg_color="transparent")
        buttons_frame.pack(anchor="w", pady=(5, 0))
        
        quick_times = [
            ("7:00 AM", "07", "00", "AM"),
            ("12:00 PM", "12", "00", "PM"), 
            ("5:00 PM", "05", "00", "PM"),
            ("Now", *self.get_current_12hour_time())
        ]
        
        for btn_text, hour_val, min_val, ampm_val in quick_times:
            time_btn = ctk.CTkButton(
                buttons_frame,
                text=btn_text,
                command=lambda h=hour_val, m=min_val, ap=ampm_val, h_var=hour_var, m_var=minute_var, ap_var=ampm_var: self.set_12hour_time(h, m, ap, h_var, m_var, ap_var),
                width=80,
                height=32,
                corner_radius=6,
                font=ctk.CTkFont(size=11)
            )
            time_btn.pack(side="left", padx=(0, 8))
        
        # Combine hour, minute, and AM/PM into 24-hour time string for database storage
        vars_dict[key] = tk.StringVar()
        
        def update_time(*args):
            try:
                hour_str = hour_var.get()
                minute_str = minute_var.get()
                ampm = ampm_var.get()
                
                # If any field is placeholder, set to empty
                if hour_str == "--" or minute_str == "--" or ampm == "--":
                    vars_dict[key].set("")
                    return
                
                hour = int(hour_str)
                minute = minute_str
                
                # Convert 12-hour to 24-hour format for storage
                if ampm == "AM":
                    if hour == 12:
                        hour_24 = 0
                    else:
                        hour_24 = hour
                else:  # PM
                    if hour == 12:
                        hour_24 = 12
                    else:
                        hour_24 = hour + 12
                
                time_str = f"{hour_24:02d}:{minute}"
                vars_dict[key].set(time_str)
            except (ValueError, TypeError):
                vars_dict[key].set("")  # Set empty instead of default
        
        hour_var.trace("w", update_time)
        minute_var.trace("w", update_time)
        ampm_var.trace("w", update_time)
        update_time()  # Initial value
        
        # Helper text
        helper_text = ctk.CTkLabel(
            field_frame,
            text="Select time using dropdowns or quick buttons (12-hour format)",
            font=ctk.CTkFont(size=10)
        )
        helper_text.pack(anchor="w", pady=(8, 0))
        
        # Return widgets for potential disabling
        return {
            'hour_combo': hour_combo,
            'minute_combo': minute_combo,
            'ampm_combo': ampm_combo,
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
        """Handle status change to enable/disable time fields and overtime hours"""
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
            
            # Exception hours are always enabled and editable
            # No special handling needed for exception hours field
                    
        except Exception as e:
            logger.error(f"Error handling status change: {e}")
    
    def create_exception_hour_field(self, parent, label, key, vars_dict):
        """Create exception hour field that's always enabled with default value 1"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)

        # Label
        label_widget = ctk.CTkLabel(
            field_frame,
            text=f"{label}",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_widget.pack(anchor="w", pady=(0, 5))

        # Entry field with default value 1 (always)
        vars_dict[key] = tk.StringVar(value="1")
        self.exception_hour_widget = ctk.CTkEntry(
            field_frame,
            textvariable=vars_dict[key],
            width=300,
            height=35,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=12),
            placeholder_text="Exception hours (default: 1)"
        )
        self.exception_hour_widget.pack(fill="x", pady=(0, 5))
        
        # Ensure the field always shows 1 if empty
        def on_focus_out(event=None):
            current_value = vars_dict[key].get().strip()
            if not current_value or current_value == "":
                vars_dict[key].set("1")
        
        self.exception_hour_widget.bind("<FocusOut>", on_focus_out)
        self.exception_hour_widget.bind("<KeyRelease>", lambda e: on_focus_out() if vars_dict[key].get().strip() == "" else None)

        # Helper text
        helper_text = ctk.CTkLabel(
            field_frame,
            text="Hours when employee is not actively working (breaks, meetings, etc.) - Default: 1",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        helper_text.pack(anchor="w")
    
    def create_overtime_hour_field(self, parent, label, key, vars_dict):
        """Create overtime hour field that's enabled only when status is Overtime"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=8)

        # Label
        label_widget = ctk.CTkLabel(
            field_frame,
            text=f"{label}",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_widget.pack(anchor="w", pady=(0, 5))

        # Entry field
        vars_dict[key] = tk.StringVar(value="0")
        self.overtime_hour_widget = ctk.CTkEntry(
            field_frame,
            textvariable=vars_dict[key],
            width=300,
            height=35,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=12),
            placeholder_text="Enter overtime hours (e.g., 2, 4)"
        )
        self.overtime_hour_widget.pack(fill="x", pady=(0, 5))
        
        # Initially disabled
        self.overtime_hour_widget.configure(state="disabled")

        # Helper text
        helper_text = ctk.CTkLabel(
            field_frame,
            text="Enabled only when status is 'Overtime'",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        helper_text.pack(anchor="w")
    
    def set_12hour_time(self, hour, minute, ampm, hour_var, minute_var, ampm_var):
        """Set time from button click in 12-hour format"""
        try:
            hour_var.set(hour)
            minute_var.set(minute)
            ampm_var.set(ampm)
        except Exception as e:
            logger.error(f"Error setting 12-hour time: {e}")
    
    def get_current_12hour_time(self):
        """Get current time in 12-hour format components"""
        try:
            now = datetime.now()
            hour = now.hour
            minute = now.minute
            
            # Convert to 12-hour format
            if hour == 0:
                hour_12 = 12
                ampm = "AM"
            elif hour < 12:
                hour_12 = hour
                ampm = "AM"
            elif hour == 12:
                hour_12 = 12
                ampm = "PM"
            else:
                hour_12 = hour - 12
                ampm = "PM"
            
            return f"{hour_12:02d}", f"{minute:02d}", ampm
        except Exception as e:
            logger.error(f"Error getting current 12-hour time: {e}")
            return "07", "00", "AM"
    
    def set_attendance_date_today(self, internal_var, display_var):
        """Set attendance date to today in both internal and display formats"""
        try:
            today = date.today()
            internal_var.set(today.strftime("%Y-%m-%d"))  # Internal format
            display_var.set(today.strftime("%d/%m/%y"))  # Display format
        except Exception as e:
            logger.error(f"Error setting today's date: {e}")
    
    def open_attendance_calendar(self, internal_var, display_var):
        """Open calendar picker for attendance date selection"""
        try:
            # Create calendar popup window
            cal_window = ctk.CTkToplevel(self.parent)
            cal_window.title("Select Date")
            cal_window.geometry("300x250")
            cal_window.transient(self.parent)
            cal_window.grab_set()
            
            # Center the window
            cal_window.update_idletasks()
            x = (cal_window.winfo_screenwidth() // 2) - (300 // 2)
            y = (cal_window.winfo_screenheight() // 2) - (250 // 2)
            cal_window.geometry(f"300x250+{x}+{y}")
            
            # Simple date selection frame
            main_frame = ctk.CTkFrame(cal_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title
            title_label = ctk.CTkLabel(main_frame, text="Select Date", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
            title_label.pack(pady=(10, 20))
            
            # Date selection frame
            date_select_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            date_select_frame.pack(pady=10)
            
            # Get current date from internal var or today
            current_date_str = internal_var.get()
            try:
                current_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
            except:
                current_date = date.today()
            
            # Day dropdown
            ctk.CTkLabel(date_select_frame, text="Day:").grid(row=0, column=0, padx=5, pady=5)
            day_var = tk.StringVar(value=str(current_date.day))
            day_combo = ctk.CTkComboBox(date_select_frame, variable=day_var, 
                                      values=[str(i) for i in range(1, 32)], width=60)
            day_combo.grid(row=0, column=1, padx=5, pady=5)
            
            # Month dropdown
            ctk.CTkLabel(date_select_frame, text="Month:").grid(row=0, column=2, padx=5, pady=5)
            month_var = tk.StringVar(value=str(current_date.month))
            month_combo = ctk.CTkComboBox(date_select_frame, variable=month_var,
                                        values=[str(i) for i in range(1, 13)], width=60)
            month_combo.grid(row=0, column=3, padx=5, pady=5)
            
            # Year dropdown  
            ctk.CTkLabel(date_select_frame, text="Year:").grid(row=1, column=0, padx=5, pady=5)
            current_year = current_date.year
            years = [str(year) for year in range(current_year-2, current_year+3)]
            year_var = tk.StringVar(value=str(current_date.year))
            year_combo = ctk.CTkComboBox(date_select_frame, variable=year_var, 
                                       values=years, width=80)
            year_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
            
            # Buttons frame
            btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            btn_frame.pack(pady=20)
            
            def apply_date():
                try:
                    selected_date = date(int(year_var.get()), int(month_var.get()), int(day_var.get()))
                    internal_var.set(selected_date.strftime("%Y-%m-%d"))
                    display_var.set(selected_date.strftime("%d/%m/%y"))
                    cal_window.destroy()
                except ValueError:
                    # Invalid date selected
                    error_label = ctk.CTkLabel(main_frame, text="Invalid date selected!", 
                                             text_color="red", font=ctk.CTkFont(size=10))
                    error_label.pack(pady=5)
                    cal_window.after(2000, error_label.destroy)
            
            # Apply button
            apply_btn = ctk.CTkButton(btn_frame, text="Select", command=apply_date, width=80)
            apply_btn.pack(side="left", padx=5)
            
            # Cancel button
            cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", 
                                     command=cal_window.destroy, width=80,
                                     fg_color="gray", hover_color="darkgray")
            cancel_btn.pack(side="left", padx=5)
            
        except Exception as e:
            logger.error(f"Error opening calendar: {e}")
            # Fallback to today
            self.set_attendance_date_today(internal_var, display_var)
    
    def darken_color(self, color):
        """Darken a hex color for hover effect"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * 0.8) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    def create_sales_orders_content(self, parent):
        """Create comprehensive sales management with orders and transactions"""
        # Main header with vibrant colors
        header_frame = ctk.CTkFrame(parent, height=100, corner_radius=15, 
                                   fg_color=("#e8f5e8", "#1a4d1a"))
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=25, pady=20)
        
        # Title with green accent
        title_label = ctk.CTkLabel(
            header_content,
            text="🛍️ Sales Management System",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#2e7d32", "#66bb6a")
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_content,
            text="Manage Orders • Track Payments • Monitor Transactions",
            font=ctk.CTkFont(size=14),
            text_color=("#388e3c", "#81c784")
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Main control panel with action buttons
        control_frame = ctk.CTkFrame(parent, height=80, corner_radius=12,
                                   fg_color=("#f3e5f5", "#2d1b2e"))
        control_frame.pack(fill="x", padx=20, pady=(0, 15))
        control_frame.pack_propagate(False)
        
        button_container = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_container.pack(expand=True, pady=15)
        
        # Add New Order Button
        add_order_btn = ctk.CTkButton(
            button_container,
            text="📝 Add New Order",
            command=self.show_new_order_form,
            width=130,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20"),
            text_color="white"
        )
        add_order_btn.pack(side="left", padx=(0, 10))
        
        # Manage Orders Button
        manage_btn = ctk.CTkButton(
            button_container,
            text="📊 Manage Orders",
            command=self.show_orders_management,
            width=130,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#2196f3", "#1565c0"),
            hover_color=("#1976d2", "#0d47a1"),
            text_color="white"
        )
        manage_btn.pack(side="left", padx=(0, 10))
        
        # Customer Management Button (NEW)
        customer_btn = ctk.CTkButton(
            button_container,
            text="👥 Manage Customers",
            command=self.show_customer_management,
            width=130,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#673ab7", "#512da8"),
            hover_color=("#5e35b1", "#4527a0"),
            text_color="white"
        )
        customer_btn.pack(side="left", padx=(0, 10))
        
        # Payment Collection Button
        payment_btn = ctk.CTkButton(
            button_container,
            text="💰 Collect Payments",
            command=self.show_payment_collection,
            width=130,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#9c27b0", "#6a1b9a"),
            hover_color=("#8e24aa", "#4a148c"),
            text_color="white"
        )
        payment_btn.pack(side="left", padx=(0, 10))
        
        # Transactions History Button
        transactions_btn = ctk.CTkButton(
            button_container,
            text="💳 Transaction History",
            command=self.show_transactions_view,
            width=130,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#ff9800", "#e65100"),
            hover_color=("#f57c00", "#bf360c"),
            text_color="white"
        )
        transactions_btn.pack(side="left")
        
        # Dynamic content area
        self.sales_content_frame = ctk.CTkFrame(parent, corner_radius=12,
                                               fg_color=("white", "gray17"))
        self.sales_content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Initialize with orders management view
        self.current_sales_view = "orders"
        self.show_orders_management()
    
    def show_new_order_form(self):
        """Display COMPLETE TAKEOVER new order creation form"""
        # COMPLETE TAKEOVER: Hide all existing sales tab content and navigation
        self.clear_sales_content()
        self.current_sales_view = "new_order"
        
        # Find the parent container (the entire data management area)
        data_parent = self.sales_content_frame.master
        
        # Hide the existing sales tab structure (buttons + content frame)
        for widget in data_parent.winfo_children():
            widget.pack_forget()
        
        # Create COMPLETE takeover container - takes ENTIRE data management area
        self.complete_takeover_container = ctk.CTkFrame(data_parent, corner_radius=0,
                                                       fg_color=("white", "gray17"))
        self.complete_takeover_container.pack(fill="both", expand=True)
        
        # Header with back button - minimal height
        header_frame = ctk.CTkFrame(self.complete_takeover_container, height=60, corner_radius=0,
                                   fg_color=("#4caf50", "#2e7d32"))
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Back button and title on same line
        ctk.CTkButton(
            header_content,
            text="← Back to Sales",
            command=self.restore_sales_tab,
            width=140,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("white", "gray25"),
            text_color=("#2e7d32", "white"),
            hover_color=("#f5f5f5", "gray35")
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_content,
            text="📝 Create New Order",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=(30, 0))
        
        # Maximized form area - full remaining space
        form_container = ctk.CTkFrame(self.complete_takeover_container, corner_radius=0,
                                     fg_color=("white", "gray20"))
        form_container.pack(fill="both", expand=True)
        
        # Large scrollable form
        form_scroll = ctk.CTkScrollableFrame(form_container, corner_radius=0)
        form_scroll.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Initialize order form variables
        self.order_vars = {}
        
        # Customer Information - Large fields
        customer_grid = ctk.CTkFrame(form_scroll, fg_color="transparent")
        customer_grid.pack(fill="x", pady=(0, 20))
        customer_grid.grid_columnconfigure((0, 1), weight=1)
        
        # Create customer name combobox with auto-fill functionality
        self.create_customer_name_combo(customer_grid, row=0, col=0)
        self.create_large_field(customer_grid, "Phone Number", "customer_phone", "text", 
                               self.order_vars, placeholder="e.g., +91 9876543210", row=0, col=1)
        
        self.create_large_field(form_scroll, "Customer Address", "customer_address", "text", 
                               self.order_vars, placeholder="Enter delivery address (optional)", required=False, full_width=True)
        
        # Order Details - Large fields
        order_grid = ctk.CTkFrame(form_scroll, fg_color="transparent")
        order_grid.pack(fill="x", pady=(20, 20))
        order_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.create_large_field(order_grid, "Item Name", "item_name", "text", 
                               self.order_vars, placeholder="Product/service name", row=0, col=0)
        self.create_large_field(order_grid, "Quantity", "quantity", "number", 
                               self.order_vars, placeholder="Qty", row=0, col=1)
        self.create_large_field(order_grid, "Unit Price (₹)", "unit_price", "number", 
                               self.order_vars, placeholder="Price per unit", row=0, col=2)
        
        # Payment Information - Large fields
        payment_grid = ctk.CTkFrame(form_scroll, fg_color="transparent")
        payment_grid.pack(fill="x", pady=(20, 20))
        payment_grid.grid_columnconfigure((0, 1), weight=1)
        
        self.create_large_field(payment_grid, "Advance Payment (₹)", "advance_payment", "number", 
                               self.order_vars, placeholder="Amount paid in advance (optional)", required=False, row=0, col=0)
        self.create_large_field(payment_grid, "Due Date", "due_date", "date", 
                               self.order_vars, placeholder=date.today().strftime("%d/%m/%y"), row=0, col=1)
        
        # Payment method selection - Large
        method_grid = ctk.CTkFrame(form_scroll, fg_color="transparent")
        method_grid.pack(fill="x", pady=(20, 30))
        method_grid.grid_columnconfigure((0, 1), weight=1)
        
        payment_method_options = ["Cash", "Card", "UPI", "Bank Transfer", "Cheque"]
        self.create_large_combo(method_grid, "Payment Method", "payment_method", 
                               payment_method_options, self.order_vars, row=0, col=0)
        
        # Auto-calculated display fields - Large
        calc_grid = ctk.CTkFrame(form_scroll, fg_color="transparent")
        calc_grid.pack(fill="x", pady=(30, 40))
        calc_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total Amount (auto-calculated) - Larger display
        total_frame = ctk.CTkFrame(calc_grid, fg_color="transparent")
        total_frame.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        ctk.CTkLabel(total_frame, text="Total Amount", 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("gray40", "gray70")).pack(anchor="w")
        self.total_amount_display = ctk.CTkLabel(
            total_frame, 
            text="₹0.00", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1976d2", "#64b5f6"),
            height=50,
            corner_radius=10,
            fg_color=("white", "gray25")
        )
        self.total_amount_display.pack(fill="x", pady=(5, 0))
        
        # Due Amount (auto-calculated) - Larger display
        due_frame = ctk.CTkFrame(calc_grid, fg_color="transparent")
        due_frame.grid(row=0, column=1, padx=(5, 5), sticky="ew")
        
        ctk.CTkLabel(due_frame, text="Due Amount", 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("gray40", "gray70")).pack(anchor="w")
        self.due_amount_display = ctk.CTkLabel(
            due_frame, 
            text="₹0.00", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#f44336", "#ef5350"),
            height=50,
            corner_radius=10,
            fg_color=("white", "gray25")
        )
        self.due_amount_display.pack(fill="x", pady=(5, 0))
        
        # Order Status (auto-determined) - Larger display
        status_frame = ctk.CTkFrame(calc_grid, fg_color="transparent")
        status_frame.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        
        ctk.CTkLabel(status_frame, text="Order Status", 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("gray40", "gray70")).pack(anchor="w")
        self.order_status_display = ctk.CTkLabel(
            status_frame, 
            text="Incomplete", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#ff9800", "#ffb74d"),
            height=50,
            corner_radius=10,
            fg_color=("white", "gray25")
        )
        self.order_status_display.pack(fill="x", pady=(5, 0))
        
        # Large action buttons
        self.create_large_order_buttons(form_scroll)
    
    def create_minimal_section(self, parent, title):
        """Create minimal section header"""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        section_frame.pack(fill="x", pady=(10, 8))
        section_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#1976d2", "#64b5f6")
        ).pack(anchor="w", pady=5)
        
        # Simple line divider
        divider = ctk.CTkFrame(section_frame, height=1, fg_color=("gray70", "gray40"))
        divider.pack(fill="x", pady=(2, 0))
    
    def create_simple_field(self, parent, label, key, field_type, vars_dict, placeholder="", required=True, row=0, col=0, full_width=False):
        """Create simple form field"""
        if full_width:
            field_container = ctk.CTkFrame(parent, fg_color="transparent")
            field_container.pack(fill="x", pady=8)
        else:
            field_container = ctk.CTkFrame(parent, fg_color="transparent")
            field_container.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
        
        # Label
        label_text = f"{label}{'*' if required else ''}"
        label_widget = ctk.CTkLabel(
            field_container,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray20", "gray80")
        )
        label_widget.pack(anchor="w", pady=(0, 4))
        
        # Input field
        vars_dict[key] = tk.StringVar()
        
        entry = ctk.CTkEntry(
            field_container,
            textvariable=vars_dict[key],
            placeholder_text=placeholder,
            height=35,
            corner_radius=8,
            border_width=1,
            font=ctk.CTkFont(size=12)
        )
        entry.pack(fill="x")
        
        # Bind calculation for relevant fields
        if key in ['quantity', 'unit_price', 'advance_payment']:
            entry.bind('<KeyRelease>', self.calculate_order_totals)
            entry.bind('<FocusOut>', self.calculate_order_totals)
        
        return entry
    
    def create_simple_combo(self, parent, label, key, options, vars_dict, required=True, row=0, col=0):
        """Create simple combo box"""
        field_container = ctk.CTkFrame(parent, fg_color="transparent")
        field_container.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
        
        # Label
        label_text = f"{label}{'*' if required else ''}"
        label_widget = ctk.CTkLabel(
            field_container,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray20", "gray80")
        )
        label_widget.pack(anchor="w", pady=(0, 4))
        
        # Combo box
        vars_dict[key] = tk.StringVar(value=options[0] if options else "")
        combo = ctk.CTkComboBox(
            field_container,
            values=options,
            variable=vars_dict[key],
            height=35,
            corner_radius=8,
            border_width=1,
            font=ctk.CTkFont(size=12)
        )
        combo.pack(fill="x")
        
        return combo
    
    def create_simple_order_buttons(self, parent):
        """Create simple action buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        button_frame.pack(fill="x", pady=(30, 20))
        button_frame.pack_propagate(False)
        
        buttons_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        buttons_container.pack(expand=True)
        
        # Create Order button
        create_btn = ctk.CTkButton(
            buttons_container,
            text="💾 Create Order",
            command=self.create_new_order,
            width=150,
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20")
        )
        create_btn.pack(side="left", padx=(0, 15))
        
        # Clear Form button
        clear_btn = ctk.CTkButton(
            buttons_container,
            text="🗑️ Clear Form",
            command=self.clear_order_form,
            width=130,
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#ff9800", "#e65100"),
            hover_color=("#f57c00", "#bf360c")
        )
        clear_btn.pack(side="left")
    
    def create_large_field(self, parent, label, key, field_type, vars_dict, placeholder="", required=True, row=0, col=0, full_width=False):
        """Create large form field for full-tab experience"""
        if full_width:
            field_container = ctk.CTkFrame(parent, fg_color="transparent")
            field_container.pack(fill="x", pady=12)
        else:
            field_container = ctk.CTkFrame(parent, fg_color="transparent")
            field_container.grid(row=row, column=col, padx=12, pady=12, sticky="ew")
        
        # Large label
        label_text = f"{label}{'*' if required else ''}"
        label_widget = ctk.CTkLabel(
            field_container,
            text=label_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray20", "gray80")
        )
        label_widget.pack(anchor="w", pady=(0, 6))
        
        # Special handling for date fields
        if field_type == "date":
            return self.create_date_picker_field(field_container, key, vars_dict, placeholder)
        
        # Large input field for other types
        vars_dict[key] = tk.StringVar()
        
        entry = ctk.CTkEntry(
            field_container,
            textvariable=vars_dict[key],
            placeholder_text=placeholder,
            height=45,
            corner_radius=10,
            border_width=2,
            font=ctk.CTkFont(size=14)
        )
        entry.pack(fill="x")
        
        # Bind calculation for relevant fields
        if key in ['quantity', 'unit_price', 'advance_payment']:
            entry.bind('<KeyRelease>', self.calculate_order_totals)
            entry.bind('<FocusOut>', self.calculate_order_totals)
        
        return entry
    
    def create_date_picker_field(self, parent, key, vars_dict, placeholder=""):
        """Create date picker field with calendar popup"""
        from datetime import date
        
        # Initialize variable
        vars_dict[key] = tk.StringVar()
        if placeholder:
            vars_dict[key].set(placeholder)
        else:
            vars_dict[key].set(date.today().strftime("%d/%m/%y"))
        
        # Container for entry and button
        date_container = ctk.CTkFrame(parent, fg_color="transparent")
        date_container.pack(fill="x")
        date_container.grid_columnconfigure(0, weight=1)
        
        # Date entry field
        date_entry = ctk.CTkEntry(
            date_container,
            textvariable=vars_dict[key],
            placeholder_text="dd/mm/yy",
            height=45,
            corner_radius=10,
            border_width=2,
            font=ctk.CTkFont(size=14)
        )
        date_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Calendar button
        calendar_btn = ctk.CTkButton(
            date_container,
            text="📅",
            width=45,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(size=16),
            command=lambda: self.show_sales_calendar(vars_dict[key])
        )
        calendar_btn.grid(row=0, column=1)
        
        return date_entry
    
    def show_calendar_popup(self, date_var):
        """Show calendar popup for date selection - now using modular calendar widget"""
        # This method is deprecated - using DateFieldWithCalendar instead
        pass
    
    def create_large_combo(self, parent, label, key, options, vars_dict, required=True, row=0, col=0):
        """Create large combo box for full-tab experience"""
        field_container = ctk.CTkFrame(parent, fg_color="transparent")
        field_container.grid(row=row, column=col, padx=12, pady=12, sticky="ew")
        
        # Large label
        label_text = f"{label}{'*' if required else ''}"
        label_widget = ctk.CTkLabel(
            field_container,
            text=label_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray20", "gray80")
        )
        label_widget.pack(anchor="w", pady=(0, 6))
        
        # Large combo box
        vars_dict[key] = tk.StringVar(value=options[0] if options else "")
        combo = ctk.CTkComboBox(
            field_container,
            values=options,
            variable=vars_dict[key],
            height=45,
            corner_radius=10,
            border_width=2,
            font=ctk.CTkFont(size=14)
        )
        combo.pack(fill="x")
        
        return combo
    
    def create_customer_name_combo(self, parent, row=0, col=0):
        """Create customer name combobox with auto-fill functionality"""
        field_container = ctk.CTkFrame(parent, fg_color="transparent")
        field_container.grid(row=row, column=col, padx=12, pady=12, sticky="ew")
        
        # Label
        label_widget = ctk.CTkLabel(
            field_container,
            text="Customer Name *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray20", "gray80")
        )
        label_widget.pack(anchor="w", pady=(0, 6))
        
        # Get customer names for dropdown
        try:
            # Use order_service for customer data if available, otherwise fall back to data_service
            service = self.order_service if self.order_service else self.data_service
            customers_df = service.get_customers()
            customer_names = [""] + customers_df['name'].tolist() if not customers_df.empty else [""]
        except:
            customer_names = [""]
        
        # Initialize variable
        self.order_vars["customer_name"] = tk.StringVar()
        
        # Create combobox
        self.customer_name_combo = ctk.CTkComboBox(
            field_container,
            values=customer_names,
            variable=self.order_vars["customer_name"],
            height=45,
            corner_radius=10,
            border_width=2,
            font=ctk.CTkFont(size=14),
            command=self.on_customer_selected
        )
        self.customer_name_combo.pack(fill="x")
        
        # Bind events for typing functionality
        self.customer_name_combo.bind('<KeyRelease>', self.on_customer_name_typed)
        self.customer_name_combo.bind('<FocusOut>', self.on_customer_focus_out)
        
        return self.customer_name_combo
    
    def on_customer_selected(self, selected_name):
        """Handle customer selection from dropdown"""
        if not selected_name or selected_name == "":
            return
        
        try:
            # Get customer details using order_service if available
            service = self.order_service if self.order_service else self.data_service
            customer = service.get_customer_by_name(selected_name)
            if customer:
                # Auto-fill customer information
                self.order_vars["customer_phone"].set(customer.get('contact_number', ''))
                self.order_vars["customer_address"].set(customer.get('address', ''))
                
        except Exception as e:
            logger.error(f"Error loading customer details: {str(e)}")
    
    def on_customer_name_typed(self, event):
        """Handle typing in customer name field"""
        # Allow users to type new customer names
        pass
    
    def on_customer_focus_out(self, event):
        """Handle when customer name field loses focus"""
        typed_name = self.order_vars["customer_name"].get().strip()
        if typed_name and typed_name not in [combo_value for combo_value in self.customer_name_combo.cget("values")]:
            # This is a new customer name - we'll add it to the database when the order is created
            pass

    def create_large_order_buttons(self, parent):
        """Create large action buttons for full-tab experience"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent", height=80)
        button_frame.pack(fill="x", pady=(40, 30))
        button_frame.pack_propagate(False)
        
        buttons_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        buttons_container.pack(expand=True)
        
        # Create Order button - Large
        create_btn = ctk.CTkButton(
            buttons_container,
            text="💾 Create Order",
            command=self.create_new_order,
            width=180,
            height=55,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20")
        )
        create_btn.pack(side="left", padx=(0, 20))
        
        # Clear Form button - Large
        clear_btn = ctk.CTkButton(
            buttons_container,
            text="🗑️ Clear Form",
            command=self.clear_order_form,
            width=150,
            height=55,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#ff9800", "#e65100"),
            hover_color=("#f57c00", "#bf360c")
        )
        clear_btn.pack(side="left")
    
    def create_compact_form_section(self, parent, title):
        """Create a compact form section header"""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent", height=35)
        section_frame.pack(fill="x", pady=(15, 5))
        section_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['primary']
        ).pack(anchor="w", pady=8)
        
        # Divider line
        divider = ctk.CTkFrame(section_frame, height=1, fg_color=("gray80", "gray30"))
        divider.pack(fill="x", pady=(2, 0))
    
    def create_compact_field(self, parent, label, key, field_type, vars_dict, placeholder="", required=True, row=0, col=0, full_width=False):
        """Create compact form field for better space utilization"""
        if full_width:
            field_container = ctk.CTkFrame(parent, fg_color="transparent")
            field_container.pack(fill="x", pady=5)
        else:
            field_container = ctk.CTkFrame(parent, fg_color="transparent")
            field_container.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Compact label
        label_widget = ctk.CTkLabel(
            field_container,
            text=f"{label}{'*' if required else ''}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray10", "gray90")
        )
        label_widget.pack(anchor="w", pady=(0, 3))
        
        # Input field
        vars_dict[key] = tk.StringVar()
        
        entry = ctk.CTkEntry(
            field_container,
            textvariable=vars_dict[key],
            placeholder_text=placeholder,
            height=32,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=11)
        )
        entry.pack(fill="x")
        
        # Bind events for real-time calculation
        if key in ['quantity', 'unit_price', 'advance_payment']:
            entry.bind('<KeyRelease>', self.calculate_order_totals)
        
        return entry
    
    def create_compact_combo(self, parent, label, key, options, vars_dict, required=True, row=0, col=0):
        """Create compact combo box"""
        field_container = ctk.CTkFrame(parent, fg_color="transparent")
        field_container.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Label
        label_widget = ctk.CTkLabel(
            field_container,
            text=f"{label}{'*' if required else ''}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray10", "gray90")
        )
        label_widget.pack(anchor="w", pady=(0, 3))
        
        # Combo box
        vars_dict[key] = tk.StringVar(value=options[0] if options else "")
        combo = ctk.CTkComboBox(
            field_container,
            values=options,
            variable=vars_dict[key],
            height=32,
            corner_radius=6,
            border_width=1,
            font=ctk.CTkFont(size=11),
            dropdown_font=ctk.CTkFont(size=10)
        )
        combo.pack(fill="x")
        
        return combo
    
    def create_compact_order_form_buttons(self, parent):
        """Create compact form buttons"""
        button_container = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        button_container.pack(fill="x", pady=(20, 10))
        button_container.pack_propagate(False)
        
        button_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        button_frame.pack(expand=True)
        
        # Create Order button
        create_btn = ctk.CTkButton(
            button_frame,
            text="💾 Create Order",
            command=self.create_new_order,
            width=120,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20")
        )
        create_btn.pack(side="left", padx=(0, 10))
        
        # Clear Form button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear",
            command=self.clear_order_form,
            width=100,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#ff9800", "#e65100"),
            hover_color=("#f57c00", "#bf360c")
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        # Back button
        back_btn = ctk.CTkButton(
            button_frame,
            text="↩️ Back",
            command=self.show_orders_management,
            width=100,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#607d8b", "#37474f"),
            hover_color=("#546e7a", "#263238")
        )
        back_btn.pack(side="left")
    
    def create_order_summary_panel(self, parent):
        """Create order summary panel on the right side"""
        # Header
        summary_header = ctk.CTkFrame(parent, height=40, corner_radius=8,
                                     fg_color=("#e8f5e8", "#1a4d1a"))
        summary_header.pack(fill="x", padx=10, pady=(15, 10))
        summary_header.pack_propagate(False)
        
        ctk.CTkLabel(
            summary_header,
            text="📊 Order Summary",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#2e7d32", "#66bb6a")
        ).pack(pady=10)
        
        # Summary content
        self.summary_content = ctk.CTkFrame(parent, fg_color="transparent")
        self.summary_content.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        # Initialize summary display
        self.update_order_summary()
    
    def calculate_order_totals(self, event=None):
        """Calculate order totals and auto-determine status in real-time"""
        try:
            quantity = float(self.order_vars.get('quantity', tk.StringVar()).get() or 0)
            unit_price = float(self.order_vars.get('unit_price', tk.StringVar()).get() or 0)
            advance = float(self.order_vars.get('advance_payment', tk.StringVar()).get() or 0)
            
            total_amount = quantity * unit_price
            due_amount = max(0, total_amount - advance)  # Ensure due amount is not negative
            
            # Auto-determine order status based on payment
            if due_amount <= 0 and total_amount > 0:
                order_status = "Complete"
                status_color = ("#4caf50", "#81c784")  # Green
            else:
                order_status = "Incomplete"
                status_color = ("#ff9800", "#ffb74d")  # Orange
            
            # Update display fields
            if hasattr(self, 'total_amount_display'):
                self.total_amount_display.configure(text=f"₹{total_amount:.2f}")
            
            if hasattr(self, 'due_amount_display'):
                self.due_amount_display.configure(text=f"₹{due_amount:.2f}")
            
            if hasattr(self, 'order_status_display'):
                self.order_status_display.configure(text=order_status, text_color=status_color)
            
        except ValueError:
            # Reset displays if invalid input
            if hasattr(self, 'total_amount_display'):
                self.total_amount_display.configure(text="₹0.00")
            if hasattr(self, 'due_amount_display'):
                self.due_amount_display.configure(text="₹0.00")
            if hasattr(self, 'order_status_display'):
                self.order_status_display.configure(text="Incomplete", text_color=("#ff9800", "#ffb74d"))
            
        except (ValueError, AttributeError):
            self.update_order_summary()
    
    def update_order_summary(self, total=0, advance=0, due=0):
        """Update the order summary panel"""
        # Clear existing content
        for widget in self.summary_content.winfo_children():
            widget.destroy()
        
        # Summary items
        summary_items = [
            ("Total Amount", f"₹{total:.2f}", "#2196f3"),
            ("Advance Payment", f"₹{advance:.2f}", "#4caf50"),
            ("Due Amount", f"₹{due:.2f}", "#ff9800" if due > 0 else "#4caf50")
        ]
        
        for label, value, color in summary_items:
            item_frame = ctk.CTkFrame(self.summary_content, corner_radius=8,
                                    fg_color=("white", "gray30"))
            item_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(item_frame, text=label, font=ctk.CTkFont(size=11)).pack(pady=(8, 2))
            ctk.CTkLabel(item_frame, text=value, font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=color).pack(pady=(0, 8))
    
    def create_order_form_buttons(self, parent):
        """Create enhanced form buttons for order creation"""
        button_container = ctk.CTkFrame(parent, fg_color="transparent", height=80)
        button_container.pack(fill="x", pady=(30, 20))
        button_container.pack_propagate(False)
        
        button_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        button_frame.pack(expand=True)
        
        # Create Order button
        create_btn = ctk.CTkButton(
            button_frame,
            text="💾 Create Order",
            command=self.create_new_order,
            width=160,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20")
        )
        create_btn.pack(side="left", padx=(0, 15))
        
        # Clear Form button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear Form",
            command=self.clear_order_form,
            width=160,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("#ff9800", "#e65100"),
            hover_color=("#f57c00", "#bf360c")
        )
        clear_btn.pack(side="left", padx=(0, 15))
        
        # Back to Orders button
        back_btn = ctk.CTkButton(
            button_frame,
            text="↩️ Back to Orders",
            command=self.show_orders_management,
            width=160,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("#607d8b", "#37474f"),
            hover_color=("#546e7a", "#263238")
        )
        back_btn.pack(side="left")
    
    def show_orders_management(self):
        """Display orders management interface"""
        self.clear_sales_content()
        self.current_sales_view = "orders"
        
        # Create two-section layout: Orders table and order details - Better spacing
        main_container = ctk.CTkFrame(self.sales_content_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Orders table section - Now expands to fill all space
        orders_section = ctk.CTkFrame(main_container, corner_radius=12,
                                     fg_color=("#f8f9fa", "gray19"))
        orders_section.pack(fill="both", expand=True, pady=(0, 10))
        
        # Orders header - More compact
        orders_header = ctk.CTkFrame(orders_section, height=45, corner_radius=10,
                                   fg_color=("#2196f3", "#1565c0"))
        orders_header.pack(fill="x", padx=15, pady=(10, 8))
        orders_header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(orders_header, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20, pady=10)
        
        ctk.CTkLabel(
            header_content,
            text="📋 Active Orders",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_content,
            text="🔄 Refresh",
            command=self.refresh_orders_table,
            width=100,
            height=35,
            corner_radius=8,
            fg_color=("white", "gray25"),
            text_color=("#2196f3", "white"),
            hover_color=("#f5f5f5", "gray30")
        )
        refresh_btn.pack(side="right")
        
        # Orders table - Now takes up all available space
        self.create_orders_table(orders_section)
    
    def create_orders_table(self, parent):
        """Create enhanced orders table with full width"""
        # Table container
        table_container = ctk.CTkFrame(parent, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create treeview for orders
        import tkinter as tk
        from tkinter import ttk
        
        # Style configuration for better appearance
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        style.configure("Treeview", font=('Arial', 10))
        
        # Create treeview with scrollbars
        tree_frame = tk.Frame(table_container, bg="#f8f9fa")
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("Order ID", "Customer", "Phone", "Item", "Quantity", "Total Amount", 
                  "Advance Paid", "Due Amount", "Status", "Due Date")
        
        self.orders_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column widths for full width utilization
        column_widths = {"Order ID": 100, "Customer": 150, "Phone": 120, "Item": 200, 
                        "Quantity": 80, "Total Amount": 120, "Advance Paid": 120, 
                        "Due Amount": 120, "Status": 100, "Due Date": 100}
        
        for col in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=column_widths.get(col, 100), minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.orders_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.orders_tree.xview)
        self.orders_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.orders_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Load orders data
        self.refresh_orders_table()
    
    def create_order_details_tabs(self, parent):
        """Create tabbed interface for order details and payment tracking"""
        # Tab header - More compact
        tab_header = ctk.CTkFrame(parent, height=40, corner_radius=10,
                                 fg_color=("#e1f5fe", "gray25"))
        tab_header.pack(fill="x", padx=15, pady=(10, 5))
        tab_header.pack_propagate(False)
        
        tab_buttons_frame = ctk.CTkFrame(tab_header, fg_color="transparent")
        tab_buttons_frame.pack(expand=True, pady=6)
        
        # Order Details Tab - Smaller buttons
        self.details_tab_btn = ctk.CTkButton(
            tab_buttons_frame,
            text="📄 Order Details",
            command=lambda: self.switch_details_tab("details"),
            width=130,
            height=28,
            corner_radius=8,
            fg_color=("#2196f3", "#1565c0"),
            hover_color=("#1976d2", "#0d47a1")
        )
        self.details_tab_btn.pack(side="left", padx=(0, 10))
        
        # Payments Tab - Smaller buttons
        self.payments_tab_btn = ctk.CTkButton(
            tab_buttons_frame,
            text="💳 Payments",
            command=lambda: self.switch_details_tab("payments"),
            width=130,
            height=28,
            corner_radius=8,
            fg_color=("#ff9800", "#e65100"),
            hover_color=("#f57c00", "#bf360c")
        )
        self.payments_tab_btn.pack(side="left")
        
        # Tab content area - Ensure proper minimum height
        self.details_content_frame = ctk.CTkFrame(parent, corner_radius=10, height=250,
                                                 fg_color=("white", "gray20"))
        self.details_content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.details_content_frame.pack_propagate(False)
        
        # Initialize with details tab
        self.current_details_tab = "details"
        self.switch_details_tab("details")
    
    def switch_details_tab(self, tab_name):
        """Switch between order details and payments tabs"""
        self.current_details_tab = tab_name
        
        # Clear current content
        for widget in self.details_content_frame.winfo_children():
            widget.destroy()
        
        if tab_name == "details":
            self.show_order_details_tab()
            # Update button colors
            self.details_tab_btn.configure(fg_color=("#2196f3", "#1565c0"))
            self.payments_tab_btn.configure(fg_color=("gray70", "gray40"))
        else:
            self.show_payments_tab()
            # Update button colors
            self.details_tab_btn.configure(fg_color=("gray70", "gray40"))
            self.payments_tab_btn.configure(fg_color=("#ff9800", "#e65100"))
    
    def show_order_details_tab(self):
        """Show selected order details"""
        if not hasattr(self, 'selected_order_id') or not self.selected_order_id:
            # No order selected message - Enhanced instructions
            message_frame = ctk.CTkFrame(self.details_content_frame, fg_color="transparent")
            message_frame.pack(expand=True, fill="both")
            
            instruction_container = ctk.CTkFrame(message_frame, corner_radius=15,
                                               fg_color=("#e3f2fd", "gray25"))
            instruction_container.pack(expand=True, fill="both", padx=30, pady=30)
            
            ctk.CTkLabel(
                instruction_container,
                text="📋 Order Details",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=("#1976d2", "#64b5f6")
            ).pack(pady=(30, 10))
            
            ctk.CTkLabel(
                instruction_container,
                text="� Click on any order in the table above\nto view detailed information here",
                font=ctk.CTkFont(size=14),
                text_color=("gray60", "gray50"),
                justify="center"
            ).pack(pady=(0, 30))
            return
        
        # Order details content
        details_scroll = ctk.CTkScrollableFrame(self.details_content_frame)
        details_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Get order data
        order_data = self.get_order_by_id(self.selected_order_id)
        if not order_data:
            return
        
        # Order Information Section
        self.create_info_section(details_scroll, "📋 Order Information", [
            ("Order ID", order_data.get('order_id', 'N/A')),
            ("Order Status", order_data.get('order_status', 'N/A')),
            ("Order Date", order_data.get('order_date', 'N/A')),
            ("Due Date", order_data.get('due_date', 'N/A'))
        ])
        
        # Customer Information Section
        self.create_info_section(details_scroll, "👤 Customer Information", [
            ("Customer Name", order_data.get('customer_name', 'N/A')),
            ("Phone Number", order_data.get('customer_phone', 'N/A')),
            ("Address", order_data.get('customer_address', 'N/A'))
        ])
        
        # Product Information Section
        self.create_info_section(details_scroll, "🛍️ Product Information", [
            ("Item Name", order_data.get('item_name', 'N/A')),
            ("Quantity", str(order_data.get('quantity', 0))),
            ("Unit Price", f"₹{order_data.get('unit_price', 0):.2f}"),
            ("Total Amount", f"₹{order_data.get('total_amount', 0):.2f}")
        ])
        
        # Payment Information Section
        advance = order_data.get('advance_payment', 0)
        total = order_data.get('total_amount', 0)
        due = total - advance
        
        self.create_info_section(details_scroll, "💰 Payment Information", [
            ("Total Amount", f"₹{total:.2f}"),
            ("Advance Paid", f"₹{advance:.2f}"),
            ("Due Amount", f"₹{due:.2f}"),
            ("Payment Method", order_data.get('payment_method', 'N/A'))
        ])
        
        # Action buttons
        self.create_order_action_buttons(details_scroll, order_data)
    
    def create_info_section(self, parent, title, data_pairs):
        """Create an information section with title and data pairs"""
        # Section header
        section_frame = ctk.CTkFrame(parent, corner_radius=10, 
                                   fg_color=("#f5f5f5", "gray25"))
        section_frame.pack(fill="x", pady=(0, 15))
        
        # Title
        title_frame = ctk.CTkFrame(section_frame, height=45, corner_radius=8,
                                  fg_color=("#e3f2fd", "#1a237e"))
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        title_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1976d2", "#64b5f6")
        ).pack(pady=12)
        
        # Data grid
        data_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        data_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        for i, (label, value) in enumerate(data_pairs):
            row_frame = ctk.CTkFrame(data_frame, height=35, corner_radius=5,
                                   fg_color=("white", "gray30"))
            row_frame.pack(fill="x", pady=2)
            row_frame.pack_propagate(False)
            
            # Configure grid
            row_frame.grid_columnconfigure(1, weight=1)
            
            # Label
            ctk.CTkLabel(
                row_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=150,
                anchor="w"
            ).grid(row=0, column=0, padx=(15, 10), pady=8, sticky="w")
            
            # Value
            ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).grid(row=0, column=1, padx=(0, 15), pady=8, sticky="w")
    
    def create_order_action_buttons(self, parent, order_data):
        """Create action buttons for order management"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        button_frame.pack(fill="x", pady=(20, 0))
        button_frame.pack_propagate(False)
        
        buttons_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        buttons_container.pack(expand=True, pady=15)
        
        # Edit Order button
        edit_btn = ctk.CTkButton(
            buttons_container,
            text="✏️ Edit Order",
            command=lambda: self.edit_order(order_data),
            width=130,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#2196f3", "#1565c0"),
            hover_color=("#1976d2", "#0d47a1")
        )
        edit_btn.pack(side="left", padx=(0, 10))
        
        # Update Status button
        status_btn = ctk.CTkButton(
            buttons_container,
            text="📊 Update Status",
            command=lambda: self.update_order_status(order_data),
            width=130,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#ff9800", "#e65100"),
            hover_color=("#f57c00", "#bf360c")
        )
        status_btn.pack(side="left", padx=(0, 10))
        
        # Delete Order button
        delete_btn = ctk.CTkButton(
            buttons_container,
            text="🗑️ Delete",
            command=lambda: self.delete_order(order_data),
            width=130,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#f44336", "#c62828"),
            hover_color=("#d32f2f", "#b71c1c")
        )
        delete_btn.pack(side="left")
    
    def show_payments_tab(self):
        """Show payments and transactions for selected order"""
        if not hasattr(self, 'selected_order_id') or not self.selected_order_id:
            # No order selected message - Enhanced instructions for payments
            message_frame = ctk.CTkFrame(self.details_content_frame, fg_color="transparent")
            message_frame.pack(expand=True, fill="both")
            
            instruction_container = ctk.CTkFrame(message_frame, corner_radius=15,
                                               fg_color=("#fff3e0", "gray25"))
            instruction_container.pack(expand=True, fill="both", padx=30, pady=30)
            
            ctk.CTkLabel(
                instruction_container,
                text="💳 Payment Tracking",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=("#f57c00", "#ffb74d")
            ).pack(pady=(30, 10))
            
            ctk.CTkLabel(
                instruction_container,
                text="� Select an order from the table above\nto view payment history and add new payments",
                font=ctk.CTkFont(size=14),
                text_color=("gray60", "gray50"),
                justify="center"
            ).pack(pady=(0, 30))
            return
        
        # Payments content
        payments_container = ctk.CTkFrame(self.details_content_frame, fg_color="transparent")
        payments_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Payment summary section
        summary_frame = ctk.CTkFrame(payments_container, height=120, corner_radius=10,
                                   fg_color=("#e8f5e8", "gray25"))
        summary_frame.pack(fill="x", pady=(0, 15))
        summary_frame.pack_propagate(False)
        
        self.create_payment_summary(summary_frame)
        
        # Add payment section
        add_payment_frame = ctk.CTkFrame(payments_container, height=80, corner_radius=10,
                                       fg_color=("#fff3e0", "gray25"))
        add_payment_frame.pack(fill="x", pady=(0, 15))
        add_payment_frame.pack_propagate(False)
        
        self.create_add_payment_section(add_payment_frame)
        
        # Transactions table
        transactions_frame = ctk.CTkFrame(payments_container, corner_radius=10,
                                        fg_color=("#f8f9fa", "gray25"))
        transactions_frame.pack(fill="both", expand=True)
        
        self.create_transactions_table(transactions_frame)
    
    def create_payment_summary(self, parent):
        """Create payment summary display"""
        order_data = self.get_order_by_id(self.selected_order_id)
        if not order_data:
            return
        
        total_amount = order_data.get('total_amount', 0)
        advance_payment = order_data.get('advance_payment', 0)
        due_amount = total_amount - advance_payment
        
        summary_content = ctk.CTkFrame(parent, fg_color="transparent")
        summary_content.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Title
        ctk.CTkLabel(
            summary_content,
            text="💰 Payment Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#2e7d32", "#66bb6a")
        ).pack(anchor="w", pady=(0, 10))
        
        # Payment info grid
        info_grid = ctk.CTkFrame(summary_content, fg_color="transparent")
        info_grid.pack(fill="x")
        
        # Configure grid columns
        info_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total Amount
        total_frame = ctk.CTkFrame(info_grid, corner_radius=8, fg_color=("white", "gray30"))
        total_frame.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        ctk.CTkLabel(total_frame, text="Total Amount", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(8, 2))
        ctk.CTkLabel(total_frame, text=f"₹{total_amount:.2f}", font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=("#1976d2", "#64b5f6")).pack(pady=(0, 8))
        
        # Paid Amount
        paid_frame = ctk.CTkFrame(info_grid, corner_radius=8, fg_color=("white", "gray30"))
        paid_frame.grid(row=0, column=1, padx=(5, 5), sticky="ew")
        
        ctk.CTkLabel(paid_frame, text="Advance Paid Amount", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(8, 2))
        ctk.CTkLabel(paid_frame, text=f"₹{advance_payment:.2f}", font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#4caf50", "#81c784")).pack(pady=(0, 8))
        
        # Due Amount
        due_frame = ctk.CTkFrame(info_grid, corner_radius=8, fg_color=("white", "gray30"))
        due_frame.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        
        ctk.CTkLabel(due_frame, text="Due Amount", font=ctk.CTkFont(size=11, weight="bold")).pack(pady=(8, 2))
        due_color = ("#f44336", "#ef5350") if due_amount > 0 else ("#4caf50", "#81c784")
        ctk.CTkLabel(due_frame, text=f"₹{due_amount:.2f}", font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=due_color).pack(pady=(0, 8))
    
    def create_add_payment_section(self, parent):
        """Create add payment interface"""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Title and form in horizontal layout
        form_container = ctk.CTkFrame(content, fg_color="transparent")
        form_container.pack(fill="x")
        
        # Title
        ctk.CTkLabel(
            form_container,
            text="💳 Add Payment",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#ff9800", "#ffb74d")
        ).pack(side="left", padx=(0, 20))
        
        # Payment amount entry
        self.payment_amount_var = tk.StringVar()
        amount_entry = ctk.CTkEntry(
            form_container,
            textvariable=self.payment_amount_var,
            placeholder_text="Enter amount",
            width=120,
            height=35,
            corner_radius=8
        )
        amount_entry.pack(side="left", padx=(0, 10))
        
        # Payment method combo
        self.payment_method_var = tk.StringVar(value="Cash")
        method_combo = ctk.CTkComboBox(
            form_container,
            values=["Cash", "Card", "UPI", "Bank Transfer", "Cheque"],
            variable=self.payment_method_var,
            width=120,
            height=35,
            corner_radius=8
        )
        method_combo.pack(side="left", padx=(0, 10))
        
        # Add payment button
        add_btn = ctk.CTkButton(
            form_container,
            text="➕ Add Payment",
            command=self.add_payment_transaction,
            width=120,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20")
        )
        add_btn.pack(side="left")
    
    def create_transactions_table(self, parent):
        """Create transactions history table"""
        # Header
        header_frame = ctk.CTkFrame(parent, height=50, corner_radius=8,
                                  fg_color=("#ff9800", "#e65100"))
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="📊 Transaction History",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Table container
        table_container = ctk.CTkFrame(parent, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create treeview for transactions
        import tkinter as tk
        from tkinter import ttk
        
        tree_frame = tk.Frame(table_container, bg="#f8f9fa")
        tree_frame.pack(fill="both", expand=True)
        
        trans_columns = ("Transaction ID", "Date", "Amount", "Payment Method", "Notes")
        
        self.transactions_tree = ttk.Treeview(tree_frame, columns=trans_columns, show="headings", height=8)
        
        # Configure columns
        col_widths = {"Transaction ID": 150, "Date": 120, "Amount": 100, "Payment Method": 120, "Notes": 200}
        for col in trans_columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=col_widths.get(col, 100))
        
        # Scrollbar
        trans_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=trans_scrollbar.set)
        
        self.transactions_tree.pack(side="left", fill="both", expand=True)
        trans_scrollbar.pack(side="right", fill="y")
        
        # Load transactions
        self.refresh_transactions_table()
    
    def show_transactions_view(self):
        """Display all transactions history view"""
        self.clear_sales_content()
        self.current_sales_view = "transactions"
        
        # Transactions view container
        trans_container = ctk.CTkFrame(self.sales_content_frame, corner_radius=12,
                                      fg_color=("#fafafa", "gray19"))
        trans_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Header
        header_frame = ctk.CTkFrame(trans_container, height=80, corner_radius=12,
                                   fg_color=("#e1f5fe", "#1a237e"))
        header_frame.pack(fill="x", padx=20, pady=(20, 15))
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=25, pady=20)
        
        ctk.CTkLabel(
            header_content,
            text="📊 Complete Transaction History",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1976d2", "#64b5f6")
        ).pack(side="left")
        
        # Back button
        back_btn = ctk.CTkButton(
            header_content,
            text="↩️ Back to Orders",
            command=self.show_orders_management,
            width=140,
            height=40,
            corner_radius=10,
            fg_color=("white", "gray25"),
            text_color=("#1976d2", "white"),
            hover_color=("#f5f5f5", "gray30")
        )
        back_btn.pack(side="right")
        
        # All transactions table
        self.create_all_transactions_table(trans_container)
    
    def create_all_transactions_table(self, parent):
        """Create comprehensive transactions table"""
        table_container = ctk.CTkFrame(parent, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create treeview
        import tkinter as tk
        from tkinter import ttk
        
        tree_frame = tk.Frame(table_container, bg="#fafafa")
        tree_frame.pack(fill="both", expand=True)
        
        all_trans_columns = ("Transaction ID", "Order ID", "Customer", "Date", "Amount", 
                            "Payment Method", "Order Status", "Notes")
        
        self.all_transactions_tree = ttk.Treeview(tree_frame, columns=all_trans_columns, 
                                                 show="headings", height=15)
        
        # Configure columns with proper widths
        col_widths = {"Transaction ID": 130, "Order ID": 100, "Customer": 150, "Date": 100, 
                     "Amount": 100, "Payment Method": 120, "Order Status": 100, "Notes": 150}
        
        for col in all_trans_columns:
            self.all_transactions_tree.heading(col, text=col)
            self.all_transactions_tree.column(col, width=col_widths.get(col, 100))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.all_transactions_tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.all_transactions_tree.xview)
        self.all_transactions_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.all_transactions_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        
        # Add transaction actions frame
        actions_frame = ctk.CTkFrame(table_container, height=50, corner_radius=8)
        actions_frame.pack(fill="x", pady=(10, 0))
        actions_frame.pack_propagate(False)
        
        # Delete transaction button
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Delete Selected Transaction",
            command=self.delete_selected_transaction,
            width=200,
            height=35,
            corner_radius=8,
            fg_color=("#d32f2f", "#b71c1c"),
            hover_color=("#c62828", "#a71c1c"),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        delete_btn.pack(side="left", padx=20, pady=8)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh",
            command=self.refresh_all_transactions_table,
            width=120,
            height=35,
            corner_radius=8,
            fg_color=("#1976d2", "#0d47a1"),
            hover_color=("#1565c0", "#0d47a1"),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        refresh_btn.pack(side="left", padx=(10, 20), pady=8)
        
        # Load all transactions
        self.refresh_all_transactions_table()
    
    def show_customer_management(self):
        """Display COMPLETE TAKEOVER customer management interface"""
        # COMPLETE TAKEOVER: Hide all existing sales tab content and navigation
        self.clear_sales_content()
        self.current_sales_view = "customers"
        
        # Find the parent container (the entire data management area)
        data_parent = self.sales_content_frame.master
        
        # Hide the existing sales tab structure (buttons + content frame)
        for widget in data_parent.winfo_children():
            widget.pack_forget()
        
        # Create COMPLETE takeover container - takes ENTIRE data management area
        self.complete_takeover_container = ctk.CTkFrame(data_parent, corner_radius=0,
                                                       fg_color=("white", "gray17"))
        self.complete_takeover_container.pack(fill="both", expand=True)
        
        # Header with back button - minimal height
        header_frame = ctk.CTkFrame(self.complete_takeover_container, height=60, corner_radius=0,
                                   fg_color=("#673ab7", "#512da8"))
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Back button and title on same line
        ctk.CTkButton(
            header_content,
            text="← Back to Sales",
            command=self.restore_sales_tab,
            width=140,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("white", "gray25"),
            text_color=("#512da8", "white"),
            hover_color=("#f5f5f5", "gray35")
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_content,
            text="👥 Customer Management",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=(30, 0))
        
        # Maximized content area - full remaining space
        content_container = ctk.CTkFrame(self.complete_takeover_container, corner_radius=0,
                                        fg_color=("white", "gray20"))
        content_container.pack(fill="both", expand=True)
        
        # Create main container with two panels
        main_container = ctk.CTkFrame(content_container, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Left panel - Customer form (40% width)
        form_panel = ctk.CTkFrame(main_container, width=450, corner_radius=12,
                                 fg_color=("#f8f9fa", "gray19"))
        form_panel.pack(side="left", fill="y", padx=(0, 15))
        form_panel.pack_propagate(False)
        
        # Right panel - Customer table (60% width)
        table_panel = ctk.CTkFrame(main_container, corner_radius=12,
                                  fg_color=("#f8f9fa", "gray19"))
        table_panel.pack(side="right", fill="both", expand=True, padx=(15, 0))
        
        # === LEFT PANEL: CUSTOMER FORM ===
        self.create_customer_form(form_panel)
        
        # === RIGHT PANEL: CUSTOMER TABLE ===
        self.create_customer_table(table_panel)
        
        # Load customers data
        self.refresh_customer_table()
    
    def create_customer_form(self, parent):
        """Create customer input form"""
        # Form header
        form_header = ctk.CTkFrame(parent, height=60, corner_radius=10,
                                  fg_color=("#673ab7", "#512da8"))
        form_header.pack(fill="x", padx=15, pady=(15, 10))
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="👥 Customer Form",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Scrollable form area
        form_scroll = ctk.CTkScrollableFrame(parent, corner_radius=0)
        form_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Initialize customer form variables
        self.customer_vars = {}
        self.current_customer_id = None
        
        # Customer Details Section
        self.create_minimal_section(form_scroll, "Customer Information")
        
        # Name field (required)
        self.create_simple_field(form_scroll, "Customer Name", "name", "text", 
                                self.customer_vars, placeholder="Enter customer full name", 
                                required=True, full_width=True)
        
        # Contact number field (required)
        self.create_simple_field(form_scroll, "Contact Number", "contact_number", "text", 
                                self.customer_vars, placeholder="e.g., +91 9876543210", 
                                required=True, full_width=True)
        
        # GST number field (optional)
        self.create_simple_field(form_scroll, "GST Number", "gst_number", "text", 
                                self.customer_vars, placeholder="e.g., 29ABCDE1234F1Z5 (optional)", 
                                required=False, full_width=True)
        
        # Address field (optional)
        address_container = ctk.CTkFrame(form_scroll, fg_color="transparent")
        address_container.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            address_container,
            text="Address",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(anchor="w", pady=(0, 4))
        
        self.customer_vars["address"] = tk.StringVar()
        address_textbox = ctk.CTkTextbox(
            address_container,
            height=80,
            corner_radius=8,
            border_width=1,
            font=ctk.CTkFont(size=12)
        )
        address_textbox.pack(fill="x")
        address_textbox.insert("1.0", "Enter customer address (optional)")
        self.customer_address_textbox = address_textbox
        
        # Due payment field (read-only, auto-calculated)
        due_container = ctk.CTkFrame(form_scroll, fg_color="transparent")
        due_container.pack(fill="x", pady=8)
        
        ctk.CTkLabel(
            due_container,
            text="Due Payment (Auto-calculated)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(anchor="w", pady=(0, 4))
        
        self.customer_vars["due_payment"] = tk.StringVar()
        self.customer_vars["due_payment"].set("₹0.00")
        due_entry = ctk.CTkEntry(
            due_container,
            textvariable=self.customer_vars["due_payment"],
            height=35,
            corner_radius=8,
            border_width=1,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="readonly"
        )
        due_entry.pack(fill="x")
        
        # Action buttons
        self.create_customer_form_buttons(form_scroll)
    
    def create_customer_form_buttons(self, parent):
        """Create customer form action buttons"""
        buttons_container = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_container.pack(fill="x", pady=(20, 10))
        buttons_container.grid_columnconfigure((0, 1), weight=1)
        
        # Save/Update button
        self.customer_save_btn = ctk.CTkButton(
            buttons_container,
            text="💾 Save Customer",
            command=self.save_customer,
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20")
        )
        self.customer_save_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Clear/Cancel button
        self.customer_clear_btn = ctk.CTkButton(
            buttons_container,
            text="🗑️ Clear Form",
            command=self.clear_customer_form,
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#6c757d", "#495057"),
            hover_color=("#5a6268", "#343a40")
        )
        self.customer_clear_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
    
    def create_customer_table(self, parent):
        """Create customer table with edit functionality"""
        # Table header
        table_header = ctk.CTkFrame(parent, height=60, corner_radius=10,
                                   fg_color=("#673ab7", "#512da8"))
        table_header.pack(fill="x", padx=15, pady=(15, 10))
        table_header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(table_header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        ctk.CTkLabel(
            header_content,
            text="📋 Customer Records",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_content,
            text="🔄 Refresh",
            command=self.refresh_customer_table,
            width=100,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("white", "gray25"),
            text_color=("#673ab7", "white"),
            hover_color=("#f5f5f5", "gray35")
        )
        refresh_btn.pack(side="right")
        
        # Table container
        table_container = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create customer table without actions column in Treeview
        columns = ("Name", "Contact", "GST Number", "Address", "Due Payment")
        
        # Define column headings and widths
        column_configs = {
            "Name": 150,
            "Contact": 120,
            "GST Number": 150,
            "Address": 200,
            "Due Payment": 100
        }
        
        # Create main table and actions layout
        table_and_actions_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_and_actions_frame.pack(fill="both", expand=True)
        
        # Left side: Table with scrollbars
        table_main_frame = ctk.CTkFrame(table_and_actions_frame, fg_color="transparent")
        table_main_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Create the treeview
        self.customer_tree = ttk.Treeview(table_main_frame, columns=columns, show="headings", height=15)
        
        for col, width in column_configs.items():
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=width, minwidth=80)
        
        # Pack the tree first
        self.customer_tree.pack(fill="both", expand=True)
        
        # Create and pack scrollbars (simplified approach)
        v_scrollbar = ttk.Scrollbar(table_main_frame, orient="vertical", command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Note: Removing horizontal scrollbar for now to simplify layout
        # v_scrollbar.pack(side="right", fill="y")
        
        # Right side: Action buttons frame
        actions_frame = ctk.CTkFrame(table_and_actions_frame, width=120, corner_radius=10,
                                   fg_color=("#f8f9fa", "gray19"))
        actions_frame.pack(side="right", fill="y")
        actions_frame.pack_propagate(False)
        
        # Actions header
        actions_header = ctk.CTkFrame(actions_frame, height=40, corner_radius=8,
                                     fg_color=("#673ab7", "#512da8"))
        actions_header.pack(fill="x", padx=5, pady=(5, 10))
        actions_header.pack_propagate(False)
        
        ctk.CTkLabel(
            actions_header,
            text="Actions",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        ).pack(pady=10)
        
        # Actions scroll frame for dynamic buttons
        self.actions_scroll = ctk.CTkScrollableFrame(actions_frame, corner_radius=0)
        self.actions_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # Bind selection event to update action buttons
        self.customer_tree.bind("<<TreeviewSelect>>", self.update_customer_actions)
        
        # Remove old event bindings since we'll use the action buttons
        # self.customer_tree.bind("<Double-1>", self.edit_customer_from_table)
        # self.customer_tree.bind("<Button-3>", self.show_customer_context_menu)
    
    def save_customer(self):
        """Save or update customer"""
        try:
            # Validate required fields
            name = self.customer_vars["name"].get().strip()
            contact = self.customer_vars["contact_number"].get().strip()
            
            if not name:
                messagebox.showerror("Validation Error", "Customer name is required!")
                return
            
            if not contact:
                messagebox.showerror("Validation Error", "Contact number is required!")
                return
            
            # Get form data
            customer_data = {
                "name": name,
                "contact_number": contact,
                "gst_number": self.customer_vars["gst_number"].get().strip(),
                "address": self.customer_address_textbox.get("1.0", "end-1c").strip()
            }
            
            # Remove placeholder text if present
            if customer_data["address"] == "Enter customer address (optional)":
                customer_data["address"] = ""
            
            if self.current_customer_id:
                # Update existing customer
                result = self.data_service.update_customer(self.current_customer_id, customer_data)
                if result > 0:
                    messagebox.showinfo("Success", "Customer updated successfully!")
                    self.clear_customer_form()
                    self.refresh_customer_table()
                else:
                    messagebox.showerror("Error", "Failed to update customer!")
            else:
                # Add new customer
                result = self.data_service.add_customer(customer_data)
                if result:
                    messagebox.showinfo("Success", "Customer added successfully!")
                    self.clear_customer_form()
                    self.refresh_customer_table()
                else:
                    messagebox.showerror("Error", "Failed to add customer!")
                    
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save customer: {str(e)}")
    
    def clear_customer_form(self):
        """Clear the customer form"""
        for var in self.customer_vars.values():
            var.set("")
        
        self.customer_address_textbox.delete("1.0", "end")
        self.customer_address_textbox.insert("1.0", "Enter customer address (optional)")
        
        self.current_customer_id = None
        self.customer_save_btn.configure(text="💾 Save Customer")
        self.customer_clear_btn.configure(text="🗑️ Clear Form")
        self.customer_vars["due_payment"].set("₹0.00")
    
    def refresh_customer_table(self):
        """Refresh customer table data"""
        try:
            # Clear existing data
            for item in self.customer_tree.get_children():
                self.customer_tree.delete(item)
            
            # Get updated customer data directly from database (with _id)
            customers_list = self.data_service.db_manager.find_documents("customers", {})
            
            if not customers_list:
                # Clear action buttons when no data
                self.update_customer_actions()
                return
            
            # Insert data into table
            for customer in customers_list:
                # Handle customer ID properly - MongoDB ObjectId needs to be converted to string
                customer_id = str(customer.get('_id', ''))
                
                name = customer.get('name', '')
                contact = customer.get('contact_number', '')
                gst = customer.get('gst_number', '')
                address = customer.get('address', '')[:50] + "..." if len(str(customer.get('address', ''))) > 50 else customer.get('address', '')
                due_payment = f"₹{customer.get('due_payment', 0):.2f}"
                
                # Store customer ID as tag for later retrieval
                item = self.customer_tree.insert("", "end", values=(name, contact, gst, address, due_payment), tags=(customer_id,))
                
            # Update action buttons for current selection
            self.update_customer_actions()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh customer table: {str(e)}")
    
    def update_customer_actions(self, event=None):
        """Update action buttons based on current selection"""
        # Clear existing action buttons
        for widget in self.actions_scroll.winfo_children():
            widget.destroy()
        
        # Get current selection
        selection = self.customer_tree.selection()
        
        if not selection:
            # Show message when no customer selected
            message_label = ctk.CTkLabel(
                self.actions_scroll,
                text="Select a customer\nto see actions",
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray60"),
                justify="center"
            )
            message_label.pack(pady=20)
            return
        
        # Get selected customer data
        item = selection[0]
        customer_data = self.customer_tree.item(item)
        customer_name = customer_data['values'][0]
        customer_id = customer_data['tags'][0] if customer_data['tags'] else None
        
        if not customer_id:
            return
        
        # Customer info display
        info_frame = ctk.CTkFrame(self.actions_scroll, corner_radius=8,
                                 fg_color=("#e8f5e8", "gray30"))
        info_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Selected:",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=("gray40", "gray70")
        ).pack(pady=(5, 0))
        
        ctk.CTkLabel(
            info_frame,
            text=customer_name[:15] + "..." if len(customer_name) > 15 else customer_name,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("#2e7d32", "#66bb6a")
        ).pack(pady=(0, 5))
        
        # Edit button
        edit_btn = ctk.CTkButton(
            self.actions_scroll,
            text="✏️ Edit",
            command=lambda: self.edit_customer_by_id(customer_id),
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#2196f3", "#1565c0"),
            hover_color=("#1976d2", "#0d47a1")
        )
        edit_btn.pack(pady=(0, 5), padx=5)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            self.actions_scroll,
            text="🗑️ Delete",
            command=lambda: self.delete_customer_by_id(customer_id, customer_name),
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#f44336", "#c62828"),
            hover_color=("#d32f2f", "#b71c1c")
        )
        delete_btn.pack(pady=(0, 5), padx=5)
        
        # View Orders button
        orders_btn = ctk.CTkButton(
            self.actions_scroll,
            text="📋 View Orders",
            command=lambda: self.view_customer_orders(customer_name),
            width=100,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#9c27b0", "#6a1b9a"),
            hover_color=("#8e24aa", "#4a148c")
        )
        orders_btn.pack(pady=(0, 5), padx=5)
    
    def edit_customer_by_id(self, customer_id):
        """Edit customer by ID"""
        try:
            # Get customer data from database
            customers = self.data_service.db_manager.find_documents("customers", {"_id": self.data_service.db_manager.string_to_objectid(customer_id)})
            
            if not customers:
                messagebox.showerror("Error", "Customer not found!")
                return
            
            customer = customers[0]
            
            # Populate form with customer data
            self.customer_vars["name"].set(customer.get('name', ''))
            self.customer_vars["contact_number"].set(customer.get('contact_number', ''))
            self.customer_vars["gst_number"].set(customer.get('gst_number', ''))
            self.customer_vars["due_payment"].set(f"₹{customer.get('due_payment', 0):.2f}")
            
            # Set address
            self.customer_address_textbox.delete("1.0", "end")
            self.customer_address_textbox.insert("1.0", customer.get('address', ''))
            
            # Set edit mode
            self.current_customer_id = customer_id
            self.customer_save_btn.configure(text="💾 Update Customer")
            self.customer_clear_btn.configure(text="❌ Cancel Edit")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer data: {str(e)}")
    
    def delete_customer_by_id(self, customer_id, customer_name):
        """Delete customer by ID"""
        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete customer '{customer_name}'?\n\nThis action cannot be undone."
        )
        
        if response:
            try:
                result = self.data_service.delete_customer(customer_id)
                
                if result > 0:
                    messagebox.showinfo("Success", "Customer deleted successfully!")
                    self.refresh_customer_table()
                    # Clear form if this customer was being edited
                    if self.current_customer_id == customer_id:
                        self.clear_customer_form()
                else:
                    messagebox.showerror("Error", "Failed to delete customer!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")
    
    def view_customer_orders(self, customer_name):
        """View all orders for a specific customer"""
        try:
            # Get orders for this customer
            orders = self.data_service.db_manager.find_documents("orders", {"customer_name": customer_name})
            
            if not orders:
                messagebox.showinfo("No Orders", f"No orders found for customer '{customer_name}'")
                return
            
            # Create a popup window to show orders
            popup = tk.Toplevel()
            popup.title(f"Orders for {customer_name}")
            popup.geometry("800x400")
            popup.resizable(True, True)
            popup.grab_set()  # Make window modal
            
            # Center the popup
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
            y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            
            # Create frame for content
            main_frame = ctk.CTkFrame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Header
            header_label = ctk.CTkLabel(
                main_frame,
                text=f"📋 Orders for {customer_name}",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            header_label.pack(pady=(10, 20))
            
            # Orders table
            orders_frame = ctk.CTkFrame(main_frame)
            orders_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            columns = ("Order ID", "Item", "Quantity", "Total", "Due Amount", "Status", "Date")
            orders_tree = ttk.Treeview(orders_frame, columns=columns, show="headings", height=15)
            
            # Configure columns
            order_column_configs = {
                "Order ID": 100,
                "Item": 150,
                "Quantity": 80,
                "Total": 100,
                "Due Amount": 100,
                "Status": 100,
                "Date": 100
            }
            
            for col, width in order_column_configs.items():
                orders_tree.heading(col, text=col)
                orders_tree.column(col, width=width, minwidth=60)
            
            # Add scrollbars
            v_scroll = ttk.Scrollbar(orders_frame, orient="vertical", command=orders_tree.yview)
            h_scroll = ttk.Scrollbar(orders_frame, orient="horizontal", command=orders_tree.xview)
            orders_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
            
            # Pack elements
            orders_tree.pack(side="left", fill="both", expand=True)
            v_scroll.pack(side="right", fill="y")
            h_scroll.pack(side="bottom", fill="x")
            
            # Populate orders
            total_due = 0
            for order in orders:
                order_id = order.get('order_id', 'N/A')
                item = order.get('item_name', 'N/A')
                quantity = order.get('quantity', 0)
                total_amount = order.get('total_amount', 0)
                due_amount = order.get('due_amount', 0)
                status = order.get('order_status', 'N/A')
                order_date = order.get('order_date', 'N/A')
                
                total_due += due_amount
                
                orders_tree.insert("", "end", values=(
                    order_id, item, quantity, f"₹{total_amount:.2f}", 
                    f"₹{due_amount:.2f}", status, order_date
                ))
            
            # Summary frame
            summary_frame = ctk.CTkFrame(main_frame, height=50)
            summary_frame.pack(fill="x", padx=10, pady=(0, 10))
            summary_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                summary_frame,
                text=f"Total Orders: {len(orders)} | Total Due: ₹{total_due:.2f}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#d32f2f", "#ef5350")
            ).pack(pady=15)
            
            # Close button
            close_btn = ctk.CTkButton(
                main_frame,
                text="Close",
                command=popup.destroy,
                width=100,
                height=35
            )
            close_btn.pack(pady=(0, 10))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer orders: {str(e)}")

    def show_payment_collection(self):
        """Display COMPLETE TAKEOVER payment collection interface"""
        # COMPLETE TAKEOVER: Hide all existing sales tab content and navigation
        self.clear_sales_content()
        self.current_sales_view = "payment_collection"
        
        # Find the parent container (the entire data management area)
        data_parent = self.sales_content_frame.master
        
        # Hide the existing sales tab structure (buttons + content frame)
        for widget in data_parent.winfo_children():
            widget.pack_forget()
        
        # Create COMPLETE takeover container - takes ENTIRE data management area
        self.complete_takeover_container = ctk.CTkFrame(data_parent, corner_radius=0,
                                                       fg_color=("white", "gray17"))
        self.complete_takeover_container.pack(fill="both", expand=True)
        
        # Header with back button - minimal height
        header_frame = ctk.CTkFrame(self.complete_takeover_container, height=60, corner_radius=0,
                                   fg_color=("#9c27b0", "#6a1b9a"))
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Back button and title on same line
        ctk.CTkButton(
            header_content,
            text="← Back to Sales",
            command=self.restore_sales_tab,
            width=140,
            height=30,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("white", "gray25"),
            text_color=("#9c27b0", "white"),
            hover_color=("#f5f5f5", "gray35")
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_content,
            text="💰 Collect Payments",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=(30, 0))
        
        # Main content area - full remaining space
        main_container = ctk.CTkFrame(self.complete_takeover_container, corner_radius=0,
                                     fg_color=("white", "gray20"))
        main_container.pack(fill="both", expand=True)
        
        # Content layout: Left form (65%), Right order details (35%)
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Left panel - Payment form - larger
        left_panel = ctk.CTkFrame(content_frame, corner_radius=10, fg_color=("white", "gray25"))
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Right panel - Order details - smaller but still functional
        right_panel = ctk.CTkFrame(content_frame, width=400, corner_radius=10, fg_color=("white", "gray25"))
        right_panel.pack(side="right", fill="y", padx=(15, 0))
        right_panel.pack_propagate(False)
        
        # Create large payment form and order details
        self.create_large_payment_form(left_panel)
        self.create_large_order_details(right_panel)
    
    def restore_sales_tab(self):
        """Restore the original sales tab structure"""
        # Find the parent container
        data_parent = self.sales_content_frame.master
        
        # Remove the complete takeover container
        if hasattr(self, 'complete_takeover_container'):
            self.complete_takeover_container.destroy()
            delattr(self, 'complete_takeover_container')
        
        # Restore the original sales tab structure
        self.create_sales_management_content(data_parent)
    
    def create_large_payment_form(self, parent):
        """Create large payment form with simple dropdown creation"""
        # Title
        ctk.CTkLabel(
            parent,
            text="💳 Payment Collection",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#9c27b0", "#e1bee7")
        ).pack(pady=(20, 15))
        
        # Form container
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Customer selection - simple direct creation
        ctk.CTkLabel(
            form_frame,
            text="Customer with Due Payments:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#333333", "#cccccc")
        ).pack(anchor="w", pady=(0, 5))
        
        self.customer_dropdown = ctk.CTkComboBox(
            form_frame,
            values=["Loading customers..."],
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=13),
            command=self.on_customer_selection
        )
        self.customer_dropdown.pack(fill="x", pady=(0, 15))
        
        # Order selection - simple direct creation
        ctk.CTkLabel(
            form_frame,
            text="Order with Due Payment:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#333333", "#cccccc")
        ).pack(anchor="w", pady=(0, 5))
        
        self.order_dropdown = ctk.CTkComboBox(
            form_frame,
            values=["Select customer first..."],
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            dropdown_font=ctk.CTkFont(size=13),
            command=self.on_order_selection_for_payment
        )
        self.order_dropdown.pack(fill="x", pady=(0, 15))
        
        # Payment details section
        payment_section = ctk.CTkFrame(form_frame, fg_color=("gray95", "gray30"), corner_radius=8)
        payment_section.pack(fill="x", pady=(10, 15))
        
        ctk.CTkLabel(
            payment_section,
            text="💰 Payment Details",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#9c27b0", "#e1bee7")
        ).pack(pady=(15, 10))
        
        # Amount and method in same row
        amount_row = ctk.CTkFrame(payment_section, fg_color="transparent")
        amount_row.pack(fill="x", padx=15, pady=(0, 15))
        
        # Left: Amount
        amount_left = ctk.CTkFrame(amount_row, fg_color="transparent")
        amount_left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            amount_left,
            text="Payment Amount (₹):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#333333", "#cccccc")
        ).pack(anchor="w", pady=(0, 5))
        
        self.payment_amount_entry = ctk.CTkEntry(
            amount_left,
            placeholder_text="Enter payment amount",
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.payment_amount_entry.pack(fill="x")
        
        # Right: Method
        method_right = ctk.CTkFrame(amount_row, fg_color="transparent")
        method_right.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(
            method_right,
            text="Payment Method:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#333333", "#cccccc")
        ).pack(anchor="w", pady=(0, 5))
        
        self.payment_method_combo = ctk.CTkComboBox(
            method_right,
            values=["Cash", "Card", "UPI", "Bank Transfer", "Cheque"],
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.payment_method_combo.pack(fill="x")
        self.payment_method_combo.set("Cash")
        
        # Notes field (full width)
        ctk.CTkLabel(
            payment_section,
            text="Notes (Optional):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#333333", "#cccccc")
        ).pack(anchor="w", padx=15, pady=(0, 5))
        
        self.payment_notes_entry = ctk.CTkEntry(
            payment_section,
            placeholder_text="Additional notes about this payment...",
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=14)
        )
        self.payment_notes_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Action buttons
        self.create_large_payment_buttons(form_frame)
        
        # Load initial data
        self.load_due_orders_data()
    
    def create_large_payment_buttons(self, parent):
        """Create large payment action buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Button row
        button_row = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_row.pack(fill="x")
        
        # Collect Payment button (primary action)
        ctk.CTkButton(
            button_row,
            text="💰 Collect Payment",
            command=self.collect_payment_for_order,
            height=55,
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20"),
            text_color="white"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Clear Form button (secondary action) 
        ctk.CTkButton(
            button_row,
            text="🗑️ Clear Form",
            command=self.clear_payment_form,
            height=55,
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#ff9800", "#e65100"),
            hover_color=("#f57c00", "#bf360c"),
            text_color="white"
        ).pack(side="right", fill="x", expand=True, padx=(10, 0))
    
    def create_large_order_details(self, parent):
        """Create large order details panel"""
        # Title
        ctk.CTkLabel(
            parent,
            text="📋 Order Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#9c27b0", "#e1bee7")
        ).pack(pady=(20, 15))
        
        # Details content - scrollable for long orders
        self.payment_details_content = ctk.CTkScrollableFrame(
            parent, 
            corner_radius=8,
            fg_color=("white", "gray25")
        )
        self.payment_details_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Initialize with empty state
        self.update_large_order_details(None)
    
    def update_large_order_details(self, order_data):
        """Update order details panel with large formatting"""
        # Clear existing content
        for widget in self.payment_details_content.winfo_children():
            widget.destroy()
        
        if not order_data:
            # Empty state
            ctk.CTkLabel(
                self.payment_details_content,
                text="📋\n\nSelect an order to view\ndetailed information",
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray40"),
                justify="center"
            ).pack(expand=True, pady=50)
            return
        
        # Order header
        header_frame = ctk.CTkFrame(self.payment_details_content, fg_color=("gray95", "gray30"), corner_radius=8)
        header_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header_frame,
            text=f"Order #{order_data.get('order_id', 'N/A')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#9c27b0", "#e1bee7")
        ).pack(pady=10)
        
        # Customer info
        info_frame = ctk.CTkFrame(self.payment_details_content, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Customer
        ctk.CTkLabel(
            info_frame,
            text="Customer:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            info_frame,
            text=order_data.get('customer_name', 'N/A'),
            font=ctk.CTkFont(size=14),
            text_color=("#2196f3", "#90caf9")
        ).pack(anchor="w", pady=(0, 8))
        
        # Order date
        ctk.CTkLabel(
            info_frame,
            text="Date:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            info_frame,
            text=order_data.get('order_date', 'N/A'),
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 8))
        
        # Financial summary
        financial_frame = ctk.CTkFrame(self.payment_details_content, fg_color=("gray95", "gray30"), corner_radius=8)
        financial_frame.pack(fill="x", pady=(10, 15))
        
        ctk.CTkLabel(
            financial_frame,
            text="💰 Financial Summary",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#4caf50", "#81c784")
        ).pack(pady=(10, 5))
        
        # Financial details
        total_amount = order_data.get('total_amount', 0)
        paid_amount = order_data.get('paid_amount', 0)
        due_amount = order_data.get('due_amount', 0)
        
        financial_details = ctk.CTkFrame(financial_frame, fg_color="transparent")
        financial_details.pack(fill="x", padx=15, pady=(0, 10))
        
        for label, value, color in [
            ("Total Amount:", f"₹{total_amount:.2f}", "#2196f3"),
            ("Advance Paid:", f"₹{paid_amount:.2f}", "#4caf50"),
            ("Due Amount:", f"₹{due_amount:.2f}", "#f44336" if due_amount > 0 else "#4caf50")
        ]:
            row = ctk.CTkFrame(financial_details, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=(color, color)
            ).pack(side="right")
        
        # Items if available
        items = order_data.get('items', [])
        if items:
            items_frame = ctk.CTkFrame(self.payment_details_content, fg_color="transparent")
            items_frame.pack(fill="x", pady=(0, 10))
            
            ctk.CTkLabel(
                items_frame,
                text="📦 Order Items",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#ff9800", "#ffb74d")
            ).pack(anchor="w", pady=(0, 5))
            
            for item in items[:3]:  # Show first 3 items
                item_text = f"• {item.get('name', 'Unknown')} x{item.get('quantity', 1)}"
                ctk.CTkLabel(
                    items_frame,
                    text=item_text,
                    font=ctk.CTkFont(size=12)
                ).pack(anchor="w", padx=10)
            
            if len(items) > 3:
                ctk.CTkLabel(
                    items_frame,
                    text=f"... and {len(items) - 3} more items",
                    font=ctk.CTkFont(size=12),
                    text_color=("gray50", "gray40")
                ).pack(anchor="w", padx=10, pady=(2, 0))
    
    def load_due_orders_data(self):
        """Load only customers and orders with due payments > 0"""
        try:
            from data_service import DataService
            data_service = DataService()
            
            # Get all orders with due amounts > 0
            service = self.order_service if self.order_service else data_service
            all_orders = service.get_all_orders()
            due_orders = [order for order in all_orders if order.get('due_amount', 0) > 0]
            
            if not due_orders:
                # No due orders found
                self.customer_dropdown.configure(values=["No customers with due payments"])
                self.customer_dropdown.set("No customers with due payments")
                self.order_dropdown.configure(values=["No orders available"])
                self.order_dropdown.set("No orders available")
                self.due_orders = []
                return
            
            # Extract unique customers with due payments
            customers = list(set([order.get('customer_name', '') for order in due_orders if order.get('customer_name')]))
            customers.sort()
            
            # Update customer dropdown
            customer_options = ["Select customer..."] + customers
            self.customer_dropdown.configure(values=customer_options)
            self.customer_dropdown.set("Select customer...")
            
            # Store due orders for quick access
            self.due_orders = due_orders
            
        except Exception as e:
            print(f"Error loading due orders data: {e}")
            self.due_orders = []
            self.customer_dropdown.configure(values=["Error loading customers"])
            self.customer_dropdown.set("Error loading customers")
    
    def on_customer_selection(self, customer_name):
        """Handle customer selection - show only orders with due payments"""
        if customer_name in ["Select customer...", "No customers with due payments", "Error loading customers"]:
            self.order_dropdown.configure(values=["Select customer first..."])
            self.order_dropdown.set("Select customer first...")
            self.update_simplified_order_details(None)
            return
        
        # Filter orders for selected customer with due amounts > 0
        customer_orders = [order for order in self.due_orders 
                          if order.get('customer_name') == customer_name and order.get('due_amount', 0) > 0]
        
        if not customer_orders:
            self.order_dropdown.configure(values=["No due orders for this customer"])
            self.order_dropdown.set("No due orders for this customer")
            self.update_simplified_order_details(None)
            return
        
        # Create order options with order ID, item name, and due amount
        order_options = ["Select order..."]
        for order in customer_orders:
            order_id = order.get('order_id', 'N/A')
            item_name = order.get('item_name', 'N/A')
            due_amount = order.get('due_amount', 0)
            option = f"{order_id} - {item_name} (Due: ₹{due_amount:.2f})"
            order_options.append(option)
        
        # Update order dropdown
        self.order_dropdown.configure(values=order_options)
        self.order_dropdown.set("Select order...")
        self.update_simplified_order_details(None)
    
    def on_order_selection_for_payment(self, order_option):
        """Handle order selection and update details panel"""
        if order_option in ["Select order...", "Select customer first...", "No due orders for this customer", "No orders available"]:
            self.update_large_order_details(None)
            return
        
        # Extract order ID from option
        order_id = order_option.split(" - ")[0]
        
        # Find the selected order
        selected_order = None
        for order in self.due_orders:
            if order.get('order_id') == order_id:
                selected_order = order
                break
        
        # Update details panel
        self.update_large_order_details(selected_order)
        
        # Store selected order for payment processing
        self.selected_payment_order = selected_order
        
        # Auto-populate max payment amount (due amount)
        if selected_order:
            due_amount = selected_order.get('due_amount', 0)
            self.payment_amount_entry.delete(0, 'end')
            self.payment_amount_entry.insert(0, str(due_amount))
    
    def update_maximized_order_details(self, order_data):
        """Update the maximized order details panel"""
        # Clear existing content
        for widget in self.payment_details_content.winfo_children():
            widget.destroy()
        
        if not order_data:
            # Show empty state
            empty_frame = ctk.CTkFrame(self.payment_details_content, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both")
            
            ctk.CTkLabel(
                empty_frame,
                text="📋\n\nSelect an order to view\npayment details",
                font=ctk.CTkFont(size=16),
                text_color=("gray50", "gray60"),
                justify="center"
            ).pack(expand=True)
            return
        
        # Order summary - prominent
        summary_frame = ctk.CTkFrame(self.payment_details_content, corner_radius=8,
                                   fg_color=("#e3f2fd", "gray25"))
        summary_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(summary_frame, text=f"Order: {order_data.get('order_id', 'N/A')}", 
                    font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(12, 3))
        ctk.CTkLabel(summary_frame, text=f"Item: {order_data.get('item_name', 'N/A')}", 
                    font=ctk.CTkFont(size=13)).pack(pady=2)
        ctk.CTkLabel(summary_frame, text=f"Customer: {order_data.get('customer_name', 'N/A')}", 
                    font=ctk.CTkFont(size=13)).pack(pady=(2, 12))
        
        # Payment status - larger display
        total_amount = order_data.get('total_amount', 0)
        advance_payment = order_data.get('advance_payment', 0)
        due_amount = order_data.get('due_amount', 0)
        due_date = order_data.get('due_date', '')
        
        # Payment amounts - bigger cards
        payment_frame = ctk.CTkFrame(self.payment_details_content, corner_radius=8,
                                   fg_color=("#fff8e1", "gray25"))
        payment_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(payment_frame, text="💰 Payment Status", 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#f57c00", "#ffb74d")).pack(pady=(12, 8))
        
        # Payment amounts in grid - larger
        amounts_grid = ctk.CTkFrame(payment_frame, fg_color="transparent")
        amounts_grid.pack(padx=12, pady=(0, 12))
        amounts_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total
        total_frame = ctk.CTkFrame(amounts_grid, corner_radius=8, fg_color=("white", "gray30"))
        total_frame.grid(row=0, column=0, padx=3, sticky="ew")
        ctk.CTkLabel(total_frame, text="Total", font=ctk.CTkFont(size=11)).pack(pady=(8, 2))
        ctk.CTkLabel(total_frame, text=f"₹{total_amount:.2f}", font=ctk.CTkFont(size=15, weight="bold"),
                    text_color=("#1976d2", "#64b5f6")).pack(pady=(0, 8))
        
        # Paid
        paid_frame = ctk.CTkFrame(amounts_grid, corner_radius=8, fg_color=("white", "gray30"))
        paid_frame.grid(row=0, column=1, padx=3, sticky="ew")
        ctk.CTkLabel(paid_frame, text="Advance Paid", font=ctk.CTkFont(size=11)).pack(pady=(8, 2))
        ctk.CTkLabel(paid_frame, text=f"₹{advance_payment:.2f}", font=ctk.CTkFont(size=15, weight="bold"),
                    text_color=("#4caf50", "#81c784")).pack(pady=(0, 8))
        
        # Due
        due_frame = ctk.CTkFrame(amounts_grid, corner_radius=8, fg_color=("white", "gray30"))
        due_frame.grid(row=0, column=2, padx=3, sticky="ew")
        ctk.CTkLabel(due_frame, text="Due", font=ctk.CTkFont(size=11)).pack(pady=(8, 2))
        ctk.CTkLabel(due_frame, text=f"₹{due_amount:.2f}", font=ctk.CTkFont(size=15, weight="bold"),
                    text_color=("#f44336", "#ef5350")).pack(pady=(0, 8))
        
        # Due date status with color coding
        days_left = self.calculate_days_until_due(due_date)
        due_status, due_color = self.get_due_status_color(days_left)
        
        due_date_frame = ctk.CTkFrame(self.payment_details_content, corner_radius=8,
                                     fg_color=due_color[1])
        due_date_frame.pack(fill="x")
        
        ctk.CTkLabel(
            due_date_frame,
            text=f"📅 Due: {due_date}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=due_color[0]
        ).pack(pady=(12, 3))
        
        ctk.CTkLabel(
            due_date_frame,
            text=due_status,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=due_color[0]
        ).pack(pady=(0, 12))
    
    def create_payment_collection_form(self, parent):
        """Create the payment collection form with dropdowns"""
        # Form header
        form_header = ctk.CTkFrame(parent, height=45, corner_radius=8,
                                  fg_color=("#e8f5e8", "#1a4d1a"))
        form_header.pack(fill="x", padx=15, pady=(15, 10))
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="💳 Collect Payment for Existing Order",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#2e7d32", "#66bb6a")
        ).pack(pady=12)
        
        # Form content
        form_content = ctk.CTkFrame(parent, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Customer selection section
        customer_section = ctk.CTkFrame(form_content, corner_radius=8, fg_color=("#fff3e0", "gray30"))
        customer_section.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            customer_section,
            text="👤 Select Customer",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#e65100", "#ffb74d")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Customer dropdown
        self.payment_customer_var = tk.StringVar()
        self.customer_dropdown = ctk.CTkComboBox(
            customer_section,
            variable=self.payment_customer_var,
            values=["Select Customer..."],
            command=self.on_customer_selection,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=11)
        )
        self.customer_dropdown.pack(fill="x", padx=15, pady=(0, 10))
        
        # Order selection section
        order_section = ctk.CTkFrame(form_content, corner_radius=8, fg_color=("#e3f2fd", "gray30"))
        order_section.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            order_section,
            text="📋 Select Order",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1565c0", "#64b5f6")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Order dropdown
        self.payment_order_var = tk.StringVar()
        self.order_dropdown = ctk.CTkComboBox(
            order_section,
            variable=self.payment_order_var,
            values=["Select Order..."],
            command=self.on_order_selection_for_payment,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=11)
        )
        self.order_dropdown.pack(fill="x", padx=15, pady=(0, 10))
        
        # Payment details section
        payment_section = ctk.CTkFrame(form_content, corner_radius=8, fg_color=("#f1f8e9", "gray30"))
        payment_section.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            payment_section,
            text="💰 Payment Details",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#2e7d32", "#81c784")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Payment amount and method in grid
        payment_grid = ctk.CTkFrame(payment_section, fg_color="transparent")
        payment_grid.pack(fill="x", padx=15, pady=(0, 10))
        payment_grid.grid_columnconfigure((0, 1), weight=1)
        
        # Payment amount
        amount_frame = ctk.CTkFrame(payment_grid, fg_color="transparent")
        amount_frame.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        
        ctk.CTkLabel(amount_frame, text="Amount (₹)*", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.payment_collection_amount_var = tk.StringVar()
        self.payment_amount_entry = ctk.CTkEntry(
            amount_frame,
            textvariable=self.payment_collection_amount_var,
            placeholder_text="Enter amount",
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.payment_amount_entry.pack(fill="x")
        
        # Payment method
        method_frame = ctk.CTkFrame(payment_grid, fg_color="transparent")
        method_frame.grid(row=0, column=1, padx=(8, 0), sticky="ew")
        
        ctk.CTkLabel(method_frame, text="Payment Method*", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.payment_collection_method_var = tk.StringVar(value="Cash")
        method_combo = ctk.CTkComboBox(
            method_frame,
            values=["Cash", "Card", "UPI", "Bank Transfer", "Cheque"],
            variable=self.payment_collection_method_var,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        method_combo.pack(fill="x")
        
        # Notes
        notes_frame = ctk.CTkFrame(payment_section, fg_color="transparent")
        notes_frame.pack(fill="x", padx=15, pady=(5, 0))
        
        ctk.CTkLabel(notes_frame, text="Notes (Optional)", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.payment_notes_var = tk.StringVar()
        notes_entry = ctk.CTkEntry(
            notes_frame,
            textvariable=self.payment_notes_var,
            placeholder_text="Additional notes...",
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        notes_entry.pack(fill="x")
        
        # Action buttons
        button_frame = ctk.CTkFrame(form_content, fg_color="transparent", height=50)
        button_frame.pack(fill="x", pady=(20, 0))
        button_frame.pack_propagate(False)
        
        buttons_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        buttons_container.pack(expand=True)
        
        # Collect Payment button
        collect_btn = ctk.CTkButton(
            buttons_container,
            text="💰 Collect Payment",
            command=self.collect_payment_for_order,
            width=150,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#4caf50", "#2e7d32"),
            hover_color=("#45a049", "#1b5e20")
        )
        collect_btn.pack(side="left", padx=(0, 10))
        
        # Clear Form button
        clear_btn = ctk.CTkButton(
            buttons_container,
            text="🗑️ Clear",
            command=self.clear_payment_form,
            width=100,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#ff9800", "#e65100"),
            hover_color=("#f57c00", "#bf360c")
        )
        clear_btn.pack(side="left")
        
        # Load initial data
        self.load_due_orders_data()
    
    def create_payment_order_details(self, parent):
        """Create order details panel for payment collection"""
        # Header
        details_header = ctk.CTkFrame(parent, height=45, corner_radius=8,
                                     fg_color=("#e1f5fe", "#0d47a1"))
        details_header.pack(fill="x", padx=15, pady=(15, 10))
        details_header.pack_propagate(False)
        
        ctk.CTkLabel(
            details_header,
            text="📊 Order Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1976d2", "#90caf9")
        ).pack(pady=12)
        
        # Details content
        self.payment_details_content = ctk.CTkScrollableFrame(parent, corner_radius=8)
        self.payment_details_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Initialize with empty state
        self.update_payment_order_details(None)
    
    def load_due_orders_data(self):
        """Load customers and orders with due payments"""
        try:
            # Use existing order_service or create new DataService
            service = self.order_service
            if not service:
                from data_service import DataService
                service = DataService()
            
            # Get all orders with due amounts > 0
            all_orders = service.get_all_orders()
            due_orders = [order for order in all_orders if order.get('due_amount', 0) > 0]
            
            # Extract unique customers
            customers = list(set([order.get('customer_name', '') for order in due_orders if order.get('customer_name')]))
            customers.sort()
            
            # Update customer dropdown
            customer_options = ["Select Customer..."] + customers
            self.customer_dropdown.configure(values=customer_options)
            self.customer_dropdown.set("Select Customer...")
            
            # Store due orders for quick access
            self.due_orders = due_orders
            
        except Exception as e:
            print(f"Error loading due orders data: {e}")
            self.due_orders = []
    
    def on_customer_selection(self, customer_name):
        """Handle customer selection and update order dropdown"""
        if customer_name == "Select Customer...":
            self.order_dropdown.configure(values=["Select Order..."])
            self.order_dropdown.set("Select Order...")
            self.update_payment_order_details(None)
            return
        
        # Filter orders for selected customer
        customer_orders = [order for order in self.due_orders if order.get('customer_name') == customer_name]
        
        # Create order options with order ID and item name
        order_options = ["Select Order..."]
        for order in customer_orders:
            order_id = order.get('order_id', 'N/A')
            item_name = order.get('item_name', 'N/A')
            due_amount = order.get('due_amount', 0)
            option = f"{order_id} - {item_name} (Due: ₹{due_amount:.2f})"
            order_options.append(option)
        
        # Update order dropdown
        self.order_dropdown.configure(values=order_options)
        self.order_dropdown.set("Select Order...")
        self.update_payment_order_details(None)
    
    def on_order_selection_for_payment(self, order_option):
        """Handle order selection and update details panel"""
        if order_option == "Select Order...":
            self.update_payment_order_details(None)
            return
        
        # Extract order ID from option
        order_id = order_option.split(" - ")[0]
        
        # Find the selected order
        selected_order = None
        for order in self.due_orders:
            if order.get('order_id') == order_id:
                selected_order = order
                break
        
        # Update details panel
        self.update_payment_order_details(selected_order)
        
        # Store selected order for payment processing
        self.selected_payment_order = selected_order
    
    def update_payment_order_details(self, order_data):
        """Update the order details panel"""
        # Clear existing content
        for widget in self.payment_details_content.winfo_children():
            widget.destroy()
        
        if not order_data:
            # Show empty state
            empty_frame = ctk.CTkFrame(self.payment_details_content, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both")
            
            ctk.CTkLabel(
                empty_frame,
                text="📋 Select an order to view details",
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray60")
            ).pack(expand=True)
            return
        
        # Order information
        self.create_payment_info_section(self.payment_details_content, "📋 Order Information", [
            ("Order ID", order_data.get('order_id', 'N/A')),
            ("Order Date", order_data.get('order_date', 'N/A')),
            ("Order Status", order_data.get('order_status', 'N/A'))
        ])
        
        # Customer information
        self.create_payment_info_section(self.payment_details_content, "👤 Customer Information", [
            ("Customer Name", order_data.get('customer_name', 'N/A')),
            ("Phone Number", order_data.get('customer_phone', 'N/A'))
        ])
        
        # Product information
        self.create_payment_info_section(self.payment_details_content, "🛍️ Product Information", [
            ("Item Name", order_data.get('item_name', 'N/A')),
            ("Quantity", str(order_data.get('quantity', 0))),
            ("Unit Price", f"₹{order_data.get('unit_price', 0):.2f}")
        ])
        
        # Payment status with color coding
        total_amount = order_data.get('total_amount', 0)
        advance_payment = order_data.get('advance_payment', 0)
        due_amount = order_data.get('due_amount', 0)
        due_date = order_data.get('due_date', '')
        
        # Calculate days until due date
        days_left = self.calculate_days_until_due(due_date)
        due_status, due_color = self.get_due_status_color(days_left)
        
        # Payment status section
        payment_frame = ctk.CTkFrame(self.payment_details_content, corner_radius=8,
                                   fg_color=("#fff8e1", "gray25"))
        payment_frame.pack(fill="x", pady=(0, 10))
        
        # Section title
        ctk.CTkLabel(
            payment_frame,
            text="💰 Payment Status",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#f57c00", "#ffb74d")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Payment grid
        payment_grid = ctk.CTkFrame(payment_frame, fg_color="transparent")
        payment_grid.pack(fill="x", padx=15, pady=(0, 10))
        payment_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total amount
        total_frame = ctk.CTkFrame(payment_grid, corner_radius=6, fg_color=("white", "gray30"))
        total_frame.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkLabel(total_frame, text="Total", font=ctk.CTkFont(size=10)).pack(pady=(5, 0))
        ctk.CTkLabel(total_frame, text=f"₹{total_amount:.2f}", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("#1976d2", "#64b5f6")).pack(pady=(0, 5))
        
        # Paid amount
        paid_frame = ctk.CTkFrame(payment_grid, corner_radius=6, fg_color=("white", "gray30"))
        paid_frame.grid(row=0, column=1, padx=(2.5, 2.5), sticky="ew")
        ctk.CTkLabel(paid_frame, text="Advance Paid", font=ctk.CTkFont(size=10)).pack(pady=(5, 0))
        ctk.CTkLabel(paid_frame, text=f"₹{advance_payment:.2f}", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("#4caf50", "#81c784")).pack(pady=(0, 5))
        
        # Due amount
        due_frame = ctk.CTkFrame(payment_grid, corner_radius=6, fg_color=("white", "gray30"))
        due_frame.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        ctk.CTkLabel(due_frame, text="Due", font=ctk.CTkFont(size=10)).pack(pady=(5, 0))
        ctk.CTkLabel(due_frame, text=f"₹{due_amount:.2f}", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("#f44336", "#ef5350")).pack(pady=(0, 5))
        
        # Due date status with change button
        due_date_frame = ctk.CTkFrame(self.payment_details_content, corner_radius=8,
                                     fg_color=due_color[1])
        due_date_frame.pack(fill="x", pady=(0, 10))
        
        # Due date info and button container
        due_date_container = ctk.CTkFrame(due_date_frame, fg_color="transparent")
        due_date_container.pack(fill="x", padx=15, pady=10)
        
        # Due date info (left side)
        due_info_frame = ctk.CTkFrame(due_date_container, fg_color="transparent")
        due_info_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            due_info_frame,
            text=f"📅 Due Date: {due_date}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=due_color[0]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            due_info_frame,
            text=due_status,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=due_color[0]
        ).pack(anchor="w")
        
        # Change due date button (right side)
        change_date_btn = ctk.CTkButton(
            due_date_container,
            text="📅 Change Due Date",
            command=lambda: self.change_order_due_date(order_data),
            width=140,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#ff9800", "#f57c00"),
            hover_color=("#f57c00", "#ef6c00"),
            text_color="white"
        )
        change_date_btn.pack(side="right", padx=(10, 0))
    
    def create_payment_info_section(self, parent, title, data_pairs):
        """Create an information section for payment details"""
        section_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=("#f5f5f5", "gray25"))
        section_frame.pack(fill="x", pady=(0, 10))
        
        # Title
        ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#424242", "#e0e0e0")
        ).pack(anchor="w", padx=15, pady=(8, 5))
        
        # Data pairs
        for label, value in data_pairs:
            row_frame = ctk.CTkFrame(section_frame, height=25, corner_radius=4,
                                   fg_color=("white", "gray30"))
            row_frame.pack(fill="x", padx=15, pady=1)
            row_frame.pack_propagate(False)
            
            row_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(
                row_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=10, weight="bold"),
                width=100
            ).grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
            
            ctk.CTkLabel(
                row_frame,
                text=str(value),
                font=ctk.CTkFont(size=10),
                anchor="w"
            ).grid(row=0, column=1, padx=(0, 10), pady=5, sticky="w")
    
    def calculate_days_until_due(self, due_date_str):
        """Calculate days until due date"""
        try:
            # Debug: Print the due_date_str to understand what we're getting
            print(f"DEBUG: Calculating due date for: '{due_date_str}'")
            
            if not due_date_str or due_date_str.strip() == '':
                print("DEBUG: Due date is empty, returning None")
                return None  # Return None instead of 0 for empty dates
            
            # Handle different date formats
            due_date_str = due_date_str.strip()
            
            # Try different date formats
            formats_to_try = [
                "%Y-%m-%d",      # 2025-01-15
                "%d/%m/%Y",      # 15/01/2025
                "%d/%m/%y",      # 15/01/25
                "%Y-%m-%d %H:%M:%S",  # 2025-01-15 00:00:00
            ]
            
            due_date_obj = None
            for fmt in formats_to_try:
                try:
                    due_date_obj = datetime.strptime(due_date_str, fmt).date()
                    print(f"DEBUG: Successfully parsed date '{due_date_str}' with format '{fmt}' -> {due_date_obj}")
                    break
                except ValueError:
                    continue
            
            if due_date_obj is None:
                print(f"DEBUG: Could not parse due date '{due_date_str}' with any format")
                return None  # Return None if we can't parse the date
                
            today = date.today()
            delta = (due_date_obj - today).days
            print(f"DEBUG: Due date: {due_date_obj}, Today: {today}, Days difference: {delta}")
            return delta
            
        except Exception as e:
            print(f"DEBUG: Error calculating due date: {e}")
            return None  # Return None instead of 0 for errors
    
    def get_due_status_color(self, days_left):
        """Get status text and color based on days left"""
        if days_left is None:
            return ("📅 No due date set", ("#757575", "#f5f5f5"))
        elif days_left < 0:
            return (f"⚠️ OVERDUE by {abs(days_left)} days", ("#d32f2f", "#ffebee"))
        elif days_left == 0:
            return ("🔥 DUE TODAY", ("#f57c00", "#fff3e0"))
        elif days_left <= 3:
            return (f"⚡ {days_left} days left", ("#ff9800", "#fff8e1"))
        elif days_left <= 7:
            return (f"⏰ {days_left} days left", ("#fbc02d", "#fffde7"))
        else:
            return (f"✅ {days_left} days left", ("#388e3c", "#e8f5e9"))
    
    def collect_payment_for_order(self):
        """Process payment collection for selected order"""
        print(f"\n=== COLLECT PAYMENT DEBUG START ===")
        try:
            # Validate inputs
            if not hasattr(self, 'selected_payment_order') or not self.selected_payment_order:
                print("ERROR: No order selected")
                self.show_status_message("Please select an order first", "warning")
                return
            
            amount_str = self.payment_amount_entry.get().strip()
            print(f"Raw amount from entry field: '{amount_str}'")
            
            if not amount_str:
                print("ERROR: No amount entered")
                self.show_status_message("Please enter payment amount", "warning")
                return
            
            try:
                amount = float(amount_str)
                print(f"Converted amount to float: {amount} (type: {type(amount)})")
            except ValueError as e:
                print(f"ERROR: Cannot convert amount to float: {e}")
                self.show_status_message("Please enter a valid numeric amount", "warning")
                return
            
            if amount <= 0:
                print(f"ERROR: Amount <= 0: {amount}")
                self.show_status_message("Payment amount must be greater than 0", "warning")
                return
            
            order = self.selected_payment_order
            due_amount = order.get('due_amount', 0)
            print(f"Order due amount: {due_amount}")
            
            if amount > due_amount:
                print(f"ERROR: Payment amount {amount} exceeds due amount {due_amount}")
                self.show_status_message("Payment amount cannot exceed due amount", "warning")
                return
            
            # Get payment method and notes
            payment_method = self.payment_method_combo.get()
            notes = self.payment_notes_entry.get().strip()
            print(f"Payment method: {payment_method}")
            print(f"Notes: '{notes}'")
            
            # Create transaction with correct field structure
            transaction_data = {
                'transaction_id': self.generate_transaction_id(),
                'order_id': order.get('order_id'),
                'customer_name': order.get('customer_name'),
                'item_name': order.get('item_name'),
                'transaction_type': 'Payment',
                'amount': amount,  # This should be the float value
                'payment_method': payment_method,
                'transaction_date': date.today().strftime("%Y-%m-%d"),
                'transaction_time': datetime.now().strftime("%H:%M:%S"),
                'notes': notes or f'Payment collection via {payment_method}',
                'status': 'Completed'
            }
            
            print(f"Transaction data to save:")
            for key, value in transaction_data.items():
                print(f"  {key}: {value} (type: {type(value)})")
            
            # CRITICAL DEBUG: Verify amount is still correct before saving
            print(f"CRITICAL CHECK - Amount before saving: {transaction_data['amount']} (type: {type(transaction_data['amount'])})")
            
            # Save transaction to database
            from data_service import DataService
            data_service = DataService()
            print(f"About to call data_service.add_transaction()...")
            result = data_service.add_transaction(transaction_data)
            print(f"Transaction save result: {result}")
            
            # Check if transaction was saved successfully (result should be document ID string)
            if result and isinstance(result, str):
                print(f"Transaction saved successfully with ID: {result}")
                
                # IMPORTANT: For payment collection, we should ONLY reduce due amount, not increase advance
                # Get fresh order data to avoid stale data issues
                fresh_order = data_service.get_order_by_id(order.get('order_id'))
                if fresh_order:
                    current_advance = fresh_order.get('advance_payment', 0)  # Keep advance as is
                    current_total = fresh_order.get('total_amount', 0)
                    current_due = fresh_order.get('due_amount', 0)
                else:
                    current_advance = order.get('advance_payment', 0)  # Keep advance as is
                    current_total = order.get('total_amount', 0)
                    current_due = order.get('due_amount', 0)
                
                # Calculate new amounts - ONLY reduce due amount, don't touch advance
                new_due = max(0, current_due - amount)  # Reduce due by payment amount
                # Keep advance payment unchanged for existing orders
                new_advance = current_advance
                
                # Auto-determine order status based on remaining due amount
                order_status = "Complete" if new_due <= 0 else "Incomplete"
                
                # Debug information
                print(f"Order payment calculation (CORRECT LOGIC):")
                print(f"  Order ID: {order.get('order_id')}")
                print(f"  Payment amount: {amount}")
                print(f"  Current advance (unchanged): {current_advance}")
                print(f"  Current due before payment: {current_due}")
                print(f"  Current total: {current_total}")
                print(f"  New due after payment: {new_due}")
                print(f"  New advance (unchanged): {new_advance}")
                print(f"  New status: {order_status}")
                
                update_data = {
                    'advance_payment': new_advance,  # Keep advance unchanged
                    'due_amount': new_due,           # Only reduce due amount
                    'order_status': order_status
                }
                
                print(f"About to update order with data: {update_data}")
                update_result = data_service.update_order(order.get('order_id'), update_data)
                print(f"Order update result: {update_result}")
                
                # Check if order update was successful (update_result should be number of modified documents)
                if update_result and update_result > 0:
                    # Enhanced success message with payment details
                    success_msg = f"💰 Payment Collected Successfully!\n\n"
                    success_msg += f"Transaction ID: {transaction_data['transaction_id']}\n"
                    success_msg += f"Order ID: {order.get('order_id')}\n"
                    success_msg += f"Customer: {order.get('customer_name')}\n"
                    success_msg += f"Payment Amount: ₹{amount:.2f}\n"
                    success_msg += f"Payment Method: {payment_method}\n"
                    success_msg += f"Remaining Due: ₹{new_due:.2f}\n"
                    success_msg += f"Order Status: {order_status}"
                    
                    print(f"Success message: {success_msg}")
                    self.show_success_message(success_msg)
                    
                    # Clear form and reload data to refresh everything
                    self.clear_payment_form()
                    
                    # Force refresh all relevant data displays
                    self.load_due_orders_data()
                    
                    # Force refresh the selected order details to show updated amounts
                    self.refresh_order_details_display()
                    
                    # Force refresh the main orders table
                    if hasattr(self, 'refresh_orders_table'):
                        self.refresh_orders_table()
                    
                    print("All views refreshed successfully")
                else:
                    print("ERROR: Failed to update order")
                    self.show_error_message("Transaction recorded but failed to update order. Please contact support.")
            else:
                print(f"ERROR: Failed to save transaction: {result}")
                self.show_error_message(f"Failed to record payment: {result}")
                
        except ValueError as e:
            print(f"ValueError: {e}")
            self.show_status_message("Please enter a valid numeric amount", "warning")
        except Exception as e:
            print(f"Exception in collect_payment_for_order: {e}")
            import traceback
            traceback.print_exc()
            self.show_status_message(f"Error processing payment: {str(e)}", "error")
        
        print(f"=== COLLECT PAYMENT DEBUG END ===\n")
    
    def clear_payment_form(self):
        """Clear payment collection form"""
        try:
            # Reset dropdowns
            self.customer_dropdown.set("Select customer...")
            self.order_dropdown.set("Select customer first...")
            
            # Clear form fields
            self.payment_amount_entry.delete(0, 'end')
            self.payment_method_combo.set("Cash")
            self.payment_notes_entry.delete(0, 'end')
            
            # Clear selected order
            if hasattr(self, 'selected_payment_order'):
                delattr(self, 'selected_payment_order')
            
            # Update order details panel
            self.update_large_order_details(None)
            
            # Reload data to refresh dropdowns
            self.load_due_orders_data()
            
        except Exception as e:
            print(f"Error clearing payment form: {e}")
    
    def clear_sales_content(self):
        """Clear the sales content frame"""
        for widget in self.sales_content_frame.winfo_children():
            widget.destroy()
    
    def create_purchases_form(self, form_panel, data_panel):
        """Create modern purchases form"""
        # Form header
        form_header = ctk.CTkFrame(form_panel, height=40, corner_radius=6)  # Reduced from 60 to 40
        form_header.pack(fill="x", padx=12, pady=(10, 8))  # Reduced padding
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="🛒 Purchase Record",
            font=ctk.CTkFont(size=14, weight="bold")  # Reduced from 18 to 14
        ).pack(pady=10)  # Reduced from 15 to 10
        
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
                # Create special date field with calendar
                self.create_date_field_with_calendar(form_scroll, label, key, self.purchase_vars)
            else:
                self.create_form_field(form_scroll, label, key, field_type, self.purchase_vars)
        
        # Form buttons
        self.create_form_buttons(form_scroll, "purchases")
        
        # Data table
        self.create_data_table(data_panel, "purchases")
    
    def create_date_field_with_calendar(self, parent, label, key, var_dict):
        """Create a date field with calendar popup using dd/mm/yy format - PURCHASE VERSION"""
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
        
        # Date input container
        date_container = ctk.CTkFrame(field_frame, fg_color="transparent")
        date_container.pack(fill="x")
        
        # Initialize variable with today's date in dd/mm/yy format
        var_dict[key] = tk.StringVar()
        var_dict[key].set(date.today().strftime("%d/%m/%y"))
        
        # Entry field for date
        date_entry = ctk.CTkEntry(
            date_container,
            textvariable=var_dict[key],
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            placeholder_text="dd/mm/yy"
        )
        date_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Calendar button - use separate method for purchases
        calendar_btn = ctk.CTkButton(
            date_container,
            text="📅",
            width=35,
            height=35,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary']),
            command=lambda: self.show_purchase_calendar(var_dict[key])
        )
        calendar_btn.pack(side="right")
        
        # Store references for validation
        if not hasattr(self, 'field_widgets'):
            self.field_widgets = {}
        self.field_widgets[f'purchase_{key}'] = {
            'entry': date_entry,
            'var': var_dict[key],
            'type': 'date'
        }
    
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
        if hasattr(self, 'emp_vars') and key in ['employee_id', 'name', 'aadhar_no', 'phone', 'daily_wage']:
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
            "employees": ["Employee_ID", "Name", "Aadhar_No", "Phone", "Department", "Position", "Daily_Wage", "Join_Date", "Last_Paid"],
            "attendance": ["Employee_ID", "Date", "Time_In", "Time_Out", "Status", "Hours", "Exception_Hours"],
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
                
                # Convert daily_wage to float after validation
                if data.get("daily_wage"):
                    data["daily_wage"] = float(data["daily_wage"])
                # Add joining date as datetime - handle dd/mm/yy format
                if data.get("join_date"):
                    try:
                        date_str = data["join_date"]
                        if '/' in date_str and len(date_str) <= 8:
                            data["hire_date"] = datetime.strptime(date_str, '%d/%m/%y')
                        elif '-' in date_str and len(date_str) == 10:
                            data["hire_date"] = datetime.strptime(date_str, '%Y-%m-%d')
                        else:
                            data["hire_date"] = datetime.strptime(date_str, '%Y-%m-%d')  # Fallback
                        del data["join_date"]  # Remove old key
                    except ValueError as e:
                        self.show_status_message(f"Invalid date format: {e}", "error")
                        return
                
                # Add last_paid field (initialize as None for new employees)
                data["last_paid"] = None
                
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
                    # For absent/leave, clear time fields
                    data["time_in"] = ""
                    data["time_out"] = ""
                    data["overtime_hour"] = 0  # No overtime for absent/leave
                else:
                    # For other statuses, validate user provided times
                    time_in = data.get("time_in", "").strip()
                    time_out = data.get("time_out", "").strip()
                    
                    # Check if user provided valid times
                    if not time_in or time_in in ["--:--", "", "00:00"]:
                        # No time provided, ask user or use sensible default
                        self.show_status_message("Please set Time In using the time picker dropdowns", "warning")
                        return
                        
                    if not time_out or time_out in ["--:--", "", "00:00"]:
                        # No time provided, ask user or use sensible default  
                        self.show_status_message("Please set Time Out using the time picker dropdowns", "warning")
                        return
                        
                    # User provided valid times, use them as-is
                    data["time_in"] = time_in
                    data["time_out"] = time_out
                
                # Handle exception hours (always save, default 1)
                exception_hours = data.get("exception_hours", "1")
                try:
                    data["exception_hours"] = float(exception_hours) if exception_hours else 1.0
                except (ValueError, TypeError):
                    data["exception_hours"] = 1.0
                
                # For backward compatibility, also save as overtime_hour (will be removed later)
                data["overtime_hour"] = 0  # No overtime in new system
                
                result = self.data_service.add_attendance(data)
                
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
                
                # Validate required fields
                if not data.get("item_name"):
                    self.show_status_message("Item name is required", "error")
                    return
                if not data.get("quantity"):
                    self.show_status_message("Quantity is required", "error")
                    return
                if not data.get("price_per_unit"):
                    self.show_status_message("Purchase price is required", "error")
                    return
                if not data.get("supplier"):
                    self.show_status_message("Supplier is required", "error")
                    return
                if not data.get("date"):
                    self.show_status_message("Purchase date is required", "error")
                    return
                
                # Convert data types
                try:
                    if data.get("quantity"):
                        data["quantity"] = int(data["quantity"])
                    if data.get("price_per_unit"):
                        # Rename to match database schema
                        data["unit_price"] = float(data.pop("price_per_unit"))
                except ValueError as e:
                    self.show_status_message("Please enter valid numbers for quantity and price", "error")
                    return
                
                # Convert date from dd/mm/yy to datetime object
                try:
                    if data.get("date"):
                        date_str = data["date"]
                        # Handle dd/mm/yy format
                        if "/" in date_str and len(date_str.split("/")) == 3:
                            day, month, year = date_str.split("/")
                            # Handle 2-digit year (convert to 4-digit)
                            if len(year) == 2:
                                year = "20" + year if int(year) < 50 else "19" + year
                            # Create datetime object
                            data["date"] = datetime(int(year), int(month), int(day))
                        else:
                            # Fallback: try to parse as is
                            data["date"] = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError as e:
                    self.show_status_message("Please enter date in dd/mm/yy format", "error")
                    return
                
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
                self.emp_vars["aadhar_no"].set(values[2])     # Aadhar No (not email)
                self.emp_vars["phone"].set(values[3])         # Phone
                self.emp_vars["department"].set(values[4])    # Department
                self.emp_vars["position"].set(values[5])      # Position
                # Remove currency formatting for daily wage
                daily_wage_str = str(values[6]).replace("₹", "").replace(",", "")
                self.emp_vars["daily_wage"].set(daily_wage_str)
                
                # Set join_date if available (values[7])
                if len(values) > 7 and values[7] and values[7] != "Not Set":
                    join_date_str = str(values[7])
                    # Convert from display format to form format if needed
                    if '/' in join_date_str and len(join_date_str) <= 8:
                        # Convert dd/mm/yy to YYYY-MM-DD for form input
                        try:
                            date_obj = datetime.strptime(join_date_str, '%d/%m/%y')
                            self.emp_vars["join_date"].set(date_obj.strftime('%Y-%m-%d'))
                        except:
                            self.emp_vars["join_date"].set(join_date_str)
                    else:
                        self.emp_vars["join_date"].set(join_date_str)
                
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
            
            # Validate employee data with field-specific feedback
            is_valid, error_message = self.validate_employee_data_with_feedback(data)
            if not is_valid:
                self.show_status_message(f"Validation Error: {error_message}", "error")
                return
            
            # Use the MongoDB ID if available, otherwise use employee_id for lookup
            if hasattr(self, 'editing_mongo_id') and self.editing_mongo_id:
                # Use MongoDB ID for direct update
                update_data = {k: v for k, v in data.items() if k != "employee_id"}
                if update_data.get("daily_wage"):
                    update_data["daily_wage"] = float(update_data["daily_wage"])
                
                # Convert join_date from dd/mm/yy to datetime
                if update_data.get("join_date"):
                    try:
                        date_str = update_data["join_date"]
                        if '/' in date_str and len(date_str) <= 8:
                            update_data["join_date"] = datetime.strptime(date_str, '%d/%m/%y')
                        elif '-' in date_str and len(date_str) == 10:
                            update_data["join_date"] = datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        pass  # Keep original value if parsing fails
                
                result = self.data_service.update_employee_by_id(self.editing_mongo_id, update_data)
            else:
                # Fallback to employee_id based update
                employee_id = str(self.editing_employee_id)
                update_data = {k: v for k, v in data.items() if k != "employee_id"}
                if update_data.get("daily_wage"):
                    update_data["daily_wage"] = float(update_data["daily_wage"])
                
                # Convert join_date from dd/mm/yy to datetime
                if update_data.get("join_date"):
                    try:
                        date_str = update_data["join_date"]
                        if '/' in date_str and len(date_str) <= 8:
                            update_data["join_date"] = datetime.strptime(date_str, '%d/%m/%y')
                        elif '-' in date_str and len(date_str) == 10:
                            update_data["join_date"] = datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        pass  # Keep original value if parsing fails
                
                result = self.data_service.update_employee(employee_id, update_data)
            
            if result > 0:
                self.show_status_message(f"Employee updated successfully!", "success")
                self.refresh_table("employees")
                self.cancel_edit_record("employees")
            else:
                self.show_status_message(f"Failed to update employee", "error")
                
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
            
            if not mongo_id:
                self.show_status_message(f"Missing database ID for {module_type[:-1]} - cannot edit", "error")
                return
            
            # Call specific edit method based on module type
            if module_type == "employees":
                self.edit_employee_data(values, mongo_id)
            elif module_type == "attendance":
                self.edit_attendance_data(values, mongo_id)
            elif module_type == "sales":
                self.edit_sales_data(values, mongo_id)
            elif module_type == "purchases":
                self.edit_purchases_data(values, mongo_id)
                
        except Exception as e:
            self.show_status_message(f"Failed to load {module_type[:-1]} for editing: {str(e)}", "error")
    
    def edit_employee_data(self, values, mongo_id=None):
        """Edit employee specific data"""
        if hasattr(self, 'emp_vars'):
            self.emp_vars["employee_id"].set(values[0])
            self.emp_vars["name"].set(values[1])
            self.emp_vars["aadhar_no"].set(values[2])     # Aadhar No (not email)
            self.emp_vars["phone"].set(values[3])
            self.emp_vars["department"].set(values[4])
            self.emp_vars["position"].set(values[5])
            # Handle daily wage (column 6)
            daily_wage_str = str(values[6]).replace("₹", "").replace(",", "")
            self.emp_vars["daily_wage"].set(daily_wage_str)
            
            # Store for editing - use the actual employee_id for string operations
            employee_id = str(values[0])
            self.editing_employee_id = employee_id
            self.editing_mongo_id = mongo_id
            
            # Set edit mode
            self.edit_mode = True
            self.edit_module_type = "employees"
            
            # Show edit buttons and change add button
            self.show_edit_buttons("employees")
            
            self.show_status_message(f"Editing employee: {values[1]} ({employee_id}). Modify fields and save.", "info")
                
    # ====== ORDERS AND TRANSACTIONS IMPLEMENTATION ======
    
    def create_new_order(self):
        """Create a new order from form data"""
        try:
            # Check if order_vars exists
            if not hasattr(self, 'order_vars') or not self.order_vars:
                self.show_status_message("Form not properly initialized. Please try again.", "error")
                return
                
            # Check if order service is available
            if not self.order_service:
                self.show_status_message("Order service not available. Please restart the application.", "error")
                return
            
            # Validate required fields
            required_fields = ['customer_name', 'customer_phone', 'item_name', 'quantity', 'unit_price']
            optional_fields = ['customer_address', 'advance_payment', 'due_date', 'payment_method']
            
            for field in required_fields:
                if field not in self.order_vars:
                    self.show_status_message(f"Form field {field} not found. Please reload the form.", "error")
                    return
                    
                field_value = self.order_vars[field].get().strip()
                if not field_value:
                    self.show_status_message(f"Please enter {field.replace('_', ' ').title()}", "warning")
                    return
            
            for field in optional_fields:
                if field not in self.order_vars:
                    # Add missing optional fields with defaults
                    if field == 'customer_address':
                        self.order_vars[field] = tk.StringVar(value="")
                    elif field == 'advance_payment':
                        self.order_vars[field] = tk.StringVar(value="0")
                    elif field == 'due_date':
                        self.order_vars[field] = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
                    elif field == 'payment_method':
                        self.order_vars[field] = tk.StringVar(value="Cash")
            
            # Check if customer exists, if not create new customer
            customer_name = self.order_vars['customer_name'].get().strip()
            customer_phone = self.order_vars['customer_phone'].get().strip()
            customer_address = self.order_vars['customer_address'].get().strip()
            
            existing_customer = self.order_service.get_customer_by_name(customer_name) if self.order_service else None
            
            if not existing_customer and self.order_service:
                # Create new customer automatically
                try:
                    new_customer_data = {
                        'name': customer_name,
                        'contact_number': customer_phone,
                        'gst_number': '',  # Empty for now
                        'address': customer_address
                    }
                    self.order_service.add_customer(new_customer_data)
                    logger.info(f"Automatically created new customer: {customer_name}")
                except Exception as e:
                    logger.warning(f"Failed to auto-create customer: {str(e)}")
            
            # Calculate amounts and auto-determine status
            quantity = int(self.order_vars['quantity'].get())
            unit_price = float(self.order_vars['unit_price'].get())
            total_amount = quantity * unit_price
            advance_payment = float(self.order_vars['advance_payment'].get()) if self.order_vars['advance_payment'].get() else 0.0
            due_amount = max(0, total_amount - advance_payment)
            
            # Auto-determine order status based on payment
            order_status = "Complete" if due_amount <= 0 and total_amount > 0 else "Incomplete"
            
            # Generate order ID
            order_id = self.generate_order_id()
            
            # Prepare order data
            order_data = {
                'order_id': order_id,
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'customer_address': customer_address,
                'item_name': self.order_vars['item_name'].get().strip(),
                'quantity': quantity,
                'unit_price': unit_price,
                'total_amount': total_amount,
                'advance_payment': advance_payment,
                'due_amount': due_amount,
                'order_status': order_status,  # Auto-determined status
                'payment_method': self.order_vars['payment_method'].get(),
                'due_date': self.order_vars['due_date'].get(),
                'order_date': date.today().strftime("%Y-%m-%d"),
                'created_date': datetime.now().isoformat()
            }
            
            # Save to database
            result = self.order_service.add_order(order_data) if self.order_service else None
            
            if result:
                # Update customer due payments after order creation
                if self.order_service:
                    self.order_service.update_all_customer_due_payments()
                
                # Create initial transaction if advance payment exists
                if advance_payment > 0:
                    self.create_initial_transaction(order_id, advance_payment, self.order_vars['payment_method'].get())
                
                # Enhanced success message with order details
                success_msg = f"✅ Order Created Successfully!\n\n"
                success_msg += f"Order ID: {order_id}\n"
                success_msg += f"Customer: {customer_name}\n"
                success_msg += f"Item: {self.order_vars['item_name'].get().strip()}\n"
                success_msg += f"Total Amount: ₹{total_amount:.2f}\n"
                success_msg += f"Status: {order_status}"
                
                if not existing_customer:
                    success_msg += f"\n\n📝 New customer '{customer_name}' added automatically!"
                
                self.show_success_message(success_msg)
                self.clear_order_form()
                # Switch to orders management view
                self.show_orders_management()
            else:
                self.show_status_message("Failed to create order", "error")
                
        except ValueError as e:
            self.show_status_message("Please enter valid numeric values for quantity and price", "warning")
        except Exception as e:
            self.show_status_message(f"Failed to create order: {str(e)}", "error")
    
    def generate_order_id(self):
        """Generate unique order ID"""
        import random
        import string
        timestamp = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"ORD{timestamp}{random_part}"
    
    def create_initial_transaction(self, order_id, amount, payment_method):
        """Create initial transaction for advance payment"""
        try:
            print(f"DEBUG: Creating initial transaction - Order ID: {order_id}, Amount: {amount}, Type: {type(amount)}")
            
            # Ensure amount is a float
            try:
                amount_float = float(amount) if amount is not None else 0.0
            except (ValueError, TypeError):
                amount_float = 0.0
                
            print(f"DEBUG: Converted amount to float: {amount_float}")
            
            transaction_data = {
                'transaction_id': self.generate_transaction_id(),
                'order_id': order_id,
                'amount': amount_float,  # Use 'amount' to match other transactions
                'payment_date': date.today().strftime("%Y-%m-%d"),
                'payment_method': payment_method,
                'transaction_type': 'advance_payment',
                'notes': 'Initial advance payment',
                'created_date': datetime.now().isoformat()
            }
            
            print(f"DEBUG: Transaction data: {transaction_data}")
            
            from data_service import DataService
            data_service = DataService()
            result = data_service.add_transaction(transaction_data)
            
            print(f"DEBUG: Transaction creation result: {result}")
            
        except Exception as e:
            print(f"Error creating initial transaction: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        import random
        import string
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = ''.join(random.choices(string.digits, k=3))
        return f"TXN{timestamp}{random_part}"
    
    def clear_order_form(self):
        """Clear all order form fields"""
        try:
            for var in self.order_vars.values():
                var.set("")
            
            # Reset dropdowns to default values
            if 'order_status' in self.order_vars:
                self.order_vars['order_status'].set("Pending")
            if 'payment_method' in self.order_vars:
                self.order_vars['payment_method'].set("Cash")
            if 'due_date' in self.order_vars:
                self.order_vars['due_date'].set(date.today().strftime("%Y-%m-%d"))
            
            # Refresh customer dropdown with latest customers
            if hasattr(self, 'customer_name_combo'):
                try:
                    service = self.order_service if self.order_service else self.data_service
                    customers_df = service.get_customers()
                    customer_names = [""] + customers_df['name'].tolist() if not customers_df.empty else [""]
                    self.customer_name_combo.configure(values=customer_names)
                except:
                    pass
                
        except Exception as e:
            print(f"Error clearing order form: {e}")
    
    def refresh_orders_table(self):
        """Refresh the orders table with latest data"""
        try:
            # Clear existing data
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)
            
            # Get orders from database using order_service
            service = self.order_service
            if not service:
                from data_service import DataService
                service = DataService()
            orders = service.get_all_orders()
            
            # Populate table
            for order in orders:
                order_id = order.get('order_id', 'N/A')
                customer = order.get('customer_name', 'N/A')
                phone = order.get('customer_phone', 'N/A')
                item = order.get('item_name', 'N/A')
                quantity = order.get('quantity', 0)
                total_amount = order.get('total_amount', 0)
                advance_paid = order.get('advance_payment', 0)
                due_amount = order.get('due_amount', 0)
                status = order.get('order_status', 'N/A')
                due_date = order.get('due_date', 'N/A')
                
                # Insert with MongoDB ID as tag
                mongo_id = str(order.get('_id', ''))
                self.orders_tree.insert("", "end", values=(
                    order_id, customer, phone, item, quantity,
                    f"₹{total_amount:.2f}", f"₹{advance_paid:.2f}", f"₹{due_amount:.2f}",
                    status, due_date
                ), tags=(mongo_id,))
                
        except Exception as e:
            self.show_status_message(f"Error loading orders: {str(e)}", "error")
    
    def on_order_selection(self, event):
        """Handle order selection in the table"""
        try:
            selection = self.orders_tree.selection()
            if selection:
                item = self.orders_tree.item(selection[0])
                values = item['values']
                tags = self.orders_tree.item(selection[0], 'tags')
                
                # Store selected order info
                self.selected_order_id = values[0]  # Order ID
                self.selected_mongo_id = tags[0] if tags else None
                
                # Refresh the details view if currently showing details
                if hasattr(self, 'current_details_tab'):
                    self.switch_details_tab(self.current_details_tab)
                    
        except Exception as e:
            print(f"Error handling order selection: {e}")
    
    def get_order_by_id(self, order_id):
        """Get order data by order ID"""
        try:
            service = self.order_service
            if not service:
                from data_service import DataService
                service = DataService()
            return service.get_order_by_id(order_id)
        except Exception as e:
            print(f"Error getting order data: {e}")
            return None
    
    def add_payment_transaction(self):
        """Add a new payment transaction for selected order"""
        try:
            if not hasattr(self, 'selected_order_id') or not self.selected_order_id:
                self.show_status_message("Please select an order first", "warning")
                return
            
            amount_str = self.payment_amount_var.get().strip()
            if not amount_str:
                self.show_status_message("Please enter payment amount", "warning")
                return
            
            amount = float(amount_str)
            if amount <= 0:
                self.show_status_message("Payment amount must be greater than 0", "warning")
                return
            
            # Create transaction data
            transaction_data = {
                'transaction_id': self.generate_transaction_id(),
                'order_id': self.selected_order_id,
                'payment_amount': amount,
                'payment_date': date.today().strftime("%Y-%m-%d"),
                'payment_method': self.payment_method_var.get(),
                'transaction_type': 'payment',
                'notes': f'Payment via {self.payment_method_var.get()}',
                'created_date': datetime.now().isoformat()
            }
            
            # Save transaction
            from data_service import DataService
            data_service = DataService()
            result = data_service.add_transaction(transaction_data)
            
            if result:
                # Update order's advance payment amount
                order_data = self.get_order_by_id(self.selected_order_id)
                if order_data:
                    new_advance = order_data.get('advance_payment', 0) + amount
                    new_due = order_data.get('total_amount', 0) - new_advance
                    
                    update_data = {
                        'advance_payment': new_advance,
                        'due_amount': new_due
                    }
                    
                    # Update payment status if fully paid
                    if new_due <= 0:
                        update_data['order_status'] = 'Paid'
                    
                    data_service.update_order(self.selected_order_id, update_data)
                
                self.show_status_message(f"Payment of ₹{amount:.2f} added successfully!", "success")
                
                # Clear form and refresh
                self.payment_amount_var.set("")
                self.payment_method_var.set("Cash")
                self.refresh_orders_table()
                self.refresh_transactions_table()
                
                # Refresh payment summary if in payments tab
                if hasattr(self, 'current_details_tab') and self.current_details_tab == "payments":
                    self.switch_details_tab("payments")
                    
            else:
                self.show_status_message("Failed to add payment", "error")
                
        except ValueError:
            self.show_status_message("Please enter a valid numeric amount", "warning")
        except Exception as e:
            self.show_status_message(f"Error adding payment: {str(e)}", "error")
    
    def refresh_transactions_table(self):
        """Refresh transactions table for selected order"""
        try:
            if not hasattr(self, 'transactions_tree'):
                return
                
            # Clear existing data
            for item in self.transactions_tree.get_children():
                self.transactions_tree.delete(item)
            
            if not hasattr(self, 'selected_order_id') or not self.selected_order_id:
                return
            
            # Get transactions for selected order
            from data_service import DataService
            data_service = DataService()
            transactions = data_service.get_transactions_by_order(self.selected_order_id)
            
            # Populate table
            for transaction in transactions:
                trans_id = transaction.get('transaction_id', 'N/A')
                trans_date = transaction.get('payment_date', 'N/A')
                # Check for both 'amount' and 'payment_amount' for backward compatibility
                amount = transaction.get('amount', transaction.get('payment_amount', 0))
                method = transaction.get('payment_method', 'N/A')
                notes = transaction.get('notes', 'N/A')
                
                print(f"DEBUG: Displaying transaction - ID: {trans_id}, Amount: {amount}, Type: {type(amount)}")
                
                # Ensure amount is properly formatted
                try:
                    amount_float = float(amount) if amount is not None else 0.0
                except (ValueError, TypeError):
                    amount_float = 0.0
                    print(f"DEBUG: Could not convert amount '{amount}' to float, using 0.0")
                
                self.transactions_tree.insert("", "end", values=(
                    trans_id, trans_date, f"₹{amount_float:.2f}", method, notes
                ))
                
        except Exception as e:
            print(f"Error refreshing transactions: {e}")
    
    def refresh_all_transactions_table(self):
        """Refresh all transactions table"""
        try:
            if not hasattr(self, 'all_transactions_tree'):
                return
                
            # Clear existing data
            for item in self.all_transactions_tree.get_children():
                self.all_transactions_tree.delete(item)
            
            # Get all transactions
            from data_service import DataService
            data_service = DataService()
            transactions = data_service.get_all_transactions_with_orders()
            
            # Populate table
            for transaction in transactions:
                trans_id = transaction.get('transaction_id', 'N/A')
                order_id = transaction.get('order_id', 'N/A')
                customer = transaction.get('customer_name', 'N/A')
                trans_date = transaction.get('transaction_date', transaction.get('payment_date', 'N/A'))
                # Check for both 'amount' and 'payment_amount' for backward compatibility
                amount = transaction.get('amount', transaction.get('payment_amount', 0))
                method = transaction.get('payment_method', 'N/A')
                order_status = transaction.get('order_status', 'N/A')
                notes = transaction.get('notes', 'N/A')
                
                # Ensure amount is properly formatted
                try:
                    amount_float = float(amount) if amount is not None else 0.0
                except (ValueError, TypeError):
                    amount_float = 0.0
                
                self.all_transactions_tree.insert("", "end", values=(
                    trans_id, order_id, customer, trans_date, f"₹{amount_float:.2f}",
                    method, order_status, notes
                ))
                
        except Exception as e:
            print(f"Error refreshing all transactions: {e}")
    
    def delete_selected_transaction(self):
        """Delete the selected transaction"""
        try:
            # Get selected item
            selected_item = self.all_transactions_tree.selection()
            if not selected_item:
                self.show_error_message("Please select a transaction to delete")
                return
            
            # Get transaction details
            values = self.all_transactions_tree.item(selected_item[0])['values']
            if not values:
                self.show_error_message("Unable to get transaction details")
                return
            
            transaction_id = values[0]  # Transaction ID is first column
            customer_name = values[2]   # Customer name is third column
            amount = values[4]          # Amount is fifth column
            
            # Confirmation dialog
            import tkinter as tk
            from tkinter import messagebox
            
            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete this transaction?\n\n"
                f"Transaction ID: {transaction_id}\n"
                f"Customer: {customer_name}\n"
                f"Amount: {amount}\n\n"
                f"⚠️ This action cannot be undone!"
            )
            
            if not confirm:
                return
            
            # Delete from database
            from data_service import DataService
            data_service = DataService()
            result = data_service.delete_transaction(transaction_id)
            
            if result.get('success'):
                self.show_success_message(f"Transaction {transaction_id} deleted successfully!")
                self.refresh_all_transactions_table()
                
                # Also refresh orders if needed
                if hasattr(self, 'load_orders_data'):
                    self.load_orders_data()
                if hasattr(self, 'load_due_orders_data'):
                    self.load_due_orders_data()
            else:
                self.show_error_message(f"Failed to delete transaction: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            self.show_error_message(f"Error deleting transaction: {str(e)}")
            print(f"Error in delete_selected_transaction: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_order_details_display(self):
        """Refresh the order details display in payment collection page"""
        try:
            if hasattr(self, 'selected_payment_order') and self.selected_payment_order:
                # Reload the order from database to get updated amounts
                from data_service import DataService
                data_service = DataService()
                updated_order = data_service.get_order_by_id(self.selected_payment_order['order_id'])
                
                if updated_order:
                    self.selected_payment_order = updated_order
                    # Refresh the order details panel
                    self.update_order_details_panel()
                    
        except Exception as e:
            print(f"Error refreshing order details: {e}")
    
    def update_order_details_panel(self):
        """Update the order details panel with current order data"""
        try:
            if hasattr(self, 'selected_payment_order') and self.selected_payment_order:
                order = self.selected_payment_order
                
                # Update the order information displayed
                if hasattr(self, 'order_details_frame'):
                    # Clear existing details
                    for widget in self.order_details_frame.winfo_children():
                        widget.destroy()
                    
                    # Recreate the order details section
                    self.create_order_details_section(self.order_details_frame, order)
                    
        except Exception as e:
            print(f"Error updating order details panel: {e}")
    
    def change_order_due_date(self, order_data):
        """Open dialog to change order due date"""
        try:
            import tkinter as tk
            from tkinter import messagebox, ttk
            from datetime import datetime, date
            
            # Create dialog window
            dialog = tk.Toplevel()
            dialog.title("📅 Change Due Date")
            dialog.geometry("450x350")
            dialog.resizable(False, False)
            dialog.configure(bg="#f0f8ff")
            dialog.grab_set()  # Make modal
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Header
            header_frame = tk.Frame(dialog, bg="#e3f2fd", height=60)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            
            tk.Label(
                header_frame,
                text="📅 Change Due Date",
                font=("Arial", 16, "bold"),
                bg="#e3f2fd",
                fg="#1565c0"
            ).pack(pady=15)
            
            # Content frame
            content_frame = tk.Frame(dialog, bg="#f0f8ff", padx=30, pady=20)
            content_frame.pack(fill="both", expand=True)
            
            # Current order info
            info_frame = tk.LabelFrame(content_frame, text="Order Information", font=("Arial", 12, "bold"), 
                                     bg="#f0f8ff", fg="#333", padx=15, pady=10)
            info_frame.pack(fill="x", pady=(0, 20))
            
            tk.Label(info_frame, text=f"Order ID: {order_data.get('order_id', 'N/A')}", 
                    font=("Arial", 11), bg="#f0f8ff").pack(anchor="w", pady=2)
            tk.Label(info_frame, text=f"Customer: {order_data.get('customer_name', 'N/A')}", 
                    font=("Arial", 11), bg="#f0f8ff").pack(anchor="w", pady=2)
            tk.Label(info_frame, text=f"Current Due Date: {order_data.get('due_date', 'N/A')}", 
                    font=("Arial", 11, "bold"), bg="#f0f8ff", fg="#d32f2f").pack(anchor="w", pady=2)
            
            # New due date selection
            date_frame = tk.LabelFrame(content_frame, text="New Due Date", font=("Arial", 12, "bold"), 
                                     bg="#f0f8ff", fg="#333", padx=15, pady=10)
            date_frame.pack(fill="x", pady=(0, 20))
            
            # Initialize variables
            cal = None
            date_var = tk.StringVar()
            
            # Try to use calendar widget, with enhanced fallback
            try:
                # Use simple date entry instead of external calendar widget
                date_entry = tk.Entry(
                    date_frame,
                    textvariable=date_var,
                    font=("Arial", 12),
                    width=15,
                    justify="center"
                )
                date_entry.pack(pady=10, padx=10)
                
                # Set today's date as default
                from datetime import date as dt_date
                date_var.set(dt_date.today().strftime('%Y-%m-%d'))
                
                # Instructions for date entry
                tk.Label(
                    date_frame, 
                    text="📅 Enter date in YYYY-MM-DD format",
                    font=("Arial", 10, "italic"), 
                    bg="#f0f8ff", 
                    fg="#666"
                ).pack(pady=(5, 0))
                
            except ImportError:
                # Enhanced fallback with date picker using dropdowns
                tk.Label(date_frame, text="📅 Select New Due Date:", 
                        font=("Arial", 11, "bold"), bg="#f0f8ff").pack(anchor="w", pady=(0, 10))
                
                # Date selection frame
                date_select_frame = tk.Frame(date_frame, bg="#f0f8ff")
                date_select_frame.pack(anchor="w", pady=(0, 10))
                
                # Get current date for defaults
                from datetime import date, timedelta
                today = date.today()
                min_date = today + timedelta(days=1)  # Tomorrow as minimum
                
                # Year dropdown
                tk.Label(date_select_frame, text="Year:", bg="#f0f8ff").grid(row=0, column=0, padx=(0, 5))
                year_var = tk.StringVar(value=str(min_date.year))
                year_combo = ttk.Combobox(date_select_frame, textvariable=year_var, width=8, state="readonly")
                year_combo['values'] = [str(y) for y in range(today.year, today.year + 5)]
                year_combo.grid(row=0, column=1, padx=(0, 15))
                
                # Month dropdown
                tk.Label(date_select_frame, text="Month:", bg="#f0f8ff").grid(row=0, column=2, padx=(0, 5))
                month_var = tk.StringVar(value=f"{min_date.month:02d}")
                month_combo = ttk.Combobox(date_select_frame, textvariable=month_var, width=8, state="readonly")
                month_combo['values'] = [f"{m:02d}" for m in range(1, 13)]
                month_combo.grid(row=0, column=3, padx=(0, 15))
                
                # Day dropdown
                tk.Label(date_select_frame, text="Day:", bg="#f0f8ff").grid(row=0, column=4, padx=(0, 5))
                day_var = tk.StringVar(value=f"{min_date.day:02d}")
                day_combo = ttk.Combobox(date_select_frame, textvariable=day_var, width=8, state="readonly")
                day_combo['values'] = [f"{d:02d}" for d in range(1, 32)]
                day_combo.grid(row=0, column=5)
                
                # Function to construct date from dropdowns
                def get_manual_date():
                    return f"{year_var.get()}-{month_var.get()}-{day_var.get()}"
                
                # Override the date variable to use dropdown values
                date_var.get = get_manual_date
            
            # Buttons frame
            button_frame = tk.Frame(content_frame, bg="#f0f8ff")
            button_frame.pack(fill="x", pady=(10, 0))
            
            def save_new_date():
                try:
                    new_date = None
                    
                    if cal:
                        # Not using calendar widget anymore
                        new_date = date_var.get().strip()
                    else:
                        # Using manual entry
                        new_date = date_var.get().strip()
                        print(f"Date from manual entry: {new_date}")
                    
                    if not new_date:
                        messagebox.showerror("Error", "Please select or enter a date")
                        return
                    
                    # Validate date format and ensure it's not in the past
                    try:
                        new_date_obj = datetime.strptime(str(new_date), "%Y-%m-%d").date()
                        if new_date_obj < date.today():
                            messagebox.showerror("Error", "Due date cannot be in the past")
                            return
                        new_date = new_date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Error", "Please enter a valid date in YYYY-MM-DD format")
                        return
                    
                    print(f"Final validated date: {new_date}")
                    
                    # Update order in database
                    from data_service import DataService
                    data_service = DataService()
                    
                    update_data = {'due_date': new_date}
                    result = data_service.update_order(order_data.get('order_id'), update_data)
                    print(f"Database update result: {result}")
                    
                    if result and result > 0:
                        # Update the order data
                        order_data['due_date'] = new_date
                        if hasattr(self, 'selected_payment_order'):
                            self.selected_payment_order['due_date'] = new_date
                        
                        # Refresh the display
                        self.update_payment_order_details(self.selected_payment_order if hasattr(self, 'selected_payment_order') else order_data)
                        
                        # Show success message
                        self.show_success_message(f"✅ Due date updated to {new_date} successfully!")
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to update due date in database")
                        
                except Exception as e:
                    print(f"Error in save_new_date: {e}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("Error", f"Error updating due date: {str(e)}")
            
            def cancel():
                dialog.destroy()
            
            # Save button
            save_btn = tk.Button(
                button_frame,
                text="💾 Save New Date",
                command=save_new_date,
                font=("Arial", 11, "bold"),
                bg="#4caf50",
                fg="white",
                padx=20,
                pady=8,
                cursor="hand2"
            )
            save_btn.pack(side="left", padx=(0, 10))
            
            # Cancel button
            cancel_btn = tk.Button(
                button_frame,
                text="❌ Cancel",
                command=cancel,
                font=("Arial", 11, "bold"),
                bg="#f44336",
                fg="white",
                padx=20,
                pady=8,
                cursor="hand2"
            )
            cancel_btn.pack(side="left")
            
        except Exception as e:
            self.show_error_message(f"Error opening change due date dialog: {str(e)}")
            print(f"Error in change_order_due_date: {e}")
            import traceback
            traceback.print_exc()
    
    def edit_order(self, order_data):
        """Edit selected order"""
        try:
            # Switch to new order form
            self.show_new_order_form()
            
            # Populate form with existing data
            self.order_vars['customer_name'].set(order_data.get('customer_name', ''))
            self.order_vars['customer_phone'].set(order_data.get('customer_phone', ''))
            self.order_vars['customer_address'].set(order_data.get('customer_address', ''))
            self.order_vars['item_name'].set(order_data.get('item_name', ''))
            self.order_vars['quantity'].set(str(order_data.get('quantity', '')))
            self.order_vars['unit_price'].set(str(order_data.get('unit_price', '')))
            self.order_vars['advance_payment'].set(str(order_data.get('advance_payment', '')))
            self.order_vars['order_status'].set(order_data.get('order_status', 'Pending'))
            self.order_vars['payment_method'].set(order_data.get('payment_method', 'Cash'))
            self.order_vars['due_date'].set(order_data.get('due_date', ''))
            
            # Store editing state
            self.editing_order_id = order_data.get('order_id')
            self.editing_order_mongo_id = self.selected_mongo_id
            
            self.show_status_message("Order loaded for editing", "info")
            
        except Exception as e:
            self.show_status_message(f"Error loading order for editing: {str(e)}", "error")
    
    def update_order_status(self, order_data):
        """Update order status with a popup dialog"""
        try:
            import tkinter as tk
            from tkinter import simpledialog
            
            current_status = order_data.get('order_status', 'Pending')
            status_options = ["Pending", "Processing", "Ready", "Delivered", "Cancelled", "Paid"]
            
            # Create status selection dialog
            dialog = tk.Toplevel()
            dialog.title("Update Order Status")
            dialog.geometry("300x200")
            dialog.resizable(False, False)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
            y = (dialog.winfo_screenheight() // 2) - (200 // 2)
            dialog.geometry(f'300x200+{x}+{y}')
            
            tk.Label(dialog, text=f"Current Status: {current_status}", font=('Arial', 12, 'bold')).pack(pady=20)
            tk.Label(dialog, text="Select New Status:", font=('Arial', 10)).pack(pady=(0, 10))
            
            selected_status = tk.StringVar(value=current_status)
            
            for status in status_options:
                tk.Radiobutton(dialog, text=status, variable=selected_status, value=status).pack(anchor='w', padx=50)
            
            def update_status():
                new_status = selected_status.get()
                if new_status != current_status:
                    from data_service import DataService
                    data_service = DataService()
                    result = data_service.update_order(order_data.get('order_id'), {'order_status': new_status})
                    
                    if result:
                        self.show_status_message(f"Order status updated to {new_status}", "success")
                        self.refresh_orders_table()
                        # Refresh current view
                        if hasattr(self, 'current_details_tab'):
                            self.switch_details_tab(self.current_details_tab)
                    else:
                        self.show_status_message("Failed to update order status", "error")
                
                dialog.destroy()
            
            button_frame = tk.Frame(dialog)
            button_frame.pack(side='bottom', pady=20)
            
            tk.Button(button_frame, text="Update", command=update_status, bg='#4CAF50', fg='white', width=10).pack(side='left', padx=5)
            tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg='#f44336', fg='white', width=10).pack(side='left', padx=5)
            
        except Exception as e:
            self.show_status_message(f"Error updating order status: {str(e)}", "error")
    
    def delete_order(self, order_data):
        """Delete selected order with confirmation"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            order_id = order_data.get('order_id')
            customer_name = order_data.get('customer_name')
            
            # Confirm deletion
            result = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete order {order_id} for {customer_name}?\n\nThis action cannot be undone.",
                icon='warning'
            )
            
            if result:
                from data_service import DataService
                data_service = DataService()
                
                # Delete related transactions first
                data_service.delete_transactions_by_order(order_id)
                
                # Delete the order
                delete_result = data_service.delete_order(order_id)
                
                if delete_result:
                    self.show_status_message(f"Order {order_id} deleted successfully", "success")
                    self.refresh_orders_table()
                    
                    # Clear selection and details
                    if hasattr(self, 'selected_order_id'):
                        self.selected_order_id = None
                    self.switch_details_tab(self.current_details_tab)
                else:
                    self.show_status_message("Failed to delete order", "error")
                    
        except Exception as e:
            self.show_status_message(f"Error deleting order: {str(e)}", "error")
    
    def edit_attendance_data(self, values, mongo_id):
        """Edit attendance specific data"""
        if hasattr(self, 'att_vars'):
            # Get the full record from database to get accurate exception_hours value
            try:
                from bson import ObjectId
                attendance_df = self.data_service.get_attendance({"_id": ObjectId(mongo_id)})
                if not attendance_df.empty:
                    record = attendance_df.iloc[0].to_dict()
                    actual_exception_hours = record.get("exception_hours", 1)
                else:
                    actual_exception_hours = 1
            except Exception as e:
                print(f"Error fetching attendance record: {e}")
                actual_exception_hours = 1
            
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
            
            # Convert date from dd/mm/yy display format to YYYY-MM-DD for form
            date_display = str(values[1])
            try:
                if '/' in date_display and len(date_display) <= 8:  # dd/mm/yy format
                    date_obj = datetime.strptime(date_display, '%d/%m/%y')
                    date_form_format = date_obj.strftime('%Y-%m-%d')
                    self.att_vars["date"].set(date_form_format)
                    # Also set the display variable if it exists
                    if hasattr(self, 'attendance_display_vars') and "date" in self.attendance_display_vars:
                        self.attendance_display_vars["date"].set(date_display)
                else:
                    self.att_vars["date"].set(date_display)
                    if hasattr(self, 'attendance_display_vars') and "date" in self.attendance_display_vars:
                        self.attendance_display_vars["date"].set(date_display)
            except:
                self.att_vars["date"].set(date_display)
                if hasattr(self, 'attendance_display_vars') and "date" in self.attendance_display_vars:
                    self.attendance_display_vars["date"].set(date_display)
            
            # Convert times from 12-hour display format to 24-hour for form
            if len(values) > 2:
                time_in_display = str(values[2])
                if time_in_display != 'N/A' and time_in_display:
                    try:
                        # Convert from "2:30 PM" to "14:30"
                        if 'AM' in time_in_display or 'PM' in time_in_display:
                            time_obj = datetime.strptime(time_in_display, '%I:%M %p')
                            time_24hr = time_obj.strftime('%H:%M')
                            self.att_vars["time_in"].set(time_24hr)
                        else:
                            self.att_vars["time_in"].set(time_in_display)
                    except:
                        self.att_vars["time_in"].set('')
                else:
                    self.att_vars["time_in"].set('')
                    
            if len(values) > 3:
                time_out_display = str(values[3])
                if time_out_display != 'N/A' and time_out_display:
                    try:
                        # Convert from "5:30 PM" to "17:30"
                        if 'AM' in time_out_display or 'PM' in time_out_display:
                            time_obj = datetime.strptime(time_out_display, '%I:%M %p')
                            time_24hr = time_obj.strftime('%H:%M')
                            self.att_vars["time_out"].set(time_24hr)
                        else:
                            self.att_vars["time_out"].set(time_out_display)
                    except:
                        self.att_vars["time_out"].set('')
                else:
                    self.att_vars["time_out"].set('')
                    
            if len(values) > 4:
                self.att_vars["status"].set(values[4])
            
            # Set exception hours from actual database record (not table display)
            if hasattr(self, 'att_vars') and "exception_hours" in self.att_vars:
                self.att_vars["exception_hours"].set(str(actual_exception_hours))
            
            # Handle notes field separately (this should come from actual notes field in database)
            # For now, we'll leave notes empty since it's not in the current table display
            if hasattr(self, 'att_vars') and "notes" in self.att_vars:
                self.att_vars["notes"].set("")
            
            self.edit_mode = True
            self.editing_attendance_id = mongo_id  # Use MongoDB ID
            self.edit_module_type = "attendance"
            
            self.show_edit_buttons("attendance")
            self.show_status_message(f"Editing attendance: {employee_id} on {date_display}", "info")
    
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
                
                # Get MongoDB document ID from the item tags for more accurate deletion
                tags = tree.item(item, 'tags')
                mongo_id = tags[0] if tags else None
                
                if not values:
                    continue
                    
                # Build filter for deletion based on module type
                result = False
                if module_type in ["employee", "employees"]:
                    result = self.data_service.delete_employee(values[0])
                elif module_type == "attendance":
                    # Use MongoDB ID for more reliable deletion
                    if mongo_id:
                        result = self.data_service.delete_attendance_by_id(mongo_id)
                    else:
                        # Fallback: Parse date from dd/mm/yy display format
                        date_str = str(values[1])
                        try:
                            # Convert dd/mm/yy to datetime for filtering
                            if '/' in date_str and len(date_str) <= 8:  # dd/mm/yy format
                                filter_date = datetime.strptime(date_str, '%d/%m/%y')
                            else:
                                filter_date = date_str
                            filter_dict = {"employee_id": values[0], "date": filter_date}
                            result = self.data_service.delete_attendance(filter_dict)
                        except Exception as e:
                            logger.error(f"Error parsing date for deletion: {e}")
                            continue
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
                    # Parse date properly for purchase deletion - handle dd/mm/yy format
                    date_str = str(values[4])
                    try:
                        # Check if it's dd/mm/yy format (8 characters or less)
                        if '/' in date_str and len(date_str) <= 8:
                            filter_date = datetime.strptime(date_str, '%d/%m/%y')
                        elif len(date_str) == 10 and '-' in date_str:
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
                
                # Sort attendance by date (newest first) and by insertion order for same dates
                if data_df is not None and not data_df.empty:
                    # Convert date column to datetime for proper sorting
                    data_df['date_for_sorting'] = pd.to_datetime(data_df['date'])
                    
                    # Sort by date descending (newest first), then by index ascending (last added first for same date)
                    data_df = data_df.sort_values(['date_for_sorting'], ascending=[False])
                    data_df = data_df.drop('date_for_sorting', axis=1)  # Remove helper column
                    data_df = data_df.reset_index(drop=True)  # Reset index after sorting
                    
                    # Sort raw_records to match the sorted dataframe order
                    if raw_records and len(raw_records) == len(data_df):
                        # Create a mapping using employee_id and date to match records
                        raw_records_dict = {}
                        for i, record in enumerate(raw_records):
                            key = f"{record.get('employee_id', '')}_{record.get('date', '')}"
                            raw_records_dict[key] = record
                        
                        # Reorder raw_records to match sorted dataframe
                        new_raw_records = []
                        for _, row in data_df.iterrows():
                            key = f"{row.get('employee_id', '')}_{row.get('date', '')}"
                            if key in raw_records_dict:
                                new_raw_records.append(raw_records_dict[key])
                        raw_records = new_raw_records
            elif table_type == "stock":
                data_df = self.data_service.get_stock()
                raw_records = self.data_service.db_manager.find_documents("stock")
            elif table_type == "sales":
                data_df = self.data_service.get_sales()
                raw_records = self.data_service.db_manager.find_documents("sales")
            elif table_type == "purchases":
                data_df = self.data_service.get_purchases()
                raw_records = self.data_service.db_manager.find_documents("purchases")
                
                # Sort purchases by date (newest first)
                if data_df is not None and not data_df.empty:
                    # Convert date column to datetime for proper sorting
                    data_df['date_for_sorting'] = pd.to_datetime(data_df['date'])
                    
                    # Sort by date descending (newest first)
                    data_df = data_df.sort_values(['date_for_sorting'], ascending=[False])
                    data_df = data_df.drop('date_for_sorting', axis=1)  # Remove helper column
                    data_df = data_df.reset_index(drop=True)  # Reset index after sorting
                    
                    # Sort raw_records to match the sorted dataframe order
                    if raw_records and len(raw_records) == len(data_df):
                        # Create a mapping using item_name and date to match records
                        raw_records_dict = {}
                        for i, record in enumerate(raw_records):
                            key = f"{record.get('item_name', '')}_{record.get('date', '')}"
                            raw_records_dict[key] = record
                        
                        # Reorder raw_records to match sorted dataframe
                        new_raw_records = []
                        for _, row in data_df.iterrows():
                            key = f"{row.get('item_name', '')}_{row.get('date', '')}"
                            if key in raw_records_dict:
                                new_raw_records.append(raw_records_dict[key])
                        raw_records = new_raw_records
            
            # Convert DataFrame to list of dictionaries and add MongoDB IDs
            if data_df is not None and not data_df.empty:
                # Create a mapping from display data to MongoDB IDs by matching key fields
                for i, (_, record) in enumerate(data_df.iterrows()):
                    values = self.extract_table_values(record, table_type)
                    
                    # Find matching MongoDB record for this row
                    mongo_id = ''
                    if i < len(raw_records):
                        mongo_id = str(raw_records[i].get('_id', ''))
                    else:
                        # Fallback: try to match by key field
                        key_field = self.get_key_field_for_table(table_type)
                        if key_field and values:
                            key_value = values[0]  # First column is usually the key
                            for raw_record in raw_records:
                                if str(raw_record.get(key_field, '')) == str(key_value):
                                    mongo_id = str(raw_record.get('_id', ''))
                                    break
                    
                    # Store the MongoDB document ID as item data using tags
                    item_id = tree.insert("", "end", values=values, tags=(mongo_id,) if mongo_id else ('',))
                
        except Exception as e:
            print(f"Error refreshing attendance table: {e}")
            logger.error(f"Error refreshing {table_type} table: {e}")
    
    def get_key_field_for_table(self, table_type):
        """Get the key field name for matching records"""
        key_mapping = {
            "employees": "employee_id",
            "attendance": "employee_id", 
            "sales": "item_name",
            "purchases": "item_name",
            "stock": "item_name"
        }
        return key_mapping.get(table_type, "name")
    
    def extract_table_values(self, record, table_type):
        """Extract values for table display"""
        if table_type == "employees":
            # Format join_date to dd/mm/yy
            join_date = record.get("join_date", "")
            if pd.isna(join_date) or join_date == "":
                # Fallback to hire_date if join_date is missing
                hire_date = record.get("hire_date", "")
                if hasattr(hire_date, 'strftime'):
                    join_date = hire_date.strftime('%d/%m/%y')
                else:
                    join_date = "Not Set"
            elif hasattr(join_date, 'strftime'):
                join_date = join_date.strftime('%d/%m/%y')
            else:
                join_date = "Not Set"
            
            # Format last_paid to dd/mm/yy
            last_paid = record.get("last_paid", "")
            if pd.isna(last_paid) or 'NaT' in str(type(last_paid)):
                last_paid_str = "Never Paid"
            elif hasattr(last_paid, 'strftime'):
                last_paid_str = last_paid.strftime('%d/%m/%y')
            else:
                last_paid_str = str(last_paid)
            
            return [
                record.get("employee_id", ""),
                record.get("name", ""),
                record.get("aadhar_no", ""),
                record.get("phone", ""),
                record.get("department", ""),
                record.get("position", ""),
                f"₹{record.get('daily_wage', 0):,.2f}",
                join_date,
                last_paid_str
            ]
        elif table_type == "attendance":
            # Format date to dd/mm/yy
            date_str = record.get("date", "")
            if hasattr(date_str, 'strftime'):
                date_str = date_str.strftime('%d/%m/%y')
            elif isinstance(date_str, str) and len(date_str) > 10:
                # Handle datetime string format
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%d/%m/%y')
                except:
                    pass
            
            # Format time_in and time_out to 12-hour format with AM/PM
            time_in = record.get("time_in", "")
            time_out = record.get("time_out", "")
            
            # Convert time_in to 12-hour format
            if time_in:
                try:
                    if isinstance(time_in, str) and ':' in time_in:
                        time_obj = datetime.strptime(time_in, "%H:%M")
                        time_in = time_obj.strftime('%I:%M %p')
                except:
                    pass
            
            # Convert time_out to 12-hour format  
            if time_out:
                try:
                    if isinstance(time_out, str) and ':' in time_out:
                        time_obj = datetime.strptime(time_out, "%H:%M")
                        time_out = time_obj.strftime('%I:%M %p')
                except:
                    pass
            
            hours = self.calculate_hours(record.get("time_in"), record.get("time_out"))
            exception_hours = record.get("exception_hours", 1)  # Default to 1 if not set
            
            # Ensure hours is a float
            try:
                hours_float = float(hours) if hours is not None else 0.0
            except (ValueError, TypeError):
                hours_float = 0.0
            
            # Ensure exception_hours is a float
            try:
                exception_hours_float = float(exception_hours) if exception_hours is not None else 1.0
            except (ValueError, TypeError):
                exception_hours_float = 1.0
            
            return [
                record.get("employee_id", ""),
                date_str,
                time_in,
                time_out,
                record.get("status", ""),
                f"{hours_float:.1f}h",
                f"{exception_hours_float:.1f}h"
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
            # Format date to dd/mm/yy format
            date_str = record.get("date", "")
            if hasattr(date_str, 'strftime'):
                date_str = date_str.strftime('%d/%m/%y')
            elif isinstance(date_str, str) and len(date_str) > 10:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%d/%m/%y')
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
                    var_dict["aadhar_no"].set(values[2])     # Aadhar No (not email)
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
            
            # Prepare update data with proper field mapping
            update_data = {}
            for k, v in data.items():
                if k == "price_per_unit":
                    update_data["unit_price"] = float(v) if v else 0.0
                else:
                    update_data[k] = v
            
            # Convert numeric fields
            if update_data.get("quantity"):
                update_data["quantity"] = int(update_data["quantity"])
            
            # Calculate total
            if update_data.get("quantity") and update_data.get("unit_price"):
                update_data["total_price"] = update_data["quantity"] * update_data["unit_price"]
            
            # Convert date from dd/mm/yy format
            if update_data.get("date"):
                date_str = update_data["date"]
                try:
                    # Handle dd/mm/yy format
                    if "/" in date_str and len(date_str.split("/")) == 3:
                        day, month, year = date_str.split("/")
                        # Handle 2-digit year (convert to 4-digit)
                        if len(year) == 2:
                            year = "20" + year if int(year) < 50 else "19" + year
                        # Create datetime object
                        update_data["date"] = datetime(int(year), int(month), int(day))
                    else:
                        # Fallback: try to parse as is
                        update_data["date"] = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError as e:
                    self.show_status_message("Please enter date in dd/mm/yy format", "error")
                    return
            
            # Update purchase record using MongoDB ID
            result = self.data_service.update_purchase(self.editing_purchase_id, update_data)
            
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
