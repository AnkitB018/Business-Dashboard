"""
Enhanced Reports and Analytics GUI Page with Calendar and Better Visualizations
Modern interface with attendance calendar and meaningful charts
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import calendar
import logging

logger = logging.getLogger(__name__)

class ModernReportsPageGUI:
    def __init__(self, parent, data_service):
        self.parent = parent
        self.data_service = data_service
        self.frame = None
        self.selected_employee = None
        
        # Calendar navigation variables
        today = datetime.now()
        self.selected_year = today.year
        self.selected_month = today.month
        
        # Modern color scheme
        self.colors = {
            'primary': '#3B82F6',      # Blue
            'success': '#10B981',      # Green  
            'warning': '#F59E0B',      # Orange
            'danger': '#EF4444',       # Red
            'info': '#06B6D4',         # Cyan
            'purple': '#8B5CF6',       # Purple
            'light': '#F8FAFC',        # Light gray
            'dark': '#1E293B',         # Dark gray
        }
        
        # Attendance color mapping - Simplified color scheme
        self.attendance_colors = {
            'Present': '#10B981',      # Green
            'Absent': '#EF4444',       # Red  
            'Leave': '#F59E0B',        # Yellow/Orange
            'Overtime': '#065F46',     # Dark Green
            'Future': '#FFFFFF',       # White for future dates
            'No Data': '#D1D5DB'       # Light Gray for no data
        }
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8')
        
        self.create_page()
        
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
        
    def create_page(self):
        """Create the enhanced reports page"""
        # Main frame with modern styling
        self.frame = ctk.CTkFrame(self.parent, corner_radius=0, fg_color="transparent")
        
        # Create header
        self.create_header()
        
        # Create tabbed interface with enhanced functionality
        self.create_enhanced_tab_view()
        
        # Create status bar at bottom
        self.create_status_bar()
        
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
            text="📊 Advanced Reports & Analytics",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Comprehensive insights with interactive calendars and detailed analytics",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(anchor="w")
        
        # Quick action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right", fill="y", padx=20, pady=15)
        
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh All",
            command=self.refresh_all_reports,
            width=120,
            height=50,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        refresh_btn.pack()
        
    def create_enhanced_tab_view(self):
        """Create enhanced tabbed interface"""
        # Tab view container
        tab_container = ctk.CTkFrame(self.frame, corner_radius=10)
        tab_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create tab view
        self.tabview = ctk.CTkTabview(tab_container, corner_radius=8)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Bind tab change events manually since command parameter might not be supported
        def on_tab_select(event=None):
            self.on_tab_changed()
        
        # Use after_idle to check for tab changes
        self.last_tab = None
        self.parent.after(100, self.check_tab_changes)
        
        # Add tabs
        self.tabview.add("📅 Attendance Calendar")
        self.tabview.add("� Wage Reports")
        self.tabview.add("🎁 Bonus Analysis")
        self.tabview.add("�👥 Employee Analytics") 
        self.tabview.add("💰 Financial Reports")
        
        # Create tab content
        self.create_attendance_tab()
        self.create_wage_reports_tab()
        self.create_bonus_analysis_tab()
        self.create_employee_tab()
        self.create_financial_tab()
        
        # Set default tab
        self.tabview.set("📅 Attendance Calendar")
        
    def create_attendance_tab(self):
        """Create enhanced attendance tab with calendar"""
        tab_frame = self.tabview.tab("📅 Attendance Calendar")
        
        # Create main container with scrollable frame
        main_container = ctk.CTkScrollableFrame(tab_frame, corner_radius=8)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure improved scroll speed
        self.configure_scroll_speed(main_container)
        
        # Generate Attendance Report button at the top
        generate_btn = ctk.CTkButton(
            main_container,
            text="📅 Generate Attendance Report",
            command=self.generate_attendance_reports,
            height=50,
            width=300,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary'])
        )
        generate_btn.pack(pady=(10, 20))
        
        # Employee selection section
        selection_frame = ctk.CTkFrame(main_container, height=100, corner_radius=8)
        selection_frame.pack(fill="x", padx=10, pady=(10, 20))
        selection_frame.pack_propagate(False)
        
        # Employee dropdown
        ctk.CTkLabel(
            selection_frame,
            text="Select Employee:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=20, pady=30)
        
        self.employee_var = ctk.StringVar()
        self.employee_dropdown = ctk.CTkComboBox(
            selection_frame,
            values=self.get_employee_list(),
            variable=self.employee_var,
            command=self.on_employee_selected,
            width=300,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.employee_dropdown.pack(side="left", padx=20, pady=30)
        
        # Month and Year selection section
        date_selection_frame = ctk.CTkFrame(main_container, height=100, corner_radius=8)
        date_selection_frame.pack(fill="x", padx=10, pady=(0, 20))
        date_selection_frame.pack_propagate(False)
        
        # Month selector
        ctk.CTkLabel(
            date_selection_frame,
            text="Month:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=(20, 10), pady=30)
        
        self.month_var = ctk.StringVar(value=calendar.month_name[self.selected_month])
        self.month_dropdown = ctk.CTkComboBox(
            date_selection_frame,
            values=[calendar.month_name[i] for i in range(1, 13)],
            variable=self.month_var,
            command=self.on_month_selected,
            width=150,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.month_dropdown.pack(side="left", padx=10, pady=30)
        
        # Year selector
        ctk.CTkLabel(
            date_selection_frame,
            text="Year:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=(20, 10), pady=30)
        
        current_year = datetime.now().year
        year_list = [str(year) for year in range(current_year - 5, current_year + 2)]
        self.year_var = ctk.StringVar(value=str(self.selected_year))
        self.year_dropdown = ctk.CTkComboBox(
            date_selection_frame,
            values=year_list,
            variable=self.year_var,
            command=self.on_year_selected,
            width=100,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.year_dropdown.pack(side="left", padx=10, pady=30)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            date_selection_frame,
            text="🔄 Refresh Calendar",
            command=self.refresh_calendar,
            height=40,
            width=150,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary'])
        )
        refresh_btn.pack(side="left", padx=20, pady=30)
        
        # Calendar and statistics container
        content_frame = ctk.CTkFrame(main_container, corner_radius=8)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Calendar
        self.calendar_frame = ctk.CTkFrame(content_frame, corner_radius=8)
        self.calendar_frame.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=20)
        
        # Right side - Statistics and Legend
        self.stats_frame = ctk.CTkFrame(content_frame, width=350, corner_radius=8)
        self.stats_frame.pack(side="right", fill="y", padx=(10, 20), pady=20)
        self.stats_frame.pack_propagate(False)
        
        # Create initial calendar
        self.create_attendance_calendar()
        self.create_attendance_legend()
        self.create_attendance_stats()
        
    def create_wage_reports_tab(self):
        """Create wage reports tab for employee wage calculations"""
        tab_frame = self.tabview.tab("� Wage Reports")
        
        # Create scrollable container
        container = ctk.CTkScrollableFrame(tab_frame, corner_radius=8)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure improved scroll speed
        self.configure_scroll_speed(container)
        
        # Header section
        header_frame = ctk.CTkFrame(container, height=80, corner_radius=8)
        header_frame.pack(fill="x", padx=10, pady=(10, 20))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="💰 Employee Wage Calculator",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['success']
        )
        title_label.pack(side="left", padx=20, pady=25)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh Data",
            command=self.refresh_wage_data,
            height=40,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary'])
        )
        refresh_btn.pack(side="right", padx=20, pady=20)
        
        # Employee selection section
        selection_frame = ctk.CTkFrame(container, corner_radius=8)
        selection_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        # Employee dropdown
        dropdown_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        dropdown_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            dropdown_frame,
            text="Select Employee:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['dark']
        ).pack(side="left", padx=(0, 20))
        
        self.wage_employee_var = ctk.StringVar()
        self.wage_employee_dropdown = ctk.CTkComboBox(
            dropdown_frame,
            variable=self.wage_employee_var,
            values=self.get_employee_list_for_wage(),
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.on_wage_employee_select
        )
        self.wage_employee_dropdown.pack(side="left", padx=(0, 20))
        
        # Calculate button
        calculate_btn = ctk.CTkButton(
            dropdown_frame,
            text="📊 Calculate Wages",
            command=self.calculate_employee_wages,
            height=40,
            width=180,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            hover_color=self.darken_color(self.colors['success'])
        )
        calculate_btn.pack(side="left")
        
        # Results display section
        self.wage_results_frame = ctk.CTkFrame(container, corner_radius=8)
        self.wage_results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Initial empty state
        self.create_wage_empty_state()
        
    def get_employee_list_for_wage(self):
        """Get list of employees for wage dropdown"""
        try:
            employees_df = self.data_service.get_employees()
            if employees_df.empty:
                return ["No employees found"]
            
            employee_list = []
            for _, emp in employees_df.iterrows():
                emp_id = emp.get('employee_id', 'Unknown')
                name = emp.get('name', 'Unknown')
                employee_list.append(f"{emp_id} - {name}")
            
            return employee_list
        except Exception as e:
            logger.error(f"Error getting employee list for wages: {e}")
            return ["Error loading employees"]
    
    def on_wage_employee_select(self, selection):
        """Handle employee selection in wage dropdown"""
        if selection and selection != "No employees found" and selection != "Error loading employees":
            # Automatically calculate wages when employee is selected
            self.calculate_employee_wages()
    
    def refresh_wage_data(self):
        """Refresh employee dropdown and clear results"""
        try:
            # Update dropdown values
            new_values = self.get_employee_list_for_wage()
            self.wage_employee_dropdown.configure(values=new_values)
            
            # Clear selection
            self.wage_employee_var.set("")
            
            # Show empty state
            self.create_wage_empty_state()
            
        except Exception as e:
            logger.error(f"Error refreshing wage data: {e}")
    
    def create_wage_empty_state(self):
        """Create empty state for wage results"""
        # Clear existing widgets
        for widget in self.wage_results_frame.winfo_children():
            widget.destroy()
        
        # Empty state message
        empty_frame = ctk.CTkFrame(self.wage_results_frame, fg_color="transparent")
        empty_frame.pack(expand=True, fill="both")
        
        ctk.CTkLabel(
            empty_frame,
            text="💼 Select an employee to calculate wages",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['gray_light'] if hasattr(self, 'colors') and 'gray_light' in self.colors else "#9CA3AF"
        ).pack(expand=True, pady=50)
    
    def calculate_employee_wages(self):
        """Calculate and display wages for selected employee"""
        try:
            # Get selected employee
            selection = self.wage_employee_var.get()
            if not selection or selection in ["No employees found", "Error loading employees", ""]:
                messagebox.showwarning("Selection Required", "Please select an employee first.")
                return
            
            # Extract employee ID
            emp_id = selection.split(" - ")[0].strip()
            
            # Get employee data
            employees_df = self.data_service.get_employees({"employee_id": emp_id})
            if employees_df.empty:
                messagebox.showerror("Error", "Employee not found.")
                return
            
            employee = employees_df.iloc[0]
            daily_wage = float(employee.get('daily_wage', 0))
            last_paid = employee.get('last_paid')
            
            if daily_wage <= 0:
                messagebox.showerror("Error", "Employee daily wage not set or invalid.")
                return
            
            # Calculate wage period: Always from (last_paid + 1 day) to today
            from datetime import datetime, date, timedelta
            
            # Get last_paid date (should always exist, defaulting to hire_date)
            last_paid = employee.get('last_paid')
            if not last_paid:
                # Fallback to hire_date if last_paid is missing
                hire_date = employee.get('hire_date')
                if hire_date:
                    last_paid = hire_date
                else:
                    # Ultimate fallback (shouldn't happen)
                    last_paid = date.today() - timedelta(days=30)
            
            # Handle different date formats for last_paid
            if isinstance(last_paid, str):
                try:
                    last_paid_date = datetime.strptime(last_paid, "%Y-%m-%d").date()
                except ValueError:
                    # Try ISO format
                    last_paid_date = datetime.fromisoformat(last_paid.replace('Z', '')).date()
            elif hasattr(last_paid, 'date'):
                last_paid_date = last_paid.date()
            else:
                last_paid_date = last_paid
            
            # Calculate from day after last_paid to today
            start_date = last_paid_date + timedelta(days=1)
            end_date = date.today()
            
            # If start_date is in the future (last_paid is today), show ₹0.0
            if start_date > end_date:
                start_date = end_date  # This will result in 0 days
            
            end_date = date.today()
            
            # Debug: Print date range
            print(f"Calculating wages for {emp_id} from {start_date} to {end_date}")
            
            # Get attendance data for the period
            # Convert dates to datetime for MongoDB query
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Get all attendance records for this employee
            all_attendance_df = self.data_service.get_attendance({"employee_id": emp_id})
            
            # Filter by date range in Python since MongoDB query might be complex
            attendance_df = pd.DataFrame()
            if not all_attendance_df.empty:
                # Convert date column to datetime for comparison
                all_attendance_df['date_converted'] = pd.to_datetime(all_attendance_df['date'])
                mask = (all_attendance_df['date_converted'] >= start_datetime) & (all_attendance_df['date_converted'] <= end_datetime)
                attendance_df = all_attendance_df[mask]
            
            print(f"Found {len(attendance_df)} attendance records in date range")
            
            # Use new wage calculation system
            from new_wage_calculator import NewWageCalculator
            
            calculator = NewWageCalculator(self.data_service)
            result = calculator.calculate_employee_wage_new_system(employee.to_dict())
            
            if 'error' in result:
                messagebox.showerror("Calculation Error", result['error'])
                return
            
            print(f"New system - Total wage calculated: ₹{result['total_wage']}")
            
            # Display results using new system data
            self.display_wage_results_new_system(result)
            
        except Exception as e:
            logger.error(f"Error calculating wages: {e}")
            print(f"Error calculating wages: {e}")
            messagebox.showerror("Error", f"Failed to calculate wages: {str(e)}")
    
    
    def display_wage_results_new_system(self, result):
        """Display calculated wage results using new system data"""
        # Clear existing widgets
        for widget in self.wage_results_frame.winfo_children():
            widget.destroy()
        
        # Main results container
        results_container = ctk.CTkFrame(self.wage_results_frame, fg_color="transparent")
        results_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Employee info header
        info_frame = ctk.CTkFrame(results_container, corner_radius=8, fg_color=self.colors['light'])
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_content = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_content.pack(fill="x", padx=20, pady=15)
        
        # Employee name and ID
        emp_label = ctk.CTkLabel(
            info_content,
            text=f"👤 {result.get('employee_name', 'Unknown')} (ID: {result.get('employee_id', 'Unknown')})",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['dark']
        )
        emp_label.pack(side="left")
        
        # Daily wage info
        wage_label = ctk.CTkLabel(
            info_content,
            text=f"💰 Daily Wage: ₹{result.get('daily_wage', 0):,.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['success']
        )
        wage_label.pack(side="right")
        
        # Period info
        period_frame = ctk.CTkFrame(results_container, corner_radius=8, fg_color=self.colors['info'])
        period_frame.pack(fill="x", pady=(0, 20))
        
        start_date = result.get('period_start')
        end_date = result.get('period_end')
        period_label = ctk.CTkLabel(
            period_frame,
            text=f"📅 Calculation Period: {start_date} to {end_date}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        period_label.pack(pady=15)
        
        # Results grid
        results_grid = ctk.CTkFrame(results_container, corner_radius=8)
        results_grid.pack(fill="x", pady=(0, 20))
        
        # Configure grid
        results_grid.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Headers
        headers = ["Work Days", "Total Hours", "Overtime Hours", "Exception Hours", "Effective Hours"]
        values = [
            str(result.get('work_days', 0)),
            f"{result.get('total_hours_worked', 0):.1f}h",
            f"{result.get('total_overtime_hours', 0):.1f}h",
            f"{result.get('total_exception_hours', 0):.1f}h", 
            f"{result.get('effective_hours', 0):.1f}h"
        ]
        
        for i, (header, value) in enumerate(zip(headers, values)):
            # Header
            header_label = ctk.CTkLabel(
                results_grid,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['dark']
            )
            header_label.grid(row=0, column=i, padx=10, pady=(15, 5), sticky="ew")
            
            # Value
            value_label = ctk.CTkLabel(
                results_grid,
                text=value,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors['dark']
            )
            value_label.grid(row=1, column=i, padx=10, pady=(0, 15), sticky="ew")
        
        # Total wage display
        total_frame = ctk.CTkFrame(results_container, corner_radius=8, fg_color=self.colors['success'])
        total_frame.pack(fill="x", pady=(0, 20))
        
        total_label = ctk.CTkLabel(
            total_frame,
            text=f"💰 Total Wage Payable: ₹{result.get('total_wage', 0):,.2f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        total_label.pack(pady=20)
        
        # Calculation breakdown
        breakdown_frame = ctk.CTkFrame(results_container, corner_radius=8)
        breakdown_frame.pack(fill="x", pady=(0, 20))
        
        breakdown_title = ctk.CTkLabel(
            breakdown_frame,
            text="📊 Calculation Breakdown (New System)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['dark']
        )
        breakdown_title.pack(pady=(15, 10))
        
        # Calculation details
        hourly_rate = result.get('hourly_rate', 0)
        effective_hours = result.get('effective_hours', 0)
        total_wage = result.get('total_wage', 0)
        
        breakdown_text = ctk.CTkLabel(
            breakdown_frame,
            text=f"""🔹 Effective Working Hours: {effective_hours:.1f} hours
🔹 Hourly Rate: ₹{hourly_rate:.2f}/hour (Daily Wage ÷ 8)
🔹 Formula: {effective_hours:.1f} × ₹{hourly_rate:.2f} = ₹{total_wage:,.2f}
🔹 Exception Hours: Time when employee is not actively working""",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['dark'],
            justify="left"
        )
        breakdown_text.pack(pady=(0, 15), padx=20)
        
        # Action buttons
        button_frame = ctk.CTkFrame(results_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        # Export button
        export_btn = ctk.CTkButton(
            button_frame,
            text="📄 Export Report",
            command=lambda: self.export_wage_report_new_system(result),
            height=40,
            width=200,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary'])
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        # Mark as paid button
        mark_paid_btn = ctk.CTkButton(
            button_frame,
            text="✅ Mark as Paid",
            command=lambda: self.mark_employee_as_paid_new_system(result),
            height=40,
            width=200,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors['success'],
            hover_color=self.darken_color(self.colors['success'])
        )
        mark_paid_btn.pack(side="left", padx=10)
    
    def display_wage_results(self, employee, present_days, overtime_hours, total_wage, start_date, end_date):
        """Display calculated wage results"""
        # Clear existing widgets
        for widget in self.wage_results_frame.winfo_children():
            widget.destroy()
        
        # Main results container
        results_container = ctk.CTkFrame(self.wage_results_frame, fg_color="transparent")
        results_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Employee info header
        info_frame = ctk.CTkFrame(results_container, corner_radius=8, fg_color=self.colors['light'])
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_content = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_content.pack(fill="x", padx=20, pady=15)
        
        # Employee name and ID
        emp_label = ctk.CTkLabel(
            info_content,
            text=f"👤 {employee.get('name', 'Unknown')} (ID: {employee.get('employee_id', 'Unknown')})",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['dark']
        )
        emp_label.pack(side="left")
        
        # Daily wage info
        wage_label = ctk.CTkLabel(
            info_content,
            text=f"💰 Daily Wage: ₹{employee.get('daily_wage', 0):,.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['success']
        )
        wage_label.pack(side="right")
        
        # Period info
        period_frame = ctk.CTkFrame(results_container, corner_radius=8, fg_color=self.colors['info'])
        period_frame.pack(fill="x", pady=(0, 20))
        
        period_label = ctk.CTkLabel(
            period_frame,
            text=f"📅 Calculation Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        period_label.pack(pady=15)
        
        # Results grid
        results_grid = ctk.CTkFrame(results_container, corner_radius=8)
        results_grid.pack(fill="x", pady=(0, 20))
        
        # Configure grid
        results_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Present days card
        present_card = ctk.CTkFrame(results_grid, corner_radius=8, fg_color=self.colors['success'])
        present_card.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        ctk.CTkLabel(
            present_card,
            text="📊 Present Days",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            present_card,
            text=str(present_days),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=(0, 15))
        
        # Overtime hours card
        overtime_card = ctk.CTkFrame(results_grid, corner_radius=8, fg_color=self.colors['warning'])
        overtime_card.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        ctk.CTkLabel(
            overtime_card,
            text="⏰ Overtime Hours",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            overtime_card,
            text=str(overtime_hours),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=(0, 15))
        
        # Total wage card
        wage_card = ctk.CTkFrame(results_grid, corner_radius=8, fg_color=self.colors['primary'])
        wage_card.grid(row=0, column=2, padx=10, pady=15, sticky="ew")
        
        ctk.CTkLabel(
            wage_card,
            text="💰 Total Wage",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            wage_card,
            text=f"₹{total_wage:,.2f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=(0, 15))
        
        # Calculation breakdown
        breakdown_frame = ctk.CTkFrame(results_container, corner_radius=8)
        breakdown_frame.pack(fill="x", pady=(0, 20))
        
        breakdown_label = ctk.CTkLabel(
            breakdown_frame,
            text="📋 Calculation Breakdown:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['dark']
        )
        breakdown_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Breakdown details
        daily_amount = present_days * employee.get('daily_wage', 0)
        overtime_amount = (employee.get('daily_wage', 0) / 8) * overtime_hours
        
        breakdown_text = f"""
        🔹 Present Days: {present_days} × ₹{employee.get('daily_wage', 0):,.2f} = ₹{daily_amount:,.2f}
        🔹 Overtime: {overtime_hours} hours × ₹{employee.get('daily_wage', 0)/8:,.2f}/hour = ₹{overtime_amount:,.2f}
        🔹 Total Wage = ₹{daily_amount:,.2f} + ₹{overtime_amount:,.2f} = ₹{total_wage:,.2f}
        """
        
        breakdown_details = ctk.CTkLabel(
            breakdown_frame,
            text=breakdown_text.strip(),
            font=ctk.CTkFont(size=12),
            text_color=self.colors['dark'],
            justify="left"
        )
        breakdown_details.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Action buttons
        action_frame = ctk.CTkFrame(results_container, fg_color="transparent")
        action_frame.pack(fill="x")
        
        # Paid button
        paid_btn = ctk.CTkButton(
            action_frame,
            text="✅ Mark as Paid",
            command=lambda: self.mark_as_paid(employee.get('employee_id'), end_date, total_wage),
            height=50,
            width=200,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors['success'],
            hover_color=self.darken_color(self.colors['success'])
        )
        paid_btn.pack(side="left", padx=(0, 20))
        
        # Export button (future feature)
        export_btn = ctk.CTkButton(
            action_frame,
            text="📄 Export Report",
            command=lambda: self.export_wage_report(employee, present_days, overtime_hours, total_wage),
            height=50,
            width=180,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors['info'],
            hover_color=self.darken_color(self.colors['info'])
        )
        export_btn.pack(side="left")
    
    def mark_as_paid(self, employee_id, paid_date, amount):
        """Mark employee as paid and reset wage calculation"""
        try:
            from tkinter import messagebox
            from datetime import datetime, date
            
            logger.info(f"Attempting to mark employee {employee_id} as paid ₹{amount}")
            logger.info(f"Paid date type: {type(paid_date)}, value: {paid_date}")
            
            # Confirm action
            result = messagebox.askyesno(
                "Confirm Payment", 
                f"Mark employee {employee_id} as paid ₹{amount:,.2f}?\n\nThis will reset the wage calculation and update the last paid date to {paid_date}."
            )
            
            if not result:
                logger.info("Payment marking cancelled by user")
                return
            
            # Convert paid_date to datetime if it's a date object
            if isinstance(paid_date, date) and not isinstance(paid_date, datetime):
                paid_date = datetime.combine(paid_date, datetime.min.time())
            elif isinstance(paid_date, str):
                paid_date = datetime.strptime(paid_date, "%Y-%m-%d")
                
            logger.info(f"Converted paid_date to: {paid_date} (type: {type(paid_date)})")
            
            # Update employee's last_paid date
            update_data = {
                "last_paid": paid_date
            }
            
            logger.info(f"Attempting database update with filter: {{'employee_id': '{employee_id}'}}")
            logger.info(f"Update data: {update_data}")
            
            updated = self.data_service.db_manager.update_document(
                "employees",
                {"employee_id": employee_id},
                {"$set": update_data}
            )
            
            logger.info(f"Database update result: {updated}")
            
            if updated > 0:
                logger.info(f"Successfully marked employee {employee_id} as paid")
                messagebox.showinfo("Success", f"Employee {employee_id} marked as paid successfully!")
                # Refresh the wage calculation
                self.calculate_employee_wages()
            else:
                logger.error(f"Database update returned 0 for employee {employee_id}")
                messagebox.showerror("Error", "Failed to update payment status.")
                
        except Exception as e:
            logger.error(f"Error marking as paid: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed to mark as paid: {str(e)}")
    
    def export_wage_report_new_system(self, result):
        """Export wage report using new system data"""
        try:
            from tkinter import filedialog
            import os
            
            # Get save location
            filename = f"wage_report_{result.get('employee_id', 'unknown')}_{result.get('period_end', 'today')}.txt"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=filename,
                title="Save Wage Report"
            )
            
            if file_path:
                # Create report content
                report_content = f"""
WAGE CALCULATION REPORT (NEW SYSTEM)
====================================

Employee Information:
- Name: {result.get('employee_name', 'Unknown')}
- Employee ID: {result.get('employee_id', 'Unknown')}
- Daily Wage: ₹{result.get('daily_wage', 0):,.2f}
- Hourly Rate: ₹{result.get('hourly_rate', 0):.2f}

Calculation Period:
- From: {result.get('period_start', 'Unknown')}
- To: {result.get('period_end', 'Unknown')}

Work Summary:
- Total Work Days: {result.get('work_days', 0)}
- Total Hours Worked: {result.get('total_hours_worked', 0):.1f} hours
- Total Overtime Hours: {result.get('total_overtime_hours', 0):.1f} hours
- Total Exception Hours: {result.get('total_exception_hours', 0):.1f} hours
- Effective Working Hours: {result.get('effective_hours', 0):.1f} hours

Calculation Formula (New System):
Wage = (Total Hours Worked - Exception Hours) × (Daily Wage ÷ 8)
Wage = ({result.get('total_hours_worked', 0):.1f} - {result.get('total_exception_hours', 0):.1f}) × ₹{result.get('hourly_rate', 0):.2f}
Wage = {result.get('effective_hours', 0):.1f} × ₹{result.get('hourly_rate', 0):.2f}

TOTAL WAGE PAYABLE: ₹{result.get('total_wage', 0):,.2f}

Note: Exception hours represent time when employee is not actively working
(breaks, meetings, training, etc.) and are deducted from total hours.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                # Show success message
                messagebox.showinfo("Export Successful", f"Wage report exported to:\n{file_path}")
                
                # Optionally open the file
                if messagebox.askyesno("Open File", "Would you like to open the exported report?"):
                    try:
                        os.startfile(file_path)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Error exporting wage report: {e}")
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
    
    def mark_employee_as_paid_new_system(self, result):
        """Mark employee as paid and update last_paid date"""
        try:
            emp_id = result.get('employee_id')
            total_wage = result.get('total_wage', 0)
            
            if not emp_id:
                messagebox.showerror("Error", "Employee ID not found")
                return
            
            # Confirm action
            confirm_msg = f"""Mark as Paid?

Employee: {result.get('employee_name', 'Unknown')}
Amount: ₹{total_wage:,.2f}
Period: {result.get('period_start')} to {result.get('period_end')}

This will update the last paid date to today."""
            
            if not messagebox.askyesno("Confirm Payment", confirm_msg):
                return
            
            # Update last_paid date to today
            from datetime import datetime
            today = datetime.now()
            
            updated_count = self.data_service.update_employee(emp_id, {"last_paid": today})
            
            if updated_count > 0:
                messagebox.showinfo("Success", f"Employee {emp_id} marked as paid.\nLast paid date updated to {today}")
                # Refresh the calculation to show ₹0 for new period
                self.calculate_employee_wages()
            else:
                messagebox.showerror("Error", "Failed to update employee payment status")
                
        except Exception as e:
            logger.error(f"Error marking employee as paid: {e}")
            messagebox.showerror("Error", f"Failed to mark as paid: {str(e)}")

    def export_wage_report(self, employee, present_days, overtime_hours, total_wage):
        """Export wage report (placeholder for future implementation)"""
        messagebox.showinfo("Coming Soon", "Export functionality will be available in a future update.")
    
    def create_bonus_analysis_tab(self):
        """Create bonus analysis tab for employee bonus calculations"""
        tab_frame = self.tabview.tab("🎁 Bonus Analysis")
        
        # Create scrollable container
        container = ctk.CTkScrollableFrame(tab_frame, corner_radius=8)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure improved scroll speed
        self.configure_scroll_speed(container)
        
        # Header section
        header_frame = ctk.CTkFrame(container, height=80, corner_radius=8)
        header_frame.pack(fill="x", padx=10, pady=(10, 20))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎁 Employee Bonus Calculator",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['purple']
        )
        title_label.pack(side="left", padx=20, pady=25)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh Data",
            command=self.refresh_bonus_data,
            height=40,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary'])
        )
        refresh_btn.pack(side="right", padx=20, pady=20)
        
        # Bonus rate configuration section
        rate_frame = ctk.CTkFrame(container, corner_radius=8)
        rate_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        rate_content = ctk.CTkFrame(rate_frame, fg_color="transparent")
        rate_content.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            rate_content,
            text="Bonus Rate Configuration:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['dark']
        ).pack(side="left", padx=(0, 20))
        
        self.bonus_rate_var = ctk.StringVar(value="8.33")
        bonus_rate_entry = ctk.CTkEntry(
            rate_content,
            textvariable=self.bonus_rate_var,
            width=100,
            height=35,
            font=ctk.CTkFont(size=14),
            placeholder_text="8.33"
        )
        bonus_rate_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            rate_content,
            text="% (Default: 8.33%)",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['dark']
        ).pack(side="left")
        
        # Date setting section for last bonus paid
        date_frame = ctk.CTkFrame(container, corner_radius=8)
        date_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        date_content = ctk.CTkFrame(date_frame, fg_color="transparent")
        date_content.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            date_content,
            text="Set Last Bonus Paid Date:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['dark']
        ).pack(side="left", padx=(0, 20))
        
        self.last_bonus_date_var = ctk.StringVar(value="")
        self.last_bonus_date_entry = ctk.CTkEntry(
            date_content,
            textvariable=self.last_bonus_date_var,
            width=150,
            height=35,
            font=ctk.CTkFont(size=14),
            placeholder_text="YYYY-MM-DD"
        )
        self.last_bonus_date_entry.pack(side="left", padx=(0, 10))
        
        update_date_btn = ctk.CTkButton(
            date_content,
            text="Update Date",
            command=self.update_last_bonus_date,
            height=35,
            width=120,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['primary'],
            hover_color=self.darken_color(self.colors['primary'])
        )
        update_date_btn.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            date_content,
            text="(Optional: Override calculation start date)",
            font=ctk.CTkFont(size=12),
            text_color="#9CA3AF"
        ).pack(side="left")
        
        # Employee selection section
        selection_frame = ctk.CTkFrame(container, corner_radius=8)
        selection_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        # Employee dropdown
        dropdown_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        dropdown_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            dropdown_frame,
            text="Select Employee:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['dark']
        ).pack(side="left", padx=(0, 20))
        
        self.bonus_employee_var = ctk.StringVar()
        self.bonus_employee_dropdown = ctk.CTkComboBox(
            dropdown_frame,
            variable=self.bonus_employee_var,
            values=self.get_employee_list_for_bonus(),
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.on_bonus_employee_select
        )
        self.bonus_employee_dropdown.pack(side="left", padx=(0, 20))
        
        # Calculate button
        calculate_btn = ctk.CTkButton(
            dropdown_frame,
            text="🎁 Calculate Bonus",
            command=self.calculate_employee_bonus,
            height=40,
            width=180,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['purple'],
            hover_color=self.darken_color(self.colors['purple'])
        )
        calculate_btn.pack(side="left")
        
        # Results display section
        self.bonus_results_frame = ctk.CTkFrame(container, corner_radius=8)
        self.bonus_results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Initial empty state
        self.create_bonus_empty_state()
    
    def get_employee_list_for_bonus(self):
        """Get list of employees for bonus dropdown"""
        try:
            # Use regular get_employees method as fallback
            employees_df = self.data_service.get_employees()
            if employees_df.empty:
                return ["No employees found"]
            
            employee_list = []
            for _, emp in employees_df.iterrows():
                emp_id = emp.get('employee_id', 'Unknown')
                name = emp.get('name', 'Unknown')
                employee_list.append(f"{emp_id} - {name}")
            
            return employee_list
        except Exception as e:
            logger.error(f"Error getting employee list for bonus: {e}")
            return ["Error loading employees"]
    
    def on_bonus_employee_select(self, selection):
        """Handle employee selection in bonus dropdown"""
        if selection and selection != "No employees found" and selection != "Error loading employees":
            # Load current last_bonus_paid date for selected employee
            self.load_employee_last_bonus_date()
            # Automatically calculate bonus when employee is selected
            self.calculate_employee_bonus()
    
    def load_employee_last_bonus_date(self):
        """Load the current last_bonus_paid date for the selected employee"""
        try:
            selected = self.bonus_employee_var.get()
            if not selected or selected in ["No employees found", "Error loading employees"]:
                self.last_bonus_date_var.set("")
                return
            
            # Extract employee ID from selection
            emp_id = selected.split(" - ")[0]
            
            # Get employee data
            employees_df = self.data_service.get_employees({"employee_id": emp_id})
            if not employees_df.empty:
                employee = employees_df.iloc[0]
                last_bonus_paid = employee.get('last_bonus_paid', '')
                
                # Format the date for display
                if last_bonus_paid:
                    if hasattr(last_bonus_paid, 'strftime'):
                        formatted_date = last_bonus_paid.strftime('%Y-%m-%d')
                    else:
                        formatted_date = str(last_bonus_paid).split(' ')[0]  # Take date part if datetime string
                    self.last_bonus_date_var.set(formatted_date)
                else:
                    self.last_bonus_date_var.set("")
                    
        except Exception as e:
            logger.error(f"Error loading last bonus date: {e}")
            self.last_bonus_date_var.set("")
    
    def update_last_bonus_date(self):
        """Update the last_bonus_paid date for the selected employee"""
        try:
            selected = self.bonus_employee_var.get()
            if not selected or selected in ["No employees found", "Error loading employees"]:
                messagebox.showwarning("No Selection", "Please select an employee first.")
                return
            
            new_date = self.last_bonus_date_var.get().strip()
            if not new_date:
                messagebox.showwarning("Invalid Date", "Please enter a date in YYYY-MM-DD format.")
                return
            
            # Validate date format
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(new_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
                return
            
            # Extract employee ID from selection
            emp_id = selected.split(" - ")[0]
            
            # Update the employee's last_bonus_paid date
            result = self.data_service.update_employee(emp_id, {
                'last_bonus_paid': new_date
            })
            
            if result > 0:
                messagebox.showinfo("Success", f"Last bonus paid date updated to {new_date} for employee {emp_id}")
                # Refresh the bonus calculation with new date
                self.calculate_employee_bonus()
            else:
                messagebox.showerror("Error", "Failed to update the last bonus paid date.")
                
        except Exception as e:
            logger.error(f"Error updating last bonus date: {e}")
            messagebox.showerror("Error", f"Failed to update date: {str(e)}")
    
    def refresh_bonus_data(self):
        """Refresh employee dropdown and clear results"""
        try:
            # Update dropdown values
            new_values = self.get_employee_list_for_bonus()
            self.bonus_employee_dropdown.configure(values=new_values)
            
            # Clear selection
            self.bonus_employee_var.set("")
            
            # Show empty state
            self.create_bonus_empty_state()
            
        except Exception as e:
            logger.error(f"Error refreshing bonus data: {e}")
    
    def create_bonus_empty_state(self):
        """Create empty state for bonus results"""
        # Clear existing widgets
        for widget in self.bonus_results_frame.winfo_children():
            widget.destroy()
        
        # Empty state message
        empty_frame = ctk.CTkFrame(self.bonus_results_frame, fg_color="transparent")
        empty_frame.pack(expand=True, fill="both")
        
        ctk.CTkLabel(
            empty_frame,
            text="🎁 Select an employee to calculate bonus",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['gray_light'] if hasattr(self, 'colors') and 'gray_light' in self.colors else "#9CA3AF"
        ).pack(expand=True, pady=50)
    
    def calculate_employee_bonus(self):
        """Calculate and display bonus for selected employee"""
        try:
            # Get selected employee
            selection = self.bonus_employee_var.get()
            if not selection or selection in ["No employees found", "Error loading employees", ""]:
                messagebox.showwarning("Selection Required", "Please select an employee first.")
                return
            
            # Extract employee ID
            emp_id = selection.split(" - ")[0].strip()
            
            # Get bonus rate
            try:
                bonus_rate = float(self.bonus_rate_var.get())
                if bonus_rate <= 0 or bonus_rate > 100:
                    messagebox.showerror("Invalid Rate", "Bonus rate must be between 0.01% and 100%.")
                    return
            except ValueError:
                messagebox.showerror("Invalid Rate", "Please enter a valid bonus rate (e.g., 8.33).")
                return
            
            # Calculate bonus using BonusCalculator directly
            try:
                from bonus_calculator import BonusCalculator
                
                # Get employee data
                employees_df = self.data_service.get_employees({"employee_id": emp_id})
                if employees_df.empty:
                    messagebox.showerror("Error", "Employee not found.")
                    return
                
                employee = employees_df.iloc[0].to_dict()
                
                # Calculate bonus using BonusCalculator directly
                calculator = BonusCalculator(self.data_service)
                result = calculator.calculate_employee_bonus(employee, bonus_rate)
                
                if 'error' in result:
                    messagebox.showerror("Calculation Error", result['error'])
                    return
                
                # Display results
                self.display_bonus_results(result)
                
            except ImportError:
                messagebox.showerror("Error", "Bonus calculator module not found.")
                return
            
        except Exception as e:
            logger.error(f"Error calculating bonus: {e}")
            messagebox.showerror("Error", f"Failed to calculate bonus: {str(e)}")
    
    def display_bonus_results(self, result):
        """Display calculated bonus results"""
        # Clear existing widgets
        for widget in self.bonus_results_frame.winfo_children():
            widget.destroy()
        
        # Main results container
        results_container = ctk.CTkFrame(self.bonus_results_frame, fg_color="transparent")
        results_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Employee info header
        info_frame = ctk.CTkFrame(results_container, corner_radius=8, fg_color=self.colors['light'])
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_content = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_content.pack(fill="x", padx=20, pady=15)
        
        # Employee name and ID
        emp_label = ctk.CTkLabel(
            info_content,
            text=f"👤 {result.get('employee_name', 'Unknown')} (ID: {result.get('employee_id', 'Unknown')})",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['dark']
        )
        emp_label.pack(side="left")
        
        # Daily wage info
        wage_label = ctk.CTkLabel(
            info_content,
            text=f"💰 Daily Wage: ₹{result.get('daily_wage', 0):,.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['success']
        )
        wage_label.pack(side="right")
        
        # Period info
        period_frame = ctk.CTkFrame(results_container, corner_radius=8, fg_color=self.colors['info'])
        period_frame.pack(fill="x", pady=(0, 20))
        
        start_date = result.get('period_start')
        end_date = result.get('period_end')
        period_label = ctk.CTkLabel(
            period_frame,
            text=f"📅 Bonus Calculation Period: {start_date} to {end_date}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        period_label.pack(pady=15)
        
        # Time remaining info
        time_frame = ctk.CTkFrame(results_container, corner_radius=8, 
                                 fg_color=self.colors['warning'] if not result.get('is_bonus_due', False) else self.colors['success'])
        time_frame.pack(fill="x", pady=(0, 20))
        
        months = result.get('months_remaining', 0)
        days = result.get('days_remaining', 0)
        
        if result.get('is_bonus_due', False):
            time_text = "🎉 Bonus is Due! (1 year completed)"
        else:
            time_text = f"⏳ Time Remaining: {months} months {days} days until next bonus"
        
        time_label = ctk.CTkLabel(
            time_frame,
            text=time_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        time_label.pack(pady=15)
        
        # Results grid
        results_grid = ctk.CTkFrame(results_container, corner_radius=8)
        results_grid.pack(fill="x", pady=(0, 20))
        
        # Configure grid
        results_grid.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Headers
        headers = ["Work Days", "Total Hours", "Overtime Hours", "Exception Hours", "Effective Hours"]
        values = [
            str(result.get('work_days', 0)),
            f"{result.get('total_hours_worked', 0):.1f}h",
            f"{result.get('total_overtime_hours', 0):.1f}h",
            f"{result.get('total_exception_hours', 0):.1f}h", 
            f"{result.get('effective_hours', 0):.1f}h"
        ]
        
        for i, (header, value) in enumerate(zip(headers, values)):
            # Header
            header_label = ctk.CTkLabel(
                results_grid,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['dark']
            )
            header_label.grid(row=0, column=i, padx=10, pady=(15, 5), sticky="ew")
            
            # Value
            value_label = ctk.CTkLabel(
                results_grid,
                text=value,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors['dark']
            )
            value_label.grid(row=1, column=i, padx=10, pady=(0, 15), sticky="ew")
        
        # Earnings and bonus display
        earnings_frame = ctk.CTkFrame(results_container, corner_radius=8)
        earnings_frame.pack(fill="x", pady=(0, 20))
        
        # Configure grid for earnings
        earnings_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Total earned
        earned_label = ctk.CTkLabel(
            earnings_frame,
            text="Total Earned",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['dark']
        )
        earned_label.grid(row=0, column=0, padx=20, pady=(15, 5))
        
        earned_value = ctk.CTkLabel(
            earnings_frame,
            text=f"₹{result.get('total_earned', 0):,.2f}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['success']
        )
        earned_value.grid(row=1, column=0, padx=20, pady=(0, 15))
        
        # Bonus rate
        rate_label = ctk.CTkLabel(
            earnings_frame,
            text="Bonus Rate",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['dark']
        )
        rate_label.grid(row=0, column=1, padx=20, pady=(15, 5))
        
        rate_value = ctk.CTkLabel(
            earnings_frame,
            text=f"{result.get('bonus_rate', 0):.2f}%",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['info']
        )
        rate_value.grid(row=1, column=1, padx=20, pady=(0, 15))
        
        # Total bonus display
        bonus_frame = ctk.CTkFrame(results_container, corner_radius=8, fg_color=self.colors['purple'])
        bonus_frame.pack(fill="x", pady=(0, 20))
        
        bonus_label = ctk.CTkLabel(
            bonus_frame,
            text=f"🎁 Total Bonus Amount: ₹{result.get('bonus_amount', 0):,.2f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        bonus_label.pack(pady=20)
        
        # Calculation breakdown
        breakdown_frame = ctk.CTkFrame(results_container, corner_radius=8)
        breakdown_frame.pack(fill="x", pady=(0, 20))
        
        breakdown_title = ctk.CTkLabel(
            breakdown_frame,
            text="📊 Bonus Calculation Breakdown",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['dark']
        )
        breakdown_title.pack(pady=(15, 10))
        
        # Calculation details
        total_earned = result.get('total_earned', 0)
        bonus_rate = result.get('bonus_rate', 0)
        bonus_amount = result.get('bonus_amount', 0)
        
        breakdown_text = ctk.CTkLabel(
            breakdown_frame,
            text=f"""🔹 Total Earned: ₹{total_earned:,.2f}
🔹 Bonus Rate: {bonus_rate:.2f}%
🔹 Formula: ₹{total_earned:,.2f} × {bonus_rate:.2f}% = ₹{bonus_amount:,.2f}""",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['dark'],
            justify="left"
        )
        breakdown_text.pack(pady=(0, 15))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(results_container, corner_radius=8)
        actions_frame.pack(fill="x", pady=(0, 10))
        
        actions_content = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_content.pack(fill="x", padx=20, pady=15)
        
        # Bonus paid button
        bonus_paid_btn = ctk.CTkButton(
            actions_content,
            text="✅ Mark Bonus as Paid",
            command=lambda: self.mark_bonus_as_paid(result.get('employee_id')),
            height=40,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['success'],
            hover_color=self.darken_color(self.colors['success'])
        )
        bonus_paid_btn.pack(side="left", padx=(0, 20))
        
        # Export button (placeholder)
        export_btn = ctk.CTkButton(
            actions_content,
            text="📄 Export Report",
            command=lambda: self.export_bonus_report(result),
            height=40,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['info'],
            hover_color=self.darken_color(self.colors['info'])
        )
        export_btn.pack(side="left")
    
    def mark_bonus_as_paid(self, employee_id):
        """Mark bonus as paid for an employee with confirmation"""
        try:
            # Show confirmation dialog
            result = messagebox.askyesno(
                "Confirm Bonus Payment",
                f"Are you sure you want to mark bonus as paid for employee {employee_id}?\n\n"
                "This will reset the bonus calculation and start counting from today.",
                icon="warning"
            )
            
            if result:
                # Mark bonus as paid using direct database update
                try:
                    from datetime import date
                    today = date.today()
                    
                    # Update employee record with last_bonus_paid
                    update_result = self.data_service.update_employee(employee_id, {
                        'last_bonus_paid': today.strftime('%Y-%m-%d')
                    })
                    
                    if update_result > 0:
                        messagebox.showinfo("Success", "Bonus payment has been recorded successfully!")
                        # Refresh the calculation to show updated data
                        self.calculate_employee_bonus()
                    else:
                        messagebox.showerror("Error", "Failed to record bonus payment.")
                        
                except Exception as e:
                    logger.error(f"Error updating bonus payment: {e}")
                    messagebox.showerror("Error", f"Failed to record bonus payment: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error marking bonus as paid: {e}")
            messagebox.showerror("Error", f"Failed to mark bonus as paid: {str(e)}")
    
    def export_bonus_report(self, result):
        """Export bonus report (placeholder for future implementation)"""
        messagebox.showinfo("Coming Soon", "Export functionality will be available in a future update.")
        
    def create_employee_tab(self):
        """Create employee analytics tab"""
        tab_frame = self.tabview.tab("�👥 Employee Analytics")
        
        # Create scrollable container
        container = ctk.CTkScrollableFrame(tab_frame, corner_radius=8)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure improved scroll speed
        self.configure_scroll_speed(container)
        
        # Generate button
        generate_btn = ctk.CTkButton(
            container,
            text="📊 Generate Employee Reports",
            command=self.generate_employee_reports,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        generate_btn.pack(pady=20)
        
        # Charts container
        self.employee_charts_frame = ctk.CTkFrame(container, corner_radius=8)
        self.employee_charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_financial_tab(self):
        """Create enhanced financial reports tab with reorganized controls"""
        tab_frame = self.tabview.tab("💰 Financial Reports")
        
        # Create scrollable container
        container = ctk.CTkScrollableFrame(tab_frame, corner_radius=8)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure improved scroll speed
        self.configure_scroll_speed(container)
        
        # Monthly Summary at the top
        self.monthly_summary_frame = ctk.CTkFrame(container, corner_radius=8)
        self.monthly_summary_frame.pack(fill="x", padx=10, pady=(10, 20))
        
        # Main Generate Report Button
        main_generate_btn = ctk.CTkButton(
            container,
            text="🔄 Generate All Financial Reports",
            command=self.generate_financial_reports,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2E86AB",
            hover_color="#1E40AF"
        )
        main_generate_btn.pack(pady=(0, 20))
        
        # Charts container
        self.financial_charts_frame = ctk.CTkFrame(container, corner_radius=8)
        self.financial_charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize control variables
        self.selected_year_var = ctk.StringVar(value=str(datetime.now().year))
        self.selected_month_var = ctk.StringVar(value=str(datetime.now().month))
        self.daily_year_var = ctk.StringVar(value=str(datetime.now().year))
        self.selected_date_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        
        # Initialize with current data
        self.generate_financial_reports()
    
    def on_year_changed(self, value):
        controls_frame.pack(fill="x", padx=10, pady=(0, 20))
        
        # Title for controls
        controls_title = ctk.CTkLabel(
            controls_frame,
            text="📊 Report Controls",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2E86AB"
        )
        controls_title.pack(pady=(15, 10))
        
        # Year selection for monthly reports
        year_frame = ctk.CTkFrame(controls_frame)
        year_frame.pack(pady=(0, 10), padx=20)
        
        ctk.CTkLabel(year_frame, text="Select Year for Monthly Analysis:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        self.selected_year_var = ctk.StringVar(value=str(datetime.now().year))
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 3, current_year + 2)]
        
        self.year_dropdown = ctk.CTkComboBox(
            year_frame,
            values=years,
            variable=self.selected_year_var,
            command=self.on_year_changed,
            width=150
        )
        self.year_dropdown.pack(pady=(0, 10))
        
        # Month and Year selection for daily sales
        daily_frame = ctk.CTkFrame(controls_frame)
        daily_frame.pack(pady=(0, 10), padx=20)
        
        ctk.CTkLabel(daily_frame, text="Select Month/Year for Daily Sales:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        daily_controls = ctk.CTkFrame(daily_frame)
        daily_controls.pack(pady=(0, 10))
        
        self.selected_month_var = ctk.StringVar(value=str(datetime.now().month))
        months = [str(i) for i in range(1, 13)]
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        self.month_dropdown = ctk.CTkComboBox(
            daily_controls,
            values=[f"{i} - {month_names[i-1]}" for i in range(1, 13)],
            variable=self.selected_month_var,
            command=self.on_month_changed,
            width=120
        )
        self.month_dropdown.pack(side="left", padx=(0, 10))
        
        self.daily_year_var = ctk.StringVar(value=str(datetime.now().year))
        self.daily_year_dropdown = ctk.CTkComboBox(
            daily_controls,
            values=years,
            variable=self.daily_year_var,
            command=self.on_daily_year_changed,
            width=100
        )
        self.daily_year_dropdown.pack(side="left")
        
        # Date selection for daily transactions
        transaction_frame = ctk.CTkFrame(controls_frame)
        transaction_frame.pack(pady=(0, 15), padx=20)
        
        ctk.CTkLabel(transaction_frame, text="Select Date for Daily Transactions:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5))
        
        self.selected_date_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ctk.CTkEntry(
            transaction_frame,
            textvariable=self.selected_date_var,
            placeholder_text="YYYY-MM-DD",
            width=150
        )
        self.date_entry.pack(pady=(0, 10))
        
        # Generate button
        generate_btn = ctk.CTkButton(
            controls_frame,
            text="� Generate Financial Reports",
            command=self.generate_financial_reports,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2E86AB",
            hover_color="#1E40AF"
        )
        generate_btn.pack(pady=(0, 15))
        
        # Charts container
        self.financial_charts_frame = ctk.CTkFrame(container, corner_radius=8)
        self.financial_charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize with current data
        self.generate_financial_reports()
    
    def on_year_changed(self, value):
        """Handle year selection change"""
        self.selected_year_var.set(value)
        
    def on_month_changed(self, value):
        """Handle month selection change"""
        month_num = value.split(" - ")[0]
        self.selected_month_var.set(month_num)
        
    def on_daily_year_changed(self, value):
        """Handle daily year selection change"""
        self.daily_year_var.set(value)
        
    def on_histogram_year_changed(self, value):
        """Handle histogram year selection change"""
        self.selected_year_var.set(value)
        
    def get_employee_list(self):
        """Get list of employees for dropdown"""
        try:
            if not self.data_service:
                return ["No employees found"]
                
            employees_df = self.data_service.get_employees()
            if employees_df.empty:
                return ["No employees found"]
            
            employee_list = []
            for _, emp in employees_df.iterrows():
                employee_list.append(f"{emp['employee_id']} - {emp['name']}")
            
            return employee_list
            
        except Exception as e:
            logger.error(f"Error loading employees: {e}")
            return ["Error loading employees"]
    
    def on_employee_selected(self, selection):
        """Handle employee selection"""
        if selection and " - " in selection:
            self.selected_employee = selection.split(" - ")[0]  # Get employee ID
            self.create_attendance_calendar()
            self.create_attendance_stats()
    
    def on_month_selected(self, selection):
        """Handle month selection"""
        if selection:
            self.selected_month = list(calendar.month_name).index(selection)
            if self.selected_employee:
                self.create_attendance_calendar()
                self.create_attendance_stats()
    
    def on_year_selected(self, selection):
        """Handle year selection"""
        if selection:
            self.selected_year = int(selection)
            if self.selected_employee:
                self.create_attendance_calendar()
                self.create_attendance_stats()
    
    def refresh_calendar(self):
        """Refresh the calendar with current selections"""
        if self.selected_employee:
            self.create_attendance_calendar()
            self.create_attendance_stats()
    
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
            
    def create_attendance_calendar(self):
        """Create enhanced, better-looking attendance calendar"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
            
        # Calendar header with modern styling
        header_frame = ctk.CTkFrame(self.calendar_frame, height=60, corner_radius=10, fg_color=self.colors['primary'])
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="📅 Monthly Attendance Overview",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        header_label.pack(expand=True, pady=15)
        
        if not self.selected_employee:
            # Show modern instruction message
            instruction_frame = ctk.CTkFrame(self.calendar_frame, corner_radius=15)
            instruction_frame.pack(expand=True, fill="both", padx=20, pady=20)
            
            icon_label = ctk.CTkLabel(
                instruction_frame,
                text="👤",
                font=ctk.CTkFont(size=48)
            )
            icon_label.pack(pady=(50, 10))
            
            instruction_label = ctk.CTkLabel(
                instruction_frame,
                text="Select an employee above to view their attendance calendar",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            instruction_label.pack(pady=(0, 50))
            return
        
        try:
            import pandas as pd
            
            # Get employee info
            employee_info = self.get_employee_info(self.selected_employee)
            
            # Create calendar for current month
            year = self.selected_year
            month = self.selected_month
            
            # Get attendance data for selected employee (handle data inconsistency)
            # Some records may have employee_id as "35011" and others as "35011 - Name"
            attendance_df_exact = self.data_service.get_attendance({
                "employee_id": self.selected_employee
            })
            
            # Also get records that might have the employee name appended
            all_attendance = self.data_service.get_attendance()
            attendance_df_flexible = all_attendance[
                all_attendance['employee_id'].str.startswith(self.selected_employee)
            ] if not all_attendance.empty else pd.DataFrame()
            
            # Combine both result sets and remove duplicates
            if not attendance_df_exact.empty and not attendance_df_flexible.empty:
                attendance_df = pd.concat([attendance_df_exact, attendance_df_flexible]).drop_duplicates()
            elif not attendance_df_exact.empty:
                attendance_df = attendance_df_exact
            elif not attendance_df_flexible.empty:
                attendance_df = attendance_df_flexible
            else:
                attendance_df = pd.DataFrame()
            
            # Employee info header
            emp_info_frame = ctk.CTkFrame(self.calendar_frame, corner_radius=10)
            emp_info_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            emp_name = employee_info.get('name', 'Unknown Employee')
            emp_dept = employee_info.get('department', 'N/A')
            
            emp_label = ctk.CTkLabel(
                emp_info_frame,
                text=f"👤 {emp_name} | 🏢 {emp_dept}",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            emp_label.pack(pady=15)
            
            # Month navigation with better styling
            nav_frame = ctk.CTkFrame(self.calendar_frame, height=50, corner_radius=10)
            nav_frame.pack(fill="x", padx=20, pady=10)
            nav_frame.pack_propagate(False)
            
            month_label = ctk.CTkLabel(
                nav_frame,
                text=f"📅 {calendar.month_name[month]} {year}",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            month_label.pack(expand=True, pady=10)
            
            # Calendar container with better styling
            cal_container = ctk.CTkFrame(self.calendar_frame, corner_radius=15)
            cal_container.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Create improved calendar grid
            self.create_enhanced_calendar_grid(cal_container, year, month, attendance_df)
            
        except Exception as e:
            error_frame = ctk.CTkFrame(self.calendar_frame, corner_radius=15)
            error_frame.pack(expand=True, fill="both", padx=20, pady=20)
            
            error_icon = ctk.CTkLabel(
                error_frame,
                text="❌",
                font=ctk.CTkFont(size=48)
            )
            error_icon.pack(pady=(50, 10))
            
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"Error loading calendar: {str(e)}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(pady=(0, 50))
    
    def get_employee_info(self, employee_id):
        """Get employee information"""
        try:
            employees_df = self.data_service.get_employees({"employee_id": employee_id})
            if not employees_df.empty:
                return employees_df.iloc[0].to_dict()
            return {}
        except:
            return {}
    
    def create_enhanced_calendar_grid(self, parent, year, month, attendance_df):
        """Create an enhanced, more readable calendar grid"""
        # Create main grid frame with padding
        grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Day headers with improved styling
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#84CC16']
        
        for i, day in enumerate(days):
            day_header = ctk.CTkFrame(
                grid_frame,
                width=100,
                height=40,
                corner_radius=8,
                fg_color=day_colors[i % len(day_colors)]
            )
            day_header.grid(row=0, column=i, padx=3, pady=3, sticky="ew")
            day_header.grid_propagate(False)
            
            day_label = ctk.CTkLabel(
                day_header,
                text=day[:3],  # Show first 3 letters
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            day_label.pack(expand=True)
        
        # Configure grid weights
        for i in range(7):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        # Get calendar data
        cal = calendar.monthcalendar(year, month)
        
        # Create attendance lookup dictionary
        attendance_lookup = {}
        if not attendance_df.empty:
            for _, record in attendance_df.iterrows():
                # Handle different date formats properly
                try:
                    if hasattr(record['date'], 'date'):
                        # Pandas Timestamp or datetime object
                        record_date = record['date'].date()
                    elif isinstance(record['date'], str):
                        # String date
                        try:
                            record_date = datetime.strptime(record['date'], '%Y-%m-%d').date()
                        except ValueError:
                            try:
                                record_date = datetime.fromisoformat(record['date'].replace('Z', '+00:00')).date()
                            except ValueError:
                                continue
                    else:
                        # Other format, try to convert
                        record_date = pd.to_datetime(record['date']).date()
                    
                    attendance_lookup[record_date] = record['status']
                except Exception as e:
                    logger.error(f"Error parsing date {record['date']}: {e}")
                    continue
        
        # Create calendar cells with enhanced design
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days from other months
                    empty_frame = ctk.CTkFrame(
                        grid_frame,
                        width=100,
                        height=80,
                        corner_radius=8,
                        fg_color="#f0f0f0"
                    )
                    empty_frame.grid(row=week_num + 1, column=day_num, padx=3, pady=3, sticky="ew")
                    empty_frame.grid_propagate(False)
                else:
                    # Check attendance status for this day
                    day_date = date(year, month, day)
                    today = date.today()
                    
                    # Determine status
                    if day_date > today:
                        # Future date
                        status = "Future"
                    else:
                        # Past or current date - check attendance
                        raw_status = attendance_lookup.get(day_date, "No Data")
                        
                        # Map old statuses to new simplified system
                        status_mapping = {
                            'Present': 'Present',
                            'Absent': 'Absent', 
                            'Leave': 'Leave',
                            'Overtime': 'Overtime',
                            'Late': 'Present',           # Map Late to Present
                            'Half Day': 'Present',       # Map Half Day to Present
                            'Remote Work': 'Present',    # Map Remote Work to Present
                            'Work from Home': 'Present', # Map WFH to Present
                            'No Data': 'No Data'
                        }
                        status = status_mapping.get(raw_status, 'No Data')
                    
                    # Determine cell appearance based on status
                    if status in self.attendance_colors:
                        bg_color = self.attendance_colors[status]
                        if status == 'Future':
                            text_color = "#374151"  # Dark text for white background
                        elif status == 'No Data':
                            text_color = "#6b7280"  # Gray text for gray background
                        else:
                            text_color = "white"    # White text for colored backgrounds
                        status_emoji = self.get_status_emoji(status)
                    else:
                        bg_color = self.attendance_colors['No Data']
                        text_color = "#6b7280"
                        status_emoji = "📅"
                    
                    # Create enhanced day cell
                    if status == 'Future':
                        # Future dates get a subtle border
                        day_frame = ctk.CTkFrame(
                            grid_frame,
                            width=100,
                            height=80,
                            fg_color=bg_color,
                            border_width=1,
                            border_color="#D1D5DB",
                            corner_radius=12
                        )
                    else:
                        # Regular cells without border
                        day_frame = ctk.CTkFrame(
                            grid_frame,
                            width=100,
                            height=80,
                            fg_color=bg_color,
                            corner_radius=12
                        )
                    day_frame.grid(row=week_num + 1, column=day_num, padx=3, pady=3, sticky="ew")
                    day_frame.grid_propagate(False)
                    
                    # Day number
                    day_label = ctk.CTkLabel(
                        day_frame,
                        text=str(day),
                        font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=text_color
                    )
                    day_label.pack(pady=(8, 2))
                    
                    # Status emoji and text
                    if status != "No Data":
                        status_label = ctk.CTkLabel(
                            day_frame,
                            text=status_emoji,
                            font=ctk.CTkFont(size=14)
                        )
                        status_label.pack()
                        
                        status_text = ctk.CTkLabel(
                            day_frame,
                            text=status[:4],  # First 4 characters
                            font=ctk.CTkFont(size=9, weight="bold"),
                            text_color=text_color
                        )
                        status_text.pack(pady=(0, 5))
                    else:
                        no_data_label = ctk.CTkLabel(
                            day_frame,
                            text="--",
                            font=ctk.CTkFont(size=12),
                            text_color=text_color
                        )
                        no_data_label.pack(expand=True)
    
    def get_status_emoji(self, status):
        """Get emoji for attendance status - Simplified"""
        emoji_map = {
            'Present': '✅',
            'Absent': '❌',
            'Leave': '🏖️',
            'Overtime': '⏱️',
            'Future': '📅',
            'No Data': '📅'
        }
        return emoji_map.get(status, '📅')
    
    def create_attendance_legend(self):
        """Create enhanced color legend for attendance status"""
        # Clear existing legend
        if hasattr(self, '_legend_frame') and self._legend_frame.winfo_exists():
            self._legend_frame.destroy()
        
        # Legend header with modern styling
        legend_header_frame = ctk.CTkFrame(self.stats_frame, height=50, corner_radius=10, fg_color=self.colors['info'])
        legend_header_frame.pack(fill="x", padx=10, pady=(20, 10))
        legend_header_frame.pack_propagate(False)
        
        legend_header = ctk.CTkLabel(
            legend_header_frame,
            text="🎨 Color Legend",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        legend_header.pack(expand=True, pady=10)
        
        # Legend items with enhanced design
        legend_frame = ctk.CTkFrame(self.stats_frame, corner_radius=15)
        legend_frame.pack(fill="x", padx=10, pady=10)
        # Store reference for cleanup
        self._legend_frame = legend_frame
        
        # Create legend items with emojis and better layout - Simplified
        legend_items = [
            ('Present', self.attendance_colors['Present'], '✅'),
            ('Absent', self.attendance_colors['Absent'], '❌'),
            ('Leave', self.attendance_colors['Leave'], '🏖️'),
            ('No Data', self.attendance_colors['No Data'], '📅')
        ]
        
        for i, (status, color, emoji) in enumerate(legend_items):
            item_frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=5, padx=15)
            
            # Emoji
            emoji_label = ctk.CTkLabel(
                item_frame,
                text=emoji,
                font=ctk.CTkFont(size=16)
            )
            emoji_label.pack(side="left", padx=(0, 10))
            
            # Color indicator with better design
            color_frame = ctk.CTkFrame(
                item_frame,
                width=25,
                height=25,
                fg_color=color,
                corner_radius=12
            )
            color_frame.pack(side="left", padx=(0, 10))
            color_frame.pack_propagate(False)
            
            # Status text with better formatting
            status_label = ctk.CTkLabel(
                item_frame,
                text=status,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            status_label.pack(side="left", padx=5)
    
    def create_attendance_stats(self):
        """Create attendance statistics with date range option"""
        # Clear existing stats (but keep legend)
        for widget in self.stats_frame.winfo_children():
            if hasattr(widget, 'cget'):
                try:
                    text = widget.cget('text')
                    if 'Legend' not in text and 'Statistics' not in text:
                        continue  # Skip legend and stat headers
                except:
                    pass
            if widget != getattr(self, '_legend_frame', None):
                widget.destroy()
        
        if not self.selected_employee:
            return
            
        try:
            # Statistics header
            stats_header = ctk.CTkLabel(
                self.stats_frame,
                text="📊 Attendance Statistics",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            stats_header.pack(pady=(15, 5))
            
            # Stat Type Selection Frame
            stat_type_frame = ctk.CTkFrame(self.stats_frame, corner_radius=8)
            stat_type_frame.pack(fill="x", padx=10, pady=(0, 5))
            
            ctk.CTkLabel(
                stat_type_frame,
                text="Stat Type:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=10, pady=10)
            
            # Initialize stat type variable if not exists
            if not hasattr(self, 'stat_type_var'):
                self.stat_type_var = ctk.StringVar(value="Overall")
            
            stat_type_dropdown = ctk.CTkComboBox(
                stat_type_frame,
                variable=self.stat_type_var,
                values=["Overall", "Range"],
                width=120,
                height=35,
                command=self.on_stat_type_change
            )
            stat_type_dropdown.pack(side="left", padx=(0, 10))
            
            # Date Range Frame (separate frame below stat type)
            self.date_range_frame = ctk.CTkFrame(self.stats_frame, corner_radius=8)
            
            # Initialize date variables if not exist
            if not hasattr(self, 'start_date_var'):
                from datetime import date, timedelta
                today = date.today()
                month_ago = today - timedelta(days=30)
                self.start_date_var = ctk.StringVar(value=month_ago.strftime('%Y-%m-%d'))
                self.end_date_var = ctk.StringVar(value=today.strftime('%Y-%m-%d'))
            
            # Date range content frame
            date_content_frame = ctk.CTkFrame(self.date_range_frame, fg_color="transparent")
            date_content_frame.pack(fill="x", padx=10, pady=5)
            
            # First row: From date
            from_row = ctk.CTkFrame(date_content_frame, fg_color="transparent")
            from_row.pack(fill="x", pady=(0, 3))
            
            ctk.CTkLabel(
                from_row,
                text="From:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=60
            ).pack(side="left", padx=(0, 5))
            
            self.start_date_entry = ctk.CTkEntry(
                from_row,
                textvariable=self.start_date_var,
                width=120,
                height=35,
                placeholder_text="YYYY-MM-DD"
            )
            self.start_date_entry.pack(side="left", padx=(0, 5))
            
            # Calendar button for start date
            def open_start_date_picker():
                self.open_date_picker(self.start_date_var)
            
            start_cal_btn = ctk.CTkButton(
                from_row,
                text="📅",
                width=40,
                height=35,
                font=ctk.CTkFont(size=12),
                command=open_start_date_picker
            )
            start_cal_btn.pack(side="left", padx=(0, 10))
            
            # Second row: To date  
            to_row = ctk.CTkFrame(date_content_frame, fg_color="transparent")
            to_row.pack(fill="x", pady=(0, 3))
            
            ctk.CTkLabel(
                to_row,
                text="To:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=60
            ).pack(side="left", padx=(0, 5))
            
            self.end_date_entry = ctk.CTkEntry(
                to_row,
                textvariable=self.end_date_var,
                width=120,
                height=35,
                placeholder_text="YYYY-MM-DD"
            )
            self.end_date_entry.pack(side="left", padx=(0, 5))
            
            # Calendar button for end date
            def open_end_date_picker():
                self.open_date_picker(self.end_date_var)
            
            end_cal_btn = ctk.CTkButton(
                to_row,
                text="📅",
                width=40,
                height=35,
                font=ctk.CTkFont(size=12),
                command=open_end_date_picker
            )
            end_cal_btn.pack(side="left", padx=(0, 10))
            
            # Third row: Update button
            button_row = ctk.CTkFrame(date_content_frame, fg_color="transparent")
            button_row.pack(fill="x", pady=(3, 0))
            
            update_stats_btn = ctk.CTkButton(
                button_row,
                text="Update Statistics",
                command=self.update_attendance_stats,
                height=35,
                width=150,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=self.colors['primary'],
                hover_color=self.darken_color(self.colors['primary'])
            )
            update_stats_btn.pack(side="left")
            
            # Show/hide date range based on current selection
            self.on_stat_type_change(self.stat_type_var.get())
            
            # Generate the actual statistics
            self.update_attendance_stats()
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.stats_frame,
                text=f"Error loading statistics: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="red"
            )
            error_label.pack(pady=20)
    
    def on_stat_type_change(self, selection):
        """Handle stat type dropdown change"""
        try:
            if selection == "Range":
                self.date_range_frame.pack(fill="x", padx=10, pady=(0, 5))
            else:
                self.date_range_frame.pack_forget()
            
            # Update stats when type changes
            self.update_attendance_stats()
        except Exception as e:
            pass  # Ignore errors during initialization
    
    def update_attendance_stats(self):
        """Update attendance statistics based on selected type and date range"""
        try:
            # Clear existing stats display (but keep the controls)
            # Find and remove only the stats container by checking for our specific attribute
            for widget in self.stats_frame.winfo_children():
                if hasattr(widget, 'stats_container_marker'):
                    widget.destroy()
            
            if not self.selected_employee:
                return
                
            # Get attendance data for selected employee
            attendance_df = self.data_service.get_attendance({
                "employee_id": self.selected_employee
            })
            
            if attendance_df.empty:
                no_data_label = ctk.CTkLabel(
                    self.stats_frame,
                    text="No attendance data found",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                no_data_label.pack(pady=20)
                # Mark as statistics content for clearing
                no_data_label.stats_container_marker = True
                return
            
            # Filter by date range if "Range" is selected
            if self.stat_type_var.get() == "Range":
                try:
                    from datetime import datetime
                    start_date = datetime.strptime(self.start_date_var.get(), '%Y-%m-%d').date()
                    end_date = datetime.strptime(self.end_date_var.get(), '%Y-%m-%d').date()
                    
                    # Convert date column to datetime for comparison
                    attendance_df['date_parsed'] = pd.to_datetime(attendance_df['date']).dt.date
                    attendance_df = attendance_df[
                        (attendance_df['date_parsed'] >= start_date) & 
                        (attendance_df['date_parsed'] <= end_date)
                    ]
                    
                    if attendance_df.empty:
                        no_data_label = ctk.CTkLabel(
                            self.stats_frame,
                            text="No attendance data found for selected date range",
                            font=ctk.CTkFont(size=12),
                            text_color="gray"
                        )
                        no_data_label.pack(pady=20)
                        # Mark as statistics content for clearing
                        no_data_label.stats_container_marker = True
                        return
                        
                except ValueError:
                    error_label = ctk.CTkLabel(
                        self.stats_frame,
                        text="Invalid date format. Please use YYYY-MM-DD",
                        font=ctk.CTkFont(size=12),
                        text_color="red"
                    )
                    error_label.pack(pady=20)
                    # Mark as statistics content for clearing
                    error_label.stats_container_marker = True
                    return
            
            # Calculate statistics
            stats = attendance_df['status'].value_counts()
            total_days = len(attendance_df)
            
            # Statistics container
            stats_container = ctk.CTkFrame(self.stats_frame, corner_radius=8)
            stats_container.pack(fill="x", padx=10, pady=5)
            # Mark this as a statistics container for easy identification
            stats_container.stats_container_marker = True
            
            # Display statistics
            for status, count in stats.items():
                percentage = (count / total_days) * 100 if total_days > 0 else 0
                
                stat_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
                stat_frame.pack(fill="x", pady=3)
                
                # Status with color indicator
                status_frame = ctk.CTkFrame(stat_frame, fg_color="transparent")
                status_frame.pack(side="left", fill="x", expand=True)
                
                color_indicator = ctk.CTkFrame(
                    status_frame,
                    width=15,
                    height=15,
                    fg_color=self.attendance_colors.get(status, "#6B7280"),
                    corner_radius=2
                )
                color_indicator.pack(side="left", padx=(10, 5), pady=8)
                color_indicator.pack_propagate(False)
                
                status_text = ctk.CTkLabel(
                    status_frame,
                    text=f"{status}:",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                status_text.pack(side="left", padx=5, pady=5)
                
                # Count and percentage
                count_text = ctk.CTkLabel(
                    stat_frame,
                    text=f"{count} ({percentage:.1f}%)",
                    font=ctk.CTkFont(size=12)
                )
                count_text.pack(side="right", padx=10, pady=5)
            
            # Total days
            total_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
            total_frame.pack(fill="x", pady=(10, 5))
            
            period_text = "Overall" if self.stat_type_var.get() == "Overall" else f"Range ({self.start_date_var.get()} to {self.end_date_var.get()})"
            
            ctk.CTkLabel(
                total_frame,
                text=f"Total Days ({period_text}):",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=10, pady=5)
            
            ctk.CTkLabel(
                total_frame,
                text=str(total_days),
                font=ctk.CTkFont(size=12)
            ).pack(side="right", padx=10, pady=5)
            
            # Calculate and display overtime hours for the selected employee
            total_overtime_hours = 0.0
            for _, row in attendance_df.iterrows():
                try:
                    hours_worked = 0.0
                    
                    # Method 1: Check if 'hours' field exists and has a value
                    hours_value = row.get('hours', None)
                    if hours_value is not None and hours_value != '' and hours_value != 0:
                        # Convert to float
                        if isinstance(hours_value, str):
                            hours_value = hours_value.strip()
                            if hours_value != '':
                                hours_worked = float(hours_value)
                        else:
                            hours_worked = float(hours_value)
                    
                    # Method 2: If no 'hours' field, calculate from time_in and time_out
                    else:
                        time_in = row.get('time_in', '')
                        time_out = row.get('time_out', '')
                        
                        if time_in and time_out and time_in != '' and time_out != '':
                            hours_worked = self.calculate_hours(time_in, time_out)
                    
                    # Calculate overtime if we have hours worked (subtract additional 1 hour as requested)
                    if hours_worked > 0:
                        overtime = max(0, hours_worked - 8.0 - 1.0)
                        total_overtime_hours += overtime
                        
                except (ValueError, TypeError, AttributeError):
                    # Skip invalid entries
                    continue
            
            # Overtime hours display
            overtime_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
            overtime_frame.pack(fill="x", pady=(5, 5))
            
            ctk.CTkLabel(
                overtime_frame,
                text="Overtime Hours:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['warning']
            ).pack(side="left", padx=10, pady=5)
            
            ctk.CTkLabel(
                overtime_frame,
                text=f"{total_overtime_hours:.1f}h",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['warning']
            ).pack(side="right", padx=10, pady=5)
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.stats_frame,
                text=f"Error updating statistics: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="red"
            )
            error_label.pack(pady=20)
            # Mark as statistics content for clearing
            error_label.stats_container_marker = True
    
    def open_date_picker(self, date_var):
        """Open a simple date picker dialog"""
        try:
            # Import here to avoid circular imports
            import tkinter as tk
            from tkinter import messagebox
            import calendar
            from datetime import datetime, date
            
            # Create a simple date picker window
            picker_window = tk.Toplevel()
            picker_window.title(f"Select Date")
            picker_window.geometry("350x400")  # Increased size for better visibility
            picker_window.resizable(False, False)
            picker_window.grab_set()  # Make modal
            
            # Center the window
            picker_window.transient(self.parent)
            
            # Current date or selected date
            try:
                current_date = datetime.strptime(date_var.get(), '%Y-%m-%d').date()
            except:
                current_date = date.today()
            
            # Variables for year and month
            year_var = tk.IntVar(value=current_date.year)
            month_var = tk.IntVar(value=current_date.month)
            selected_day = tk.IntVar(value=current_date.day)
            
            # Year and month selection frame
            control_frame = tk.Frame(picker_window)
            control_frame.pack(pady=15)
            
            tk.Label(control_frame, text="Year:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
            year_spinbox = tk.Spinbox(control_frame, from_=2020, to=2030, textvariable=year_var, width=6, command=lambda: update_calendar())
            year_spinbox.pack(side="left", padx=5)
            
            tk.Label(control_frame, text="Month:", font=("Arial", 10, "bold")).pack(side="left", padx=10)
            month_spinbox = tk.Spinbox(control_frame, from_=1, to=12, textvariable=month_var, width=4, command=lambda: update_calendar())
            month_spinbox.pack(side="left", padx=5)
            
            # Calendar frame
            cal_frame = tk.Frame(picker_window)
            cal_frame.pack(pady=15)
            
            # Days of week header
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for i, day in enumerate(days):
                tk.Label(cal_frame, text=day, font=("Arial", 9, "bold"), width=4).grid(row=0, column=i, padx=1, pady=1)
            
            day_buttons = {}
            
            def update_calendar():
                # Clear existing buttons
                for btn in day_buttons.values():
                    btn.destroy()
                day_buttons.clear()
                
                # Get calendar for the month
                cal = calendar.monthcalendar(year_var.get(), month_var.get())
                
                for week_num, week in enumerate(cal, 1):
                    for day_num, day in enumerate(week):
                        if day == 0:
                            continue
                        
                        btn = tk.Button(
                            cal_frame,
                            text=str(day),
                            width=4,
                            height=2,
                            font=("Arial", 9),
                            command=lambda d=day: select_day(d)
                        )
                        btn.grid(row=week_num, column=day_num, padx=2, pady=2)
                        day_buttons[day] = btn
                        
                        # Highlight current selection
                        if day == selected_day.get() and year_var.get() == current_date.year and month_var.get() == current_date.month:
                            btn.configure(bg="lightblue")
            
            def select_day(day):
                selected_day.set(day)
                # Update button colors
                for d, btn in day_buttons.items():
                    if d == day:
                        btn.configure(bg="lightblue")
                    else:
                        btn.configure(bg="SystemButtonFace")
            
            def confirm_date():
                try:
                    selected_date = date(year_var.get(), month_var.get(), selected_day.get())
                    date_var.set(selected_date.strftime('%Y-%m-%d'))
                    picker_window.destroy()
                    # Update stats after date selection
                    if hasattr(self, 'update_attendance_stats'):
                        self.update_attendance_stats()
                except ValueError:
                    messagebox.showerror("Invalid Date", "Please select a valid date.")
            
            # Buttons frame
            btn_frame = tk.Frame(picker_window)
            btn_frame.pack(pady=20)
            
            tk.Button(btn_frame, text="Today", command=lambda: (year_var.set(date.today().year), month_var.set(date.today().month), selected_day.set(date.today().day), update_calendar()), font=("Arial", 9), width=8).pack(side="left", padx=8)
            tk.Button(btn_frame, text="OK", command=confirm_date, bg="lightgreen", font=("Arial", 9, "bold"), width=8).pack(side="left", padx=8)
            tk.Button(btn_frame, text="Cancel", command=picker_window.destroy, font=("Arial", 9), width=8).pack(side="left", padx=8)
            
            # Initial calendar display
            update_calendar()
            
        except Exception as e:
            messagebox.showerror("Date Picker Error", f"Error opening date picker: {str(e)}")
    
    def generate_employee_reports(self):
        """Generate enhanced employee analytics"""
        # Clear previous charts
        for widget in self.employee_charts_frame.winfo_children():
            widget.destroy()
        
        try:
            # Create prominent total wage display at the top
            self.create_total_wage_display()
            
            # Create charts with better spacing
            self.create_chart_section(
                self.employee_charts_frame,
                "👥 Department Distribution",
                self.create_department_chart,
                height=400
            )
            
            self.create_chart_section(
                self.employee_charts_frame,
                "💰 Daily Wage Analysis",
                self.create_daily_wage_chart,
                height=400
            )
            
            self.create_chart_section(
                self.employee_charts_frame,
                "📊 Monthly Attendance Stats",
                self.create_employee_overview_chart,
                height=400
            )
            
            self.create_chart_section(
                self.employee_charts_frame,
                "🏆 Employee Statistics",
                self.create_employee_stats_report,
                height=400
            )
            
            self.show_status_message("Employee reports generated successfully", "success")
            
        except Exception as e:
            self.show_status_message(f"Error generating employee reports: {str(e)}", "error")
    
    def create_total_wage_display(self):
        """Create prominent total wage to be paid display at the top"""
        try:
            # Use the new wage calculator for accurate total wage calculation
            from new_wage_calculator import NewWageCalculator
            
            calculator = NewWageCalculator(self.data_service)
            wage_calculation_result = calculator.calculate_all_employees_total_wage()
            
            total_wages_to_pay = wage_calculation_result.get('total_wage', 0)
            employees_with_dues = wage_calculation_result.get('total_employees', 0)
            
            # Convert the detailed employee data for display
            calculation_details = []
            for emp_data in wage_calculation_result.get('employees', []):
                if emp_data.get('total_wage', 0) > 0:
                    calculation_details.append({
                        'emp_id': emp_data.get('employee_id', ''),
                        'name': emp_data.get('employee_name', 'Unknown'),
                        'wage': emp_data.get('total_wage', 0),
                        'days': emp_data.get('work_days', 0),
                        'overtime': emp_data.get('total_overtime_hours', 0)  # Get actual overtime hours
                    })
            
            # Update employees_with_dues to only count those with wages > 0
            employees_with_dues = len(calculation_details)
            
            # Create prominent display frame
            total_wage_frame = ctk.CTkFrame(
                self.employee_charts_frame, 
                corner_radius=15,
                fg_color="#1a472a",  # Dark green background
                height=120
            )
            total_wage_frame.pack(fill="x", padx=15, pady=(10, 20))
            total_wage_frame.pack_propagate(False)
            
            # Main title
            title_label = ctk.CTkLabel(
                total_wage_frame,
                text="💰 TOTAL WAGES TO BE PAID",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#ffffff"
            )
            title_label.pack(pady=(15, 5))
            
            # Amount display
            amount_label = ctk.CTkLabel(
                total_wage_frame,
                text=f"₹{total_wages_to_pay:,.2f}",
                font=ctk.CTkFont(size=32, weight="bold"),
                text_color="#4ade80"  # Bright green
            )
            amount_label.pack(pady=(0, 5))
            
            # Details
            details_text = f"Outstanding wages for {employees_with_dues} employees"
            if employees_with_dues > 0:
                avg_per_employee = total_wages_to_pay / employees_with_dues
                details_text += f" • Average: ₹{avg_per_employee:,.2f} per employee"
            
            details_label = ctk.CTkLabel(
                total_wage_frame,
                text=details_text,
                font=ctk.CTkFont(size=12),
                text_color="#d1fae5"
            )
            details_label.pack(pady=(0, 15))
            
            logger.info(f"Total wage calculation: ₹{total_wages_to_pay:,.2f} for {employees_with_dues} employees")
            
        except Exception as e:
            logger.error(f"Error creating total wage display: {e}")
            # Create error display
            error_frame = ctk.CTkFrame(self.employee_charts_frame, corner_radius=10, fg_color="#7f1d1d")
            error_frame.pack(fill="x", padx=15, pady=(10, 20))
            
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"❌ Error calculating total wages: {str(e)}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ffffff"
            )
            error_label.pack(pady=20)
    
    def generate_financial_reports(self):
        """Generate enhanced financial reports with new structure"""
        # Clear previous charts
        for widget in self.financial_charts_frame.winfo_children():
            widget.destroy()
            
        # Clear monthly summary
        for widget in self.monthly_summary_frame.winfo_children():
            widget.destroy()

        try:
            # Generate monthly summary at top
            self.create_monthly_summary()
            
            # 1. Monthly Expense vs Sales Histogram (NEW)
            self.create_chart_section_with_controls(
                self.financial_charts_frame,
                "📊 Monthly Expense vs Sales Comparison",
                self.create_monthly_expense_vs_sales_histogram,
                "monthly_histogram",
                height=400
            )

            # 2. Daily Sales Trend (Month/Year-based)
            self.create_chart_section_with_controls(
                self.financial_charts_frame,
                "📈 Daily Sales Trend",
                self.create_daily_sales_chart,
                "daily_sales",
                height=400
            )
            
            # 3. Daily Transactions (Date-based)
            self.create_chart_section_with_controls(
                self.financial_charts_frame,
                "💳 Daily Transactions",
                self.create_daily_transactions_chart,
                "daily_transactions",
                height=400
            )
            
            # 4. Top Customer Spenders
            self.create_chart_section(
                self.financial_charts_frame,
                "🏆 Top Customer Spenders",
                self.create_top_customers_chart,
                height=400
            )
            
            # 5. Outstanding Dues Analysis
            self.create_chart_section(
                self.financial_charts_frame,
                "⚠️ Outstanding Dues Analysis",
                self.create_dues_analysis_chart,
                height=400
            )
            
            self.show_status_message("Financial reports generated successfully", "success")
            
        except Exception as e:
            logger.error(f"Error generating financial reports: {str(e)}")
            self.show_status_message(f"Error generating financial reports: {str(e)}", "error")
    
    def show_status_message(self, message, message_type="info"):
        """Show status message - robust version"""
        try:
            # Check if status bar is initialized
            if hasattr(self, 'status_icon') and self.status_icon:
                # Use full status bar functionality
                icons = {
                    "success": "✅",
                    "error": "❌", 
                    "warning": "⚠️",
                    "info": "ℹ️"
                }
                
                # Update components
                self.status_icon.configure(text=icons.get(message_type, "📊"))
                self.status_label.configure(text=message)
                
                # Add timestamp
                from datetime import datetime
                current_time = datetime.now().strftime("%H:%M:%S")
                self.status_time.configure(text=current_time)
                
                # Clear message after 5 seconds
                self.frame.after(5000, lambda: self.reset_status())
            else:
                # Just log the message since status bar isn't ready
                if message_type == "error":
                    logger.error(message)
                else:
                    logger.info(message)
        except Exception as e:
            logger.error(f"Error showing status message: {str(e)}")
    
    def create_monthly_summary(self):
        """Create monthly summary display at the top"""
        try:
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Get data using correct method names
            orders_data = self.data_service.get_all_orders()
            purchases_df = self.data_service.get_purchases()
            
            # Calculate current month totals
            monthly_sales = 0
            monthly_expenses = 0
            
            # Process orders data
            if orders_data:
                for order in orders_data:
                    try:
                        order_date = pd.to_datetime(order.get('created_date', order.get('date', '')))
                        if (order_date.month == current_month and 
                            order_date.year == current_year):
                            monthly_sales += float(order.get('total_amount', 0))
                    except:
                        continue
            
            # Process purchases data
            if not purchases_df.empty:
                purchases_df['date'] = pd.to_datetime(purchases_df['date'])
                current_month_purchases = purchases_df[
                    (purchases_df['date'].dt.month == current_month) & 
                    (purchases_df['date'].dt.year == current_year)
                ]
                monthly_expenses = current_month_purchases['total_price'].sum()
            
            # Create summary display
            summary_title = ctk.CTkLabel(
                self.monthly_summary_frame,
                text=f"📅 {datetime.now().strftime('%B %Y')} Summary",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#2E86AB"
            )
            summary_title.pack(pady=(15, 10))
            
            # Summary stats frame
            stats_frame = ctk.CTkFrame(self.monthly_summary_frame)
            stats_frame.pack(pady=(0, 15), padx=20)
            
            # Sales (Green)
            sales_frame = ctk.CTkFrame(stats_frame)
            sales_frame.pack(side="left", padx=20, pady=15)
            
            ctk.CTkLabel(
                sales_frame,
                text="💰 Monthly Sales",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#333333"
            ).pack(pady=(10, 5))
            
            ctk.CTkLabel(
                sales_frame,
                text=f"₹{monthly_sales:,.2f}",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#10B981"
            ).pack(pady=(0, 10))
            
            # Expenses (Red)
            expense_frame = ctk.CTkFrame(stats_frame)
            expense_frame.pack(side="left", padx=20, pady=15)
            
            ctk.CTkLabel(
                expense_frame,
                text="💸 Monthly Expenses",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#333333"
            ).pack(pady=(10, 5))
            
            ctk.CTkLabel(
                expense_frame,
                text=f"₹{monthly_expenses:,.2f}",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#EF4444"
            ).pack(pady=(0, 10))
            
            # Net Profit/Loss
            net_amount = monthly_sales - monthly_expenses
            net_color = "#10B981" if net_amount >= 0 else "#EF4444"
            net_label = "Profit" if net_amount >= 0 else "Loss"
            
            net_frame = ctk.CTkFrame(stats_frame)
            net_frame.pack(side="left", padx=20, pady=15)
            
            ctk.CTkLabel(
                net_frame,
                text=f"📈 Net {net_label}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#333333"
            ).pack(pady=(10, 5))
            
            ctk.CTkLabel(
                net_frame,
                text=f"₹{abs(net_amount):,.2f}",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=net_color
            ).pack(pady=(0, 10))
            
        except Exception as e:
            logger.error(f"Error creating monthly summary: {str(e)}")
            ctk.CTkLabel(
                self.monthly_summary_frame,
                text="Error loading monthly summary",
                text_color="#EF4444"
            ).pack(pady=20)
    
    def generate_attendance_reports(self):
        """Generate/refresh attendance reports with latest data"""
        try:
            # Update status
            self.show_status_message("Refreshing attendance data...", "info")
            
            # Refresh employee dropdown with latest data
            self.refresh_employee_dropdown()
            
            # If no employee is selected, auto-select the first one
            if not self.selected_employee and self.employee_var.get() and self.employee_var.get() != "No employees found":
                self.on_employee_selected(self.employee_var.get())
            
            # Refresh the calendar and statistics
            self.refresh_calendar()
            
            self.show_status_message("Attendance report refreshed successfully", "success")
            
        except Exception as e:
            self.show_status_message(f"Error refreshing attendance report: {str(e)}", "error")
    
    def refresh_employee_dropdown(self):
        """Refresh the employee dropdown with latest data"""
        try:
            # Get latest employee list
            updated_employee_list = self.get_employee_list()
            
            # Update the dropdown values
            self.employee_dropdown.configure(values=updated_employee_list)
            
            # If no employee is selected or current selection is invalid, select first employee
            current_selection = self.employee_var.get()
            if not current_selection or current_selection not in updated_employee_list:
                if updated_employee_list:
                    self.employee_var.set(updated_employee_list[0])
                    self.employee_dropdown.set(updated_employee_list[0])
                
        except Exception as e:
            print(f"Error refreshing employee dropdown: {e}")
    
    def on_tab_changed(self):
        """Handle tab change events"""
        try:
            current_tab = self.tabview.get()
            if current_tab == "📅 Attendance Calendar":
                # Auto-refresh attendance data when tab is accessed
                self.refresh_employee_dropdown()
        except Exception as e:
            print(f"Error handling tab change: {e}")
    
    def check_tab_changes(self):
        """Periodically check for tab changes"""
        try:
            current_tab = self.tabview.get()
            if current_tab != self.last_tab:
                self.last_tab = current_tab
                if current_tab == "📅 Attendance Calendar":
                    self.refresh_employee_dropdown()
            
            # Schedule next check
            self.parent.after(1000, self.check_tab_changes)  # Check every second
        except Exception as e:
            print(f"Error checking tab changes: {e}")
            # Schedule next check even if there's an error
            self.parent.after(1000, self.check_tab_changes)
    
    def create_chart_section(self, parent, title, chart_function, height=350):
        """Create a chart section with proper spacing"""
        # Section container
        section_frame = ctk.CTkFrame(parent, corner_radius=10)
        section_frame.pack(fill="x", padx=15, pady=15)
        
        # Title
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Chart container
        chart_container = ctk.CTkFrame(section_frame, height=height, corner_radius=8)
        chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create chart
        chart_function(chart_container)
    
    def create_disabled_chart(self, parent):
        """Disabled chart - does nothing"""
        pass
    
    def create_chart_section_with_controls(self, parent, title, chart_function, control_type, height=350):
        """Create a chart section with controls above it"""
        # Section container
        section_frame = ctk.CTkFrame(parent, corner_radius=10)
        section_frame.pack(fill="x", padx=15, pady=15)
        
        # Title
        title_label = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Controls container
        controls_frame = ctk.CTkFrame(section_frame, corner_radius=8)
        controls_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Add specific controls based on type
        if control_type == "daily_sales":
            self.create_daily_sales_controls(controls_frame)
        elif control_type == "daily_transactions":
            self.create_daily_transactions_controls(controls_frame)
        elif control_type == "monthly_histogram":
            self.create_monthly_histogram_controls(controls_frame)
        
        # Chart container
        chart_container = ctk.CTkFrame(section_frame, height=height, corner_radius=8)
        chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create chart
        chart_function(chart_container)
    
    def create_daily_sales_controls(self, parent):
        """Create controls for daily sales chart"""
        ctk.CTkLabel(
            parent, 
            text="Select Month/Year:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(10, 5))
        
        controls_container = ctk.CTkFrame(parent)
        controls_container.pack(pady=(0, 10))
        
        # Month dropdown
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        month_dropdown = ctk.CTkComboBox(
            controls_container,
            values=[f"{i} - {month_names[i-1]}" for i in range(1, 13)],
            variable=self.selected_month_var,
            command=self.on_month_changed,
            width=120
        )
        month_dropdown.pack(side="left", padx=(10, 5))
        
        # Year dropdown
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 3, current_year + 2)]
        
        year_dropdown = ctk.CTkComboBox(
            controls_container,
            values=years,
            variable=self.daily_year_var,
            command=self.on_daily_year_changed,
            width=100
        )
        year_dropdown.pack(side="left", padx=(5, 10))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            controls_container,
            text="🔄 Refresh",
            command=self.generate_financial_reports,
            width=80,
            height=28
        )
        refresh_btn.pack(side="left", padx=(5, 10))
    
    def create_daily_transactions_controls(self, parent):
        """Create controls for daily transactions chart"""
        ctk.CTkLabel(
            parent, 
            text="Select Date:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(10, 5))
        
        controls_container = ctk.CTkFrame(parent)
        controls_container.pack(pady=(0, 10))
        
        # Date entry
        date_entry = ctk.CTkEntry(
            controls_container,
            textvariable=self.selected_date_var,
            placeholder_text="YYYY-MM-DD",
            width=150
        )
        date_entry.pack(side="left", padx=(10, 5))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            controls_container,
            text="🔄 Refresh",
            command=self.generate_financial_reports,
            width=80,
            height=28
        )
        refresh_btn.pack(side="left", padx=(5, 10))
    
    def create_monthly_histogram_controls(self, parent):
        """Create controls for monthly expense vs sales histogram"""
        ctk.CTkLabel(
            parent, 
            text="Select Year:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(10, 5))
        
        controls_container = ctk.CTkFrame(parent)
        controls_container.pack(pady=(0, 10))
        
        # Year dropdown
        current_year = datetime.now().year
        years = [str(year) for year in range(current_year - 3, current_year + 2)]
        
        year_dropdown = ctk.CTkComboBox(
            controls_container,
            values=years,
            variable=self.selected_year_var,
            command=self.on_histogram_year_changed,
            width=100
        )
        year_dropdown.pack(side="left", padx=(10, 5))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            controls_container,
            text="🔄 Refresh",
            command=self.generate_financial_reports,
            width=80,
            height=28
        )
        refresh_btn.pack(side="left", padx=(5, 10))
    
    def create_department_chart(self, parent):
        """Create department distribution chart"""
        try:
            employees_df = self.data_service.get_employees()
            if employees_df.empty:
                self.show_no_data_message(parent, "No employee data available")
                return
            
            # Create figure with better styling
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Department distribution
            dept_counts = employees_df['department'].value_counts()
            
            # Create pie chart with custom colors
            colors = plt.cm.Set3(np.linspace(0, 1, len(dept_counts)))
            wedges, texts, autotexts = ax.pie(
                dept_counts.values,
                labels=dept_counts.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors,
                textprops={'fontsize': 11, 'weight': 'bold'}
            )
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Employee Distribution by Department', 
                        fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating department chart: {str(e)}")
    
    def create_daily_wage_chart(self, parent):
        """Create daily wage analysis chart"""
        try:
            employees_df = self.data_service.get_employees()
            if employees_df.empty:
                self.show_no_data_message(parent, "No employee data available")
                return
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            fig.patch.set_facecolor('white')
            
            # Daily wage by department
            dept_daily_wage = employees_df.groupby('department')['daily_wage'].mean()
            bars1 = ax1.bar(dept_daily_wage.index, dept_daily_wage.values, 
                           color=self.colors['primary'], alpha=0.7)
            ax1.set_title('Average Daily Wage by Department', fontweight='bold')
            ax1.set_ylabel('Average Daily Wage (₹)')
            ax1.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'₹{height:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            # Employee count by position (pie chart)
            position_counts = employees_df['position'].value_counts()
            colors = [self.colors['success'], self.colors['warning'], self.colors['danger'], 
                     self.colors['info'], '#FF6B6B', '#4ECDC4', '#45B7D1']
            
            wedges, texts, autotexts = ax2.pie(position_counts.values, labels=position_counts.index, 
                                              autopct='%1.1f%%', startangle=90, 
                                              colors=colors[:len(position_counts)])
            ax2.set_title('Employee Distribution by Position', fontweight='bold')
            
            # Enhance pie chart text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating daily wage chart: {str(e)}")
    
    def create_employee_overview_chart(self, parent):
        """Create monthly attendance statistics report"""
        try:
            employees_df = self.data_service.get_employees()
            attendance_df = self.data_service.get_attendance()
            
            if employees_df.empty:
                self.show_no_data_message(parent, "No employee data available")
                return
                
            # Create main frame for attendance statistics
            stats_frame = ctk.CTkFrame(parent)
            stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title
            title_label = ctk.CTkLabel(
                stats_frame, 
                text="📊 Monthly Attendance Statistics", 
                font=("Arial", 18, "bold"),
                text_color="#2E86AB"
            )
            title_label.pack(pady=(15, 20))
            
            # Create scrollable frame for stats
            scroll_frame = ctk.CTkScrollableFrame(stats_frame, height=300)
            scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
            # Get current month and year
            from datetime import datetime
            current_date = datetime.now()
            current_month = current_date.month
            current_year = current_date.year
            current_month_name = current_date.strftime("%B %Y")
            
            if attendance_df.empty:
                # Show message when no attendance data
                no_data_frame = ctk.CTkFrame(scroll_frame)
                no_data_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(
                    no_data_frame,
                    text="📋 No attendance data available for analysis",
                    font=("Arial", 14),
                    text_color="#666666"
                ).pack(pady=20)
                return
            
            # Filter attendance for current month
            attendance_df['date'] = pd.to_datetime(attendance_df['date'])
            current_month_attendance = attendance_df[
                (attendance_df['date'].dt.month == current_month) & 
                (attendance_df['date'].dt.year == current_year)
            ]
            
            # Calculate attendance statistics
            if current_month_attendance.empty:
                # Show message for no current month data
                no_data_frame = ctk.CTkFrame(scroll_frame)
                no_data_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(
                    no_data_frame,
                    text=f"📋 No attendance data available for {current_month_name}",
                    font=("Arial", 14),
                    text_color="#666666"
                ).pack(pady=20)
                return
            
            # Calculate monthly statistics
            monthly_stats = current_month_attendance.groupby('employee_id').agg({
                'status': lambda x: ((x == 'Present') | (x == 'Overtime')).sum(),
                'date': 'count'
            }).rename(columns={'status': 'present_days', 'date': 'total_days'})
            
            monthly_stats['attendance_rate'] = (monthly_stats['present_days'] / monthly_stats['total_days']) * 100
            
            # Get employee details for top performers
            top_attendance_stats = []
            if not monthly_stats.empty:
                # Sort by attendance rate
                sorted_stats = monthly_stats.sort_values('attendance_rate', ascending=False)
                
                for emp_id in sorted_stats.head(3).index:  # Top 3
                    emp_info = employees_df[employees_df['employee_id'] == emp_id]
                    if not emp_info.empty:
                        emp_data = emp_info.iloc[0]
                        stats = sorted_stats.loc[emp_id]
                        top_attendance_stats.append({
                            'name': emp_data['name'],
                            'department': emp_data['department'],
                            'position': emp_data['position'],
                            'present_days': int(stats['present_days']),
                            'total_days': int(stats['total_days']),
                            'attendance_rate': stats['attendance_rate']
                        })
            
            # Overall monthly statistics
            total_working_days = current_month_attendance['date'].nunique()
            total_present = len(current_month_attendance[
                (current_month_attendance['status'] == 'Present') |
                (current_month_attendance['status'] == 'Late') |
                (current_month_attendance['status'] == 'Remote Work') |
                (current_month_attendance['status'] == 'Half Day')
            ])
            total_absent = len(current_month_attendance[current_month_attendance['status'] == 'Absent'])
            total_records = len(current_month_attendance)
            overall_attendance_rate = (total_present / total_records) * 100 if total_records > 0 else 0
            
            # Create statistics display
            stats_sections = [
                (f"📅 {current_month_name} Overview", "#2E86AB", [
                    f"Total Working Days Recorded: {total_working_days}",
                    f"Total Present Records: {total_present}",
                    f"Total Absent Records: {total_absent}",
                    f"Overall Attendance Rate: {overall_attendance_rate:.1f}%",
                    f"Active Employees This Month: {len(monthly_stats)}"
                ])
            ]
            
            # Add top performers if available
            if top_attendance_stats:
                rank_colors = ["#F18F01", "#A7C957", "#C73E1D"]  # Gold, Green, Red
                rank_emojis = ["🥇", "🥈", "🥉"]
                
                for i, emp_stat in enumerate(top_attendance_stats):
                    rank = i + 1
                    color = rank_colors[i] if i < len(rank_colors) else "#666666"
                    emoji = rank_emojis[i] if i < len(rank_emojis) else "🏅"
                    
                    stats_sections.append((
                        f"{emoji} #{rank} Best Attendance - {emp_stat['name']}", color, [
                            f"Department: {emp_stat['department']}",
                            f"Position: {emp_stat['position']}",
                            f"Present Days: {emp_stat['present_days']} out of {emp_stat['total_days']}",
                            f"Attendance Rate: {emp_stat['attendance_rate']:.1f}%"
                        ]
                    ))
            
            # Display all statistics
            for section_title, color, items in stats_sections:
                # Section header
                section_frame = ctk.CTkFrame(scroll_frame)
                section_frame.pack(fill="x", padx=10, pady=(10, 5))
                
                header_label = ctk.CTkLabel(
                    section_frame,
                    text=section_title,
                    font=("Arial", 16, "bold"),
                    text_color=color
                )
                header_label.pack(pady=(10, 5))
                
                # Section content
                for item in items:
                    item_label = ctk.CTkLabel(
                        section_frame,
                        text=f"• {item}",
                        font=("Arial", 12),
                        text_color="#333333",
                        anchor="w"
                    )
                    item_label.pack(anchor="w", padx=20, pady=2)
                
                # Add spacing
                ctk.CTkLabel(section_frame, text="", height=5).pack()
                
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating attendance statistics: {str(e)}")
    
    def create_employee_stats_report(self, parent):
        """Create employee statistics report showing top performers and key metrics"""
        try:
            employees_df = self.data_service.get_employees()
            attendance_df = self.data_service.get_attendance()
            
            if employees_df.empty:
                self.show_no_data_message(parent, "No employee data available")
                return
                
            # Create main frame for statistics
            stats_frame = ctk.CTkFrame(parent)
            stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title
            title_label = ctk.CTkLabel(
                stats_frame, 
                text="🏆 Employee Performance Statistics", 
                font=("Arial", 18, "bold"),
                text_color="#2E86AB"
            )
            title_label.pack(pady=(15, 20))
            
            # Create scrollable frame for stats
            scroll_frame = ctk.CTkScrollableFrame(stats_frame, height=300)
            scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
            # Basic statistics
            total_employees = len(employees_df)
            avg_daily_wage = employees_df['daily_wage'].mean()
            total_daily_wage_budget = employees_df['daily_wage'].sum()
            
            # Find highest daily wage employee
            highest_daily_wage_emp = employees_df.loc[employees_df['daily_wage'].idxmax()]
            
            # Calculate attendance statistics if available
            attendance_stats = {}
            if not attendance_df.empty:
                # Group by employee_id and calculate attendance rate
                emp_attendance = attendance_df.groupby('employee_id').agg({
                    'status': lambda x: ((x == 'Present') | (x == 'Overtime')).sum(),
                    'date': 'count'
                }).rename(columns={'status': 'present_days', 'date': 'total_days'})
                
                emp_attendance['attendance_rate'] = (emp_attendance['present_days'] / emp_attendance['total_days']) * 100
                
                if not emp_attendance.empty:
                    best_attendance_id = emp_attendance['attendance_rate'].idxmax()
                    best_attendance_rate = emp_attendance.loc[best_attendance_id, 'attendance_rate']
                    
                    # Find employee details
                    best_attendance_emp = employees_df[employees_df['employee_id'] == best_attendance_id]
                    if not best_attendance_emp.empty:
                        attendance_stats = {
                            'name': best_attendance_emp.iloc[0]['name'],
                            'rate': best_attendance_rate,
                            'department': best_attendance_emp.iloc[0]['department']
                        }
            
            # Department analysis
            dept_counts = employees_df['department'].value_counts()
            largest_dept = dept_counts.index[0] if not dept_counts.empty else "N/A"
            largest_dept_count = dept_counts.iloc[0] if not dept_counts.empty else 0
            
            # Position analysis
            position_counts = employees_df['position'].value_counts()
            most_common_position = position_counts.index[0] if not position_counts.empty else "N/A"
            
            # Create statistics display
            stats_data = [
                ("📊 Overall Statistics", "#2E86AB", [
                    f"Total Employees: {total_employees}",
                    f"Average Daily Wage: ₹{avg_daily_wage:,.2f}",
                    f"Total Daily Wage Budget: ₹{total_daily_wage_budget:,.2f}",
                    f"Largest Department: {largest_dept} ({largest_dept_count} employees)",
                    f"Most Common Position: {most_common_position}"
                ]),
                
                
                ("�💰 Highest Daily Wage Employee", "#F18F01", [
                    f"Name: {highest_daily_wage_emp['name']}",
                    f"Daily Wage: ₹{highest_daily_wage_emp['daily_wage']:,.2f}",
                    f"Department: {highest_daily_wage_emp['department']}",
                    f"Position: {highest_daily_wage_emp['position']}",
                    f"Employee ID: {highest_daily_wage_emp['employee_id']}"
                ])
            ]
            
            # Add attendance statistics if available
            if attendance_stats:
                stats_data.append((
                    "🎯 Best Attendance Record", "#A7C957", [
                        f"Name: {attendance_stats['name']}",
                        f"Attendance Rate: {attendance_stats['rate']:.1f}%",
                        f"Department: {attendance_stats['department']}"
                    ]
                ))
            
            # Daily wage distribution analysis
            daily_wage_ranges = {
                "₹0 - ₹200": len(employees_df[employees_df['daily_wage'] <= 200]),
                "₹201 - ₹500": len(employees_df[(employees_df['daily_wage'] > 200) & (employees_df['daily_wage'] <= 500)]),
                "₹501 - ₹800": len(employees_df[(employees_df['daily_wage'] > 500) & (employees_df['daily_wage'] <= 800)]),
                "₹801+": len(employees_df[employees_df['daily_wage'] > 800])
            }
            
            stats_data.append((
                "💵 Daily Wage Distribution", "#C73E1D", [
                    f"{range_name}: {count} employees" 
                    for range_name, count in daily_wage_ranges.items() if count > 0
                ]
            ))
            
            # Display all statistics
            for section_title, color, items in stats_data:
                # Section header
                section_frame = ctk.CTkFrame(scroll_frame)
                section_frame.pack(fill="x", padx=10, pady=(10, 5))
                
                header_label = ctk.CTkLabel(
                    section_frame,
                    text=section_title,
                    font=("Arial", 16, "bold"),
                    text_color=color
                )
                header_label.pack(pady=(10, 5))
                
                # Section content
                for item in items:
                    item_label = ctk.CTkLabel(
                        section_frame,
                        text=f"• {item}",
                        font=("Arial", 12),
                        text_color="#333333",
                        anchor="w"
                    )
                    item_label.pack(anchor="w", padx=20, pady=2)
                
                # Add spacing
                ctk.CTkLabel(section_frame, text="", height=5).pack()
                
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating employee statistics: {str(e)}")
    
    def create_monthly_revenue_expense_chart(self, parent):
        """Create monthly revenue vs expenses chart for selected year"""
        try:
            selected_year = int(self.selected_year_var.get())
            
            # Get data using correct method names
            orders_data = self.data_service.get_all_orders()
            purchases_df = self.data_service.get_purchases()
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Prepare monthly data
            months = list(range(1, 13))
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            monthly_sales = []
            monthly_expenses = []
            
            for month in months:
                # Calculate sales for this month from orders
                sales_amount = 0
                if orders_data:
                    for order in orders_data:
                        try:
                            order_date = pd.to_datetime(order.get('created_date', order.get('date', '')))
                            if (order_date.month == month and 
                                order_date.year == selected_year):
                                sales_amount += float(order.get('total_amount', 0))
                        except:
                            continue
                
                # Calculate expenses for this month from purchases
                expense_amount = 0
                if not purchases_df.empty:
                    purchases_df['date'] = pd.to_datetime(purchases_df['date'])
                    month_purchases = purchases_df[
                        (purchases_df['date'].dt.month == month) & 
                        (purchases_df['date'].dt.year == selected_year)
                    ]
                    expense_amount = month_purchases['total_price'].sum()
                
                monthly_sales.append(sales_amount)
                monthly_expenses.append(expense_amount)
            
            # Create bar chart
            x = np.arange(len(month_names))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, monthly_sales, width, label='Sales', 
                          color='#10B981', alpha=0.8)
            bars2 = ax.bar(x + width/2, monthly_expenses, width, label='Expenses', 
                          color='#EF4444', alpha=0.8)
            
            # Customize chart
            ax.set_xlabel('Month', fontweight='bold')
            ax.set_ylabel('Amount (₹)', fontweight='bold')
            ax.set_title(f'Monthly Revenue vs Expenses - {selected_year}', 
                        fontweight='bold', fontsize=16)
            ax.set_xticks(x)
            ax.set_xticklabels(month_names)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            def add_value_labels(bars):
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'₹{height:,.0f}', ha='center', va='bottom', 
                               fontsize=8, rotation=45)
            
            add_value_labels(bars1)
            add_value_labels(bars2)
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            logger.error(f"Error creating monthly revenue expense chart: {str(e)}")
            self.show_no_data_message(parent, f"Error creating chart: {str(e)}")
    
    def create_monthly_expense_vs_sales_histogram(self, parent):
        """Create monthly expense vs sales histogram for the selected year"""
        try:
            selected_year = int(self.selected_year_var.get())
            
            # Get data using correct method names
            orders_data = self.data_service.get_all_orders()
            purchases_df = self.data_service.get_purchases()
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Prepare monthly data
            months = list(range(1, 13))
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            monthly_sales = []
            monthly_expenses = []
            
            for month in months:
                # Calculate sales for this month from orders
                sales_amount = 0
                if orders_data:
                    for order in orders_data:
                        try:
                            order_date = pd.to_datetime(order.get('created_date', order.get('date', '')))
                            if (order_date.month == month and 
                                order_date.year == selected_year):
                                sales_amount += float(order.get('total_amount', 0))
                        except:
                            continue
                
                # Calculate expenses for this month from purchases
                expense_amount = 0
                if not purchases_df.empty:
                    purchases_df['date'] = pd.to_datetime(purchases_df['date'])
                    month_purchases = purchases_df[
                        (purchases_df['date'].dt.month == month) & 
                        (purchases_df['date'].dt.year == selected_year)
                    ]
                    expense_amount = month_purchases['total_price'].sum()
                
                monthly_sales.append(sales_amount)
                monthly_expenses.append(expense_amount)
            
            # Create grouped bar chart (histogram style)
            x = np.arange(len(month_names))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, monthly_sales, width, label='Sales', 
                          color='#10B981', alpha=0.8, edgecolor='white', linewidth=1)
            bars2 = ax.bar(x + width/2, monthly_expenses, width, label='Expenses', 
                          color='#EF4444', alpha=0.8, edgecolor='white', linewidth=1)
            
            # Customize the chart
            ax.set_xlabel('Month', fontsize=12, fontweight='bold')
            ax.set_ylabel('Amount (₹)', fontsize=12, fontweight='bold')
            ax.set_title(f'Monthly Sales vs Expenses - {selected_year}', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xticks(x)
            ax.set_xticklabels(month_names)
            ax.legend(fontsize=12)
            
            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
            
            # Add value labels on bars
            def add_value_labels(bars):
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + max(monthly_sales + monthly_expenses) * 0.01,
                               f'₹{height:,.0f}',
                               ha='center', va='bottom', fontsize=9, rotation=45)
            
            add_value_labels(bars1)
            add_value_labels(bars2)
            
            # Improve layout
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            # Calculate totals for summary
            total_sales = sum(monthly_sales)
            total_expenses = sum(monthly_expenses)
            net_profit = total_sales - total_expenses
            
            # Add summary text
            summary_text = f'Total Sales: ₹{total_sales:,.2f} | Total Expenses: ₹{total_expenses:,.2f} | Net: ₹{net_profit:,.2f}'
            fig.suptitle(summary_text, fontsize=12, y=0.02, color='#666666')
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            logger.error(f"Error creating monthly expense vs sales histogram: {str(e)}")
            self.show_no_data_message(parent, f"Error creating histogram: {str(e)}")

    def create_daily_sales_chart(self, parent):
        """Create daily sales trend chart for selected month/year"""
        try:
            selected_month = int(self.selected_month_var.get())
            selected_year = int(self.daily_year_var.get())
            
            # Get orders data
            orders_data = self.data_service.get_all_orders()
            
            if not orders_data:
                self.show_no_data_message(parent, "No sales data available")
                return
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Process orders for selected month/year
            daily_sales_dict = {}
            for order in orders_data:
                try:
                    order_date = pd.to_datetime(order.get('created_date', order.get('date', '')))
                    if (order_date.month == selected_month and 
                        order_date.year == selected_year):
                        date_key = order_date.date()
                        if date_key not in daily_sales_dict:
                            daily_sales_dict[date_key] = 0
                        daily_sales_dict[date_key] += float(order.get('total_amount', 0))
                except:
                    continue
            
            if not daily_sales_dict:
                self.show_no_data_message(parent, f"No sales data for {selected_month}/{selected_year}")
                return
            
            # Create complete date range for the month
            from calendar import monthrange
            _, last_day = monthrange(selected_year, selected_month)
            date_range = pd.date_range(
                start=f'{selected_year}-{selected_month:02d}-01',
                end=f'{selected_year}-{selected_month:02d}-{last_day:02d}',
                freq='D'
            )
            
            # Create series with all days (fill missing with 0)
            daily_values = []
            daily_dates = []
            for date in date_range:
                daily_dates.append(date.date())
                daily_values.append(daily_sales_dict.get(date.date(), 0))
            
            # Plot line chart
            ax.plot(daily_dates, daily_values, marker='o', 
                   linewidth=2, markersize=4, color='#3B82F6')
            ax.fill_between(daily_dates, daily_values, alpha=0.3, color='#3B82F6')
            
            # Customize chart
            ax.set_xlabel('Date', fontweight='bold')
            ax.set_ylabel('Sales Amount (₹)', fontweight='bold')
            ax.set_title(f'Daily Sales Trend - {datetime(selected_year, selected_month, 1).strftime("%B %Y")}', 
                        fontweight='bold', fontsize=16)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis dates
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            # Add statistics
            total_sales = sum(daily_values)
            avg_sales = total_sales / len(daily_values) if daily_values else 0
            max_sales = max(daily_values) if daily_values else 0
            
            stats_text = f'Total: ₹{total_sales:,.0f} | Avg: ₹{avg_sales:,.0f} | Peak: ₹{max_sales:,.0f}'
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            logger.error(f"Error creating daily sales chart: {str(e)}")
            self.show_no_data_message(parent, f"Error creating chart: {str(e)}")
    
    def create_daily_transactions_chart(self, parent):
        """Create daily transactions chart for selected date"""
        try:
            selected_date = self.selected_date_var.get()
            
            # Get data using available methods
            transactions_data = self.data_service.get_all_transactions_with_orders()
            purchases_df = self.data_service.get_purchases()
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Filter transactions for selected date
            transaction_amounts = {}
            purchase_data = {}
            
            # Process transactions
            if transactions_data:
                for transaction in transactions_data:
                    try:
                        trans_date = pd.to_datetime(transaction.get('created_date', transaction.get('date', ''))).date()
                        if trans_date == pd.to_datetime(selected_date).date():
                            trans_type = transaction.get('transaction_type', 'Unknown')
                            amount = float(transaction.get('amount', 0))
                            if trans_type not in transaction_amounts:
                                transaction_amounts[trans_type] = 0
                            transaction_amounts[trans_type] += amount
                    except:
                        continue
            
            # Process purchases
            if not purchases_df.empty:
                purchases_df['date'] = pd.to_datetime(purchases_df['date']).dt.date
                daily_purchases = purchases_df[
                    purchases_df['date'] == pd.to_datetime(selected_date).date()
                ]
                if not daily_purchases.empty:
                    purchase_data = daily_purchases.groupby('supplier')['total_price'].sum().to_dict()
            
            # Transactions pie chart
            if transaction_amounts:
                colors1 = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']
                ax1.pie(transaction_amounts.values(), labels=transaction_amounts.keys(), autopct='%1.1f%%',
                       colors=colors1[:len(transaction_amounts)], startangle=90)
                ax1.set_title(f'Transactions by Type\n{selected_date}', fontweight='bold')
            else:
                ax1.text(0.5, 0.5, 'No transactions\nfor this date', 
                        ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title(f'Transactions\n{selected_date}', fontweight='bold')
            
            # Purchases bar chart
            if purchase_data:
                suppliers = list(purchase_data.keys())
                amounts = list(purchase_data.values())
                bars = ax2.bar(range(len(suppliers)), amounts, 
                              color='#EF4444', alpha=0.7)
                ax2.set_xlabel('Suppliers')
                ax2.set_ylabel('Amount (₹)')
                ax2.set_title(f'Purchases by Supplier\n{selected_date}', fontweight='bold')
                ax2.set_xticks(range(len(suppliers)))
                ax2.set_xticklabels(suppliers, rotation=45, ha='right')
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                           f'₹{height:,.0f}', ha='center', va='bottom', fontsize=8)
            else:
                ax2.text(0.5, 0.5, 'No purchases\nfor this date', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title(f'Purchases\n{selected_date}', fontweight='bold')
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            logger.error(f"Error creating daily transactions chart: {str(e)}")
            self.show_no_data_message(parent, f"Error creating chart: {str(e)}")
    
    def create_top_customers_chart(self, parent):
        """Create top customer spenders chart"""
        try:
            # Get orders data
            orders_data = self.data_service.get_all_orders()
            
            if not orders_data:
                self.show_no_data_message(parent, "No customer data available")
                return
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Group by customer and sum total amounts
            customer_spending = {}
            for order in orders_data:
                try:
                    customer_name = order.get('customer_name', 'Unknown')
                    amount = float(order.get('total_amount', 0))
                    if customer_name not in customer_spending:
                        customer_spending[customer_name] = 0
                    customer_spending[customer_name] += amount
                except:
                    continue
            
            if not customer_spending:
                self.show_no_data_message(parent, "No customer spending data available")
                return
            
            # Get top 10 customers
            sorted_customers = sorted(customer_spending.items(), key=lambda x: x[1], reverse=True)[:10]
            customer_names = [item[0] for item in sorted_customers]
            spending_amounts = [item[1] for item in sorted_customers]
            
            # Create horizontal bar chart
            bars = ax.barh(range(len(customer_names)), spending_amounts, 
                          color='#3B82F6', alpha=0.8)
            
            # Customize chart
            ax.set_xlabel('Total Spent (₹)', fontweight='bold')
            ax.set_ylabel('Customers', fontweight='bold')
            ax.set_title('Top Customer Spenders', fontweight='bold', fontsize=16)
            ax.set_yticks(range(len(customer_names)))
            ax.set_yticklabels(customer_names)
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + max(spending_amounts) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'₹{width:,.0f}', ha='left', va='center', fontweight='bold')
            
            # Add statistics
            total_revenue = sum(spending_amounts)
            avg_spending = total_revenue / len(spending_amounts) if spending_amounts else 0
            stats_text = f'Total from Top 10: ₹{total_revenue:,.0f} | Average: ₹{avg_spending:,.0f}'
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            logger.error(f"Error creating top customers chart: {str(e)}")
            self.show_no_data_message(parent, f"Error creating chart: {str(e)}")
    
    def create_dues_analysis_chart(self, parent):
        """Create outstanding dues analysis chart"""
        try:
            # Get orders data
            orders_data = self.data_service.get_all_orders()
            
            if not orders_data:
                self.show_no_data_message(parent, "No dues data available")
                return
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Calculate dues
            customer_dues = {}
            total_amount = 0
            total_paid = 0
            
            for order in orders_data:
                try:
                    customer_name = order.get('customer_name', 'Unknown')
                    order_total = float(order.get('total_amount', 0))
                    paid_amount = float(order.get('paid_amount', order_total * 0.8))  # Assume 80% paid if not specified
                    due_amount = order_total - paid_amount
                    
                    total_amount += order_total
                    total_paid += paid_amount
                    
                    if due_amount > 0:
                        if customer_name not in customer_dues:
                            customer_dues[customer_name] = 0
                        customer_dues[customer_name] += due_amount
                except:
                    continue
            
            total_dues = total_amount - total_paid
            
            # Chart 1: Total dues by customer
            if customer_dues:
                sorted_dues = sorted(customer_dues.items(), key=lambda x: x[1], reverse=True)[:8]
                customer_names = [item[0] for item in sorted_dues]
                due_amounts = [item[1] for item in sorted_dues]
                
                bars1 = ax1.bar(range(len(customer_names)), due_amounts, 
                               color='#EF4444', alpha=0.8)
                ax1.set_xlabel('Customers', fontweight='bold')
                ax1.set_ylabel('Outstanding Dues (₹)', fontweight='bold')
                ax1.set_title('Top Customers with Outstanding Dues', fontweight='bold')
                ax1.set_xticks(range(len(customer_names)))
                ax1.set_xticklabels(customer_names, rotation=45, ha='right')
                ax1.grid(True, alpha=0.3, axis='y')
                
                # Add value labels
                for bar in bars1:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'₹{height:,.0f}', ha='center', va='bottom', fontsize=8)
            else:
                ax1.text(0.5, 0.5, 'No outstanding dues', 
                        ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Outstanding Dues by Customer', fontweight='bold')
            
            # Chart 2: Dues distribution pie chart
            dues_distribution = [total_paid, total_dues] if total_dues > 0 else [total_paid]
            labels = ['Paid', 'Outstanding'] if total_dues > 0 else ['Paid']
            colors = ['#10B981', '#EF4444'] if total_dues > 0 else ['#10B981']
            
            ax2.pie(dues_distribution, labels=labels, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax2.set_title('Payment Status Distribution', fontweight='bold')
            
            # Add summary text
            summary_text = f'Total Outstanding: ₹{total_dues:,.0f}\nTotal Paid: ₹{total_paid:,.0f}'
            ax2.text(0.02, 0.02, summary_text, transform=ax2.transAxes, 
                    verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            logger.error(f"Error creating dues analysis chart: {str(e)}")
            self.show_no_data_message(parent, f"Error creating chart: {str(e)}")
            self.show_no_data_message(parent, f"Error creating financial chart: {str(e)}")
    
    def show_no_data_message(self, parent, message):
        """Show no data message"""
        # Clear parent
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Create message
        message_label = ctk.CTkLabel(
            parent,
            text=message,
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        message_label.pack(expand=True, pady=50)
    
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
            text="📊",
            font=ctk.CTkFont(size=16)
        )
        self.status_icon.pack(side="left", padx=(0, 10))
        
        # Status message
        self.status_label = ctk.CTkLabel(
            status_container,
            text="Ready - Generate comprehensive reports and analytics",
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
        """Show enhanced status message with icon and timestamp - robust version"""
        try:
            # Check if status bar is initialized
            if hasattr(self, 'status_icon') and self.status_icon:
                icons = {
                    "success": "✅",
                    "error": "❌", 
                    "warning": "⚠️",
                    "info": "ℹ️"
                }
                
                # Update components
                self.status_icon.configure(text=icons.get(message_type, "📊"))
                self.status_label.configure(text=message)
                
                # Add timestamp
                from datetime import datetime
                current_time = datetime.now().strftime("%H:%M:%S")
                self.status_time.configure(text=current_time)
                
                # Clear message after 5 seconds
                self.frame.after(5000, lambda: self.reset_status())
            else:
                # Just log the message since status bar isn't ready
                if message_type == "error":
                    logger.error(message)
                else:
                    logger.info(message)
        except Exception as e:
            logger.error(f"Error showing status message: {str(e)}")
        
    def reset_status(self):
        """Reset status to default - robust version"""
        try:
            if hasattr(self, 'status_icon') and self.status_icon:
                self.status_icon.configure(text="📊")
                self.status_label.configure(text="Ready - Generate comprehensive reports and analytics")
                self.status_time.configure(text="")
        except Exception as e:
            logger.error(f"Error resetting status: {str(e)}")
    
    def refresh_all_reports(self):
        """Refresh all report data"""
        try:
            # Reload employee list
            self.employee_dropdown.configure(values=self.get_employee_list())
            
            # Refresh calendar if employee is selected
            if self.selected_employee:
                self.create_attendance_calendar()
                self.create_attendance_stats()
            
            self.show_status_message("All reports refreshed successfully", "success")
            
        except Exception as e:
            self.show_status_message(f"Refresh failed: {str(e)}", "error")
    
    def calculate_hours(self, time_in, time_out):
        """Calculate working hours from time_in and time_out"""
        try:
            if not time_in or not time_out:
                return 0.0
            
            # Convert to string if not already
            time_in_str = str(time_in)
            time_out_str = str(time_out)
            
            from datetime import datetime
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
    
    def get_frame(self):
        """Return the main frame for this page"""
        return self.frame
    
    def show(self):
        """Show this page"""
        if self.frame:
            self.frame.pack(fill="both", expand=True)
    
    def hide(self):
        """Hide this page"""
        if self.frame:
            self.frame.pack_forget()
