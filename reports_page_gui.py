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
        
        # Attendance color mapping
        self.attendance_colors = {
            'Present': '#10B981',      # Green
            'Absent': '#EF4444',       # Red
            'Late': '#F59E0B',         # Orange
            'Half Day': '#84CC16',     # Light Green
            'Leave': '#8B5CF6',        # Purple
            'Overtime': '#06B6D4',     # Cyan
            'Remote Work': '#EC4899',  # Pink
            'Work from Home': '#EC4899'  # Pink (alias)
        }
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8')
        
        self.create_page()
        
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
        
        # Add tabs
        self.tabview.add("📅 Attendance Calendar")
        self.tabview.add("👥 Employee Analytics") 
        self.tabview.add("💰 Financial Reports")
        self.tabview.add("📦 Inventory Dashboard")
        
        # Create tab content
        self.create_attendance_tab()
        self.create_employee_tab()
        self.create_financial_tab()
        self.create_inventory_tab()
        
        # Set default tab
        self.tabview.set("📅 Attendance Calendar")
        
    def create_attendance_tab(self):
        """Create enhanced attendance tab with calendar"""
        tab_frame = self.tabview.tab("📅 Attendance Calendar")
        
        # Create main container with scrollable frame
        main_container = ctk.CTkScrollableFrame(tab_frame, corner_radius=8)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
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
        """Create financial reports tab"""
        tab_frame = self.tabview.tab("💰 Financial Reports")
        
        # Create scrollable container
        container = ctk.CTkScrollableFrame(tab_frame, corner_radius=8)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Generate button
        generate_btn = ctk.CTkButton(
            container,
            text="💰 Generate Financial Reports",
            command=self.generate_financial_reports,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        generate_btn.pack(pady=20)
        
        # Charts container
        self.financial_charts_frame = ctk.CTkFrame(container, corner_radius=8)
        self.financial_charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_inventory_tab(self):
        """Create inventory dashboard tab"""
        tab_frame = self.tabview.tab("📦 Inventory Dashboard")
        
        # Create scrollable container
        container = ctk.CTkScrollableFrame(tab_frame, corner_radius=8)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Generate button
        generate_btn = ctk.CTkButton(
            container,
            text="📦 Generate Inventory Reports",
            command=self.generate_inventory_reports,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        generate_btn.pack(pady=20)
        
        # Charts container
        self.inventory_charts_frame = ctk.CTkFrame(container, corner_radius=8)
        self.inventory_charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
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
                    status = attendance_lookup.get(day_date, "No Data")
                    
                    # Determine cell appearance based on status
                    if status in self.attendance_colors:
                        bg_color = self.attendance_colors[status]
                        text_color = "white"
                        status_emoji = self.get_status_emoji(status)
                    else:
                        bg_color = "#f8f9fa"
                        text_color = "#6b7280"
                        status_emoji = "📅"
                    
                    # Create enhanced day cell
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
        """Get emoji for attendance status"""
        emoji_map = {
            'Present': '✅',
            'Absent': '❌',
            'Late': '⏰',
            'Half Day': '🕐',
            'Leave': '🏖️',
            'Overtime': '⏱️',
            'Remote Work': '🏠',
            'Work from Home': '🏠'
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
        
        # Create legend items with emojis and better layout
        legend_items = [
            ('Present', self.attendance_colors['Present'], '✅'),
            ('Absent', self.attendance_colors['Absent'], '❌'),
            ('Late', self.attendance_colors['Late'], '⏰'),
            ('Half Day', self.attendance_colors['Half Day'], '🕐'),
            ('Leave', self.attendance_colors['Leave'], '🏖️'),
            ('Overtime', self.attendance_colors['Overtime'], '⏱️')
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
                "📊 Employee Overview",
                self.create_employee_overview_chart,
                height=400
            )
            
            self.show_status_message("Employee reports generated successfully", "success")
            
        except Exception as e:
            self.show_status_message(f"Error generating employee reports: {str(e)}", "error")
    
    def generate_financial_reports(self):
        """Generate enhanced financial reports"""
        # Clear previous charts
        for widget in self.financial_charts_frame.winfo_children():
            widget.destroy()
        
        try:
            self.create_chart_section(
                self.financial_charts_frame,
                "💰 Revenue vs Expenses",
                self.create_revenue_expense_chart,
                height=400
            )
            
            self.create_chart_section(
                self.financial_charts_frame,
                "📈 Sales Trends",
                self.create_sales_trends_chart,
                height=400
            )
            
            self.create_chart_section(
                self.financial_charts_frame,
                "🛒 Purchase Analysis",
                self.create_purchase_trends_chart,
                height=400
            )
            
            self.show_status_message("Financial reports generated successfully", "success")
            
        except Exception as e:
            self.show_status_message(f"Error generating financial reports: {str(e)}", "error")
    
    def generate_inventory_reports(self):
        """Generate enhanced inventory reports"""
        # Clear previous charts
        for widget in self.inventory_charts_frame.winfo_children():
            widget.destroy()
        
        try:
            self.create_chart_section(
                self.inventory_charts_frame,
                "📦 Current Stock Levels",
                self.create_stock_levels_chart,
                height=400
            )
            
            self.create_chart_section(
                self.inventory_charts_frame,
                "⚠️ Low Stock Alerts",
                self.create_low_stock_chart,
                height=400
            )
            
            self.create_chart_section(
                self.inventory_charts_frame,
                "📊 Stock Movement",
                self.create_stock_movement_chart,
                height=400
            )
            
            self.show_status_message("Inventory reports generated successfully", "success")
            
        except Exception as e:
            self.show_status_message(f"Error generating inventory reports: {str(e)}", "error")
    
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
        """Create employee overview chart"""
        try:
            employees_df = self.data_service.get_employees()
            if employees_df.empty:
                self.show_no_data_message(parent, "No employee data available")
                return
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Position distribution
            position_counts = employees_df['position'].value_counts()
            
            # Create horizontal bar chart
            bars = ax.barh(position_counts.index, position_counts.values, 
                          color=self.colors['warning'], alpha=0.8)
            
            ax.set_title('Employee Count by Position', fontweight='bold', fontsize=16)
            ax.set_xlabel('Number of Employees')
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{int(width)}', ha='left', va='center', fontweight='bold')
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating employee overview: {str(e)}")
    
    def create_revenue_expense_chart(self, parent):
        """Create revenue vs expense chart"""
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
    
    def create_sales_trends_chart(self, parent):
        """Create sales trends chart"""
        try:
            sales_df = self.data_service.get_sales()
            if sales_df.empty:
                self.show_no_data_message(parent, "No sales data available")
                return
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Daily sales trend
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            daily_sales = sales_df.groupby(sales_df['date'].dt.date)['total_price'].sum()
            
            # Plot line chart
            ax.plot(daily_sales.index, daily_sales.values, 
                   marker='o', linewidth=2, markersize=6, 
                   color=self.colors['primary'])
            
            ax.set_title('Daily Sales Trends', fontweight='bold', fontsize=16)
            ax.set_ylabel('Sales Amount (₹)')
            ax.set_xlabel('Date')
            plt.xticks(rotation=45)
            
            # Add trend line
            z = np.polyfit(range(len(daily_sales)), daily_sales.values, 1)
            p = np.poly1d(z)
            ax.plot(daily_sales.index, p(range(len(daily_sales))), 
                   "r--", alpha=0.8, linewidth=2, label='Trend')
            ax.legend()
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating sales trends: {str(e)}")
    
    def create_purchase_trends_chart(self, parent):
        """Create purchase trends chart"""
        try:
            purchases_df = self.data_service.get_purchases()
            if purchases_df.empty:
                self.show_no_data_message(parent, "No purchase data available")
                return
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Purchase by supplier
            supplier_totals = purchases_df.groupby('supplier')['total_price'].sum().sort_values(ascending=True)
            
            # Create horizontal bar chart
            bars = ax.barh(supplier_totals.index, supplier_totals.values, 
                          color=self.colors['purple'], alpha=0.8)
            
            ax.set_title('Purchase Amount by Supplier', fontweight='bold', fontsize=16)
            ax.set_xlabel('Total Purchase Amount (₹)')
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                       f'₹{width:,.0f}', ha='left', va='center', fontweight='bold')
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating purchase chart: {str(e)}")
    
    def create_stock_levels_chart(self, parent):
        """Create stock levels chart"""
        try:
            stock_df = self.data_service.get_stock()
            if stock_df.empty:
                self.show_no_data_message(parent, "No stock data available")
                return
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Current stock levels
            items = stock_df['item_name'][:15]  # Top 15 items
            quantities = stock_df['current_quantity'][:15]
            
            # Create bar chart with color coding
            colors = []
            for qty in quantities:
                if qty < 10:
                    colors.append(self.colors['danger'])  # Low stock
                elif qty < 25:
                    colors.append(self.colors['warning'])  # Medium stock
                else:
                    colors.append(self.colors['success'])  # Good stock
            
            bars = ax.bar(range(len(items)), quantities, color=colors, alpha=0.8)
            
            ax.set_title('Current Stock Levels (Top 15 Items)', fontweight='bold', fontsize=16)
            ax.set_ylabel('Quantity')
            ax.set_xlabel('Items')
            ax.set_xticks(range(len(items)))
            ax.set_xticklabels(items, rotation=45, ha='right')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=self.colors['danger'], label='Low Stock (<10)'),
                Patch(facecolor=self.colors['warning'], label='Medium Stock (10-25)'),
                Patch(facecolor=self.colors['success'], label='Good Stock (>25)')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating stock chart: {str(e)}")
    
    def create_low_stock_chart(self, parent):
        """Create low stock alerts chart"""
        try:
            stock_df = self.data_service.get_stock()
            if stock_df.empty:
                self.show_no_data_message(parent, "No stock data available")
                return
            
            # Filter low stock items
            low_stock = stock_df[stock_df['current_quantity'] < stock_df.get('minimum_stock', 10)]
            
            if low_stock.empty:
                # Show good news message
                fig, ax = plt.subplots(1, 1, figsize=(12, 6))
                fig.patch.set_facecolor('white')
                
                ax.text(0.5, 0.5, '✅ All Items Have Sufficient Stock!', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=20, fontweight='bold',
                       color=self.colors['success'])
                ax.set_title('Stock Alert Status', fontweight='bold', fontsize=16)
                ax.axis('off')
                
                plt.tight_layout()
                
                # Embed in GUI
                canvas = FigureCanvasTkAgg(fig, parent)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
                return
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Low stock items
            items = low_stock['item_name']
            current_qty = low_stock['current_quantity']
            min_qty = low_stock.get('minimum_stock', 10)
            
            x = np.arange(len(items))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, current_qty, width, label='Current Stock', 
                          color=self.colors['danger'], alpha=0.8)
            bars2 = ax.bar(x + width/2, min_qty, width, label='Minimum Required', 
                          color=self.colors['warning'], alpha=0.8)
            
            ax.set_title('Low Stock Alerts', fontweight='bold', fontsize=16)
            ax.set_ylabel('Quantity')
            ax.set_xlabel('Items')
            ax.set_xticks(x)
            ax.set_xticklabels(items, rotation=45, ha='right')
            ax.legend()
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating low stock chart: {str(e)}")
    
    def create_stock_movement_chart(self, parent):
        """Create stock movement analysis"""
        try:
            sales_df = self.data_service.get_sales()
            purchases_df = self.data_service.get_purchases()
            
            if sales_df.empty and purchases_df.empty:
                self.show_no_data_message(parent, "No transaction data available")
                return
            
            # Create figure
            fig, ax = plt.subplots(1, 1, figsize=(12, 6))
            fig.patch.set_facecolor('white')
            
            # Combine sales and purchase data
            stock_movement = {}
            
            if not sales_df.empty:
                for _, sale in sales_df.iterrows():
                    item = sale['item_name']
                    if item not in stock_movement:
                        stock_movement[item] = {'sold': 0, 'purchased': 0}
                    stock_movement[item]['sold'] += sale['quantity']
            
            if not purchases_df.empty:
                for _, purchase in purchases_df.iterrows():
                    item = purchase['item_name']
                    if item not in stock_movement:
                        stock_movement[item] = {'sold': 0, 'purchased': 0}
                    stock_movement[item]['purchased'] += purchase['quantity']
            
            if not stock_movement:
                self.show_no_data_message(parent, "No stock movement data")
                return
            
            # Get top 10 items by total movement
            items = list(stock_movement.keys())[:10]
            sold_qty = [stock_movement[item]['sold'] for item in items]
            purchased_qty = [stock_movement[item]['purchased'] for item in items]
            
            x = np.arange(len(items))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, purchased_qty, width, label='Purchased', 
                          color=self.colors['success'], alpha=0.8)
            bars2 = ax.bar(x + width/2, sold_qty, width, label='Sold', 
                          color=self.colors['info'], alpha=0.8)
            
            ax.set_title('Stock Movement Analysis (Top 10 Items)', fontweight='bold', fontsize=16)
            ax.set_ylabel('Quantity')
            ax.set_xlabel('Items')
            ax.set_xticks(x)
            ax.set_xticklabels(items, rotation=45, ha='right')
            ax.legend()
            
            plt.tight_layout()
            
            # Embed in GUI
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            self.show_no_data_message(parent, f"Error creating stock movement chart: {str(e)}")
    
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
        """Show enhanced status message with icon and timestamp"""
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
        
    def reset_status(self):
        """Reset status to default"""
        self.status_icon.configure(text="📊")
        self.status_label.configure(text="Ready - Generate comprehensive reports and analytics")
        self.status_time.configure(text="")
    
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
