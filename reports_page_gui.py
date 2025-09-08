"""
Enhanced Reports and Analytics GUI Page with Calendar and Better Visualizations
Modern interface with attendance calendar and meaningful charts
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
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
        self.tabview.add("👥 Employee Analytics") 
        self.tabview.add("💰 Financial Reports")
        
        # Create tab content
        self.create_attendance_tab()
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
        
    def create_employee_tab(self):
        """Create employee analytics tab"""
        tab_frame = self.tabview.tab("👥 Employee Analytics")
        
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
            ('Overtime', self.attendance_colors['Overtime'], '⏱️'),
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
        """Create attendance statistics"""
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
            # Get attendance data for selected employee
            attendance_df = self.data_service.get_attendance({
                "employee_id": self.selected_employee
            })
            
            # Statistics header
            stats_header = ctk.CTkLabel(
                self.stats_frame,
                text="📊 Attendance Statistics",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            stats_header.pack(pady=(30, 10))
            
            if attendance_df.empty:
                no_data_label = ctk.CTkLabel(
                    self.stats_frame,
                    text="No attendance data found",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                no_data_label.pack(pady=20)
                return
            
            # Calculate statistics
            stats = attendance_df['status'].value_counts()
            total_days = len(attendance_df)
            
            # Statistics container
            stats_container = ctk.CTkFrame(self.stats_frame, corner_radius=8)
            stats_container.pack(fill="x", padx=10, pady=10)
            
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
            
            ctk.CTkLabel(
                total_frame,
                text="Total Days:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=10, pady=5)
            
            ctk.CTkLabel(
                total_frame,
                text=str(total_days),
                font=ctk.CTkFont(size=12)
            ).pack(side="right", padx=10, pady=5)
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.stats_frame,
                text=f"Error loading statistics: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="red"
            )
            error_label.pack(pady=20)
    
    def generate_employee_reports(self):
        """Generate enhanced employee analytics"""
        # Clear previous charts
        for widget in self.employee_charts_frame.winfo_children():
            widget.destroy()
        
        try:
            # Create charts with better spacing
            self.create_chart_section(
                self.employee_charts_frame,
                "👥 Department Distribution",
                self.create_department_chart,
                height=400
            )
            
            self.create_chart_section(
                self.employee_charts_frame,
                "💰 Salary Analysis",
                self.create_salary_chart,
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
            

            self.create_chart_section(
                self.financial_charts_frame,
                "� Monthly Revenue vs Expenses",
                self.create_monthly_revenue_expense_chart,
                height=400
            )
            
            # 1. Daily Sales Trend (Month/Year-based)
            self.create_chart_section_with_controls(
                self.financial_charts_frame,
                "📈 Daily Sales Trend",
                self.create_daily_sales_chart,
                "daily_sales",
                height=400
            )
            
            # 2. Daily Transactions (Date-based)
            self.create_chart_section_with_controls(
                self.financial_charts_frame,
                "💳 Daily Transactions",
                self.create_daily_transactions_chart,
                "daily_transactions",
                height=400
            )
            
            # 3. Top Customer Spenders
            self.create_chart_section(
                self.financial_charts_frame,
                "🏆 Top Customer Spenders",
                self.create_top_customers_chart,
                height=400
            )
            
            # 4. Outstanding Dues Analysis
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
            command=lambda: self.create_daily_sales_chart(parent.master.winfo_children()[-1]),
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
            command=lambda: self.create_daily_transactions_chart(parent.master.winfo_children()[-1]),
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
    
    def create_salary_chart(self, parent):
        """Create salary analysis chart"""
        try:
            employees_df = self.data_service.get_employees()
            if employees_df.empty:
                self.show_no_data_message(parent, "No employee data available")
                return
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            fig.patch.set_facecolor('white')
            
            # Salary by department
            dept_salary = employees_df.groupby('department')['salary'].mean()
            bars1 = ax1.bar(dept_salary.index, dept_salary.values, 
                           color=self.colors['primary'], alpha=0.7)
            ax1.set_title('Average Salary by Department', fontweight='bold')
            ax1.set_ylabel('Average Salary (₹)')
            ax1.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'₹{height:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            # Salary distribution histogram
            ax2.hist(employees_df['salary'], bins=10, color=self.colors['success'], 
                    alpha=0.7, edgecolor='black')
            ax2.set_title('Salary Distribution', fontweight='bold')
            ax2.set_xlabel('Salary (₹)')
            ax2.set_ylabel('Number of Employees')
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating salary chart: {str(e)}")
    
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
                (current_month_attendance['status'] == 'Overtime')
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
            avg_salary = employees_df['salary'].mean()
            total_salary_budget = employees_df['salary'].sum()
            
            # Find highest salary employee
            highest_salary_emp = employees_df.loc[employees_df['salary'].idxmax()]
            
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
                    f"Average Salary: ₹{avg_salary:,.2f}",
                    f"Total Salary Budget: ₹{total_salary_budget:,.2f}",
                    f"Largest Department: {largest_dept} ({largest_dept_count} employees)",
                    f"Most Common Position: {most_common_position}"
                ]),
                
                ("💰 Highest Paid Employee", "#F18F01", [
                    f"Name: {highest_salary_emp['name']}",
                    f"Salary: ₹{highest_salary_emp['salary']:,.2f}",
                    f"Department: {highest_salary_emp['department']}",
                    f"Position: {highest_salary_emp['position']}",
                    f"Email: {highest_salary_emp['email']}"
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
            
            # Salary distribution analysis
            salary_ranges = {
                "₹0 - ₹30,000": len(employees_df[employees_df['salary'] <= 30000]),
                "₹30,001 - ₹50,000": len(employees_df[(employees_df['salary'] > 30000) & (employees_df['salary'] <= 50000)]),
                "₹50,001 - ₹75,000": len(employees_df[(employees_df['salary'] > 50000) & (employees_df['salary'] <= 75000)]),
                "₹75,001+": len(employees_df[employees_df['salary'] > 75000])
            }
            
            stats_data.append((
                "💵 Salary Distribution", "#C73E1D", [
                    f"{range_name}: {count} employees" 
                    for range_name, count in salary_ranges.items() if count > 0
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
        try:
            sales_df = self.data_service.get_sales()
            purchases_df = self.data_service.get_purchases()
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            if sales_df.empty and purchases_df.empty:
                self.show_no_data_message(parent, "No financial data available")
                return
            
            # Calculate monthly totals
            monthly_data = []
            
            if not sales_df.empty:
                sales_df['month'] = pd.to_datetime(sales_df['date']).dt.to_period('M')
                monthly_sales = sales_df.groupby('month')['total_price'].sum()
            else:
                monthly_sales = pd.Series()
            
            if not purchases_df.empty:
                purchases_df['month'] = pd.to_datetime(purchases_df['date']).dt.to_period('M')
                monthly_purchases = purchases_df.groupby('month')['total_price'].sum()
            else:
                monthly_purchases = pd.Series()
            
            # Get all months
            all_months = set()
            if not monthly_sales.empty:
                all_months.update(monthly_sales.index)
            if not monthly_purchases.empty:
                all_months.update(monthly_purchases.index)
            
            if not all_months:
                self.show_no_data_message(parent, "No financial data for charting")
                return
            
            months = sorted(list(all_months))
            sales_values = [monthly_sales.get(month, 0) for month in months]
            purchase_values = [monthly_purchases.get(month, 0) for month in months]
            
            # Create grouped bar chart
            x = np.arange(len(months))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, sales_values, width, label='Revenue', 
                          color=self.colors['success'], alpha=0.8)
            bars2 = ax.bar(x + width/2, purchase_values, width, label='Expenses', 
                          color=self.colors['danger'], alpha=0.8)
            
            ax.set_title('Monthly Revenue vs Expenses', fontweight='bold', fontsize=16)
            ax.set_ylabel('Amount (₹)')
            ax.set_xlabel('Month')
            ax.set_xticks(x)
            ax.set_xticklabels([str(m) for m in months], rotation=45)
            ax.legend()
            
            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                               f'₹{height:,.0f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
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
