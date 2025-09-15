"""
Calendar Widget Module for Business Dashboard
Provides reusable calendar functionality for date selection
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from datetime import datetime, timedelta
import calendar


class CalendarWidget:
    """A custom calendar widget for date selection"""
    
    def __init__(self, master, date_var, callback=None):
        """
        Initialize the calendar widget
        
        Args:
            master: Parent widget
            date_var: tkinter StringVar to update with selected date
            callback: Optional callback function when date is selected
        """
        self.master = master
        self.date_var = date_var
        self.callback = callback
        self.popup = None
        
        # Current calendar state
        self.current_date = datetime.now()
        self.selected_date = None
        
    def show_calendar(self, event=None):
        """Show the calendar popup"""
        if self.popup:
            self.popup.destroy()
            
        # Create popup window
        self.popup = tk.Toplevel(self.master)
        self.popup.title("Select Date")
        self.popup.geometry("300x250")
        self.popup.transient(self.master)
        self.popup.grab_set()
        
        # Position popup near the clicked widget
        x = self.master.winfo_rootx() + 50
        y = self.master.winfo_rooty() + 50
        self.popup.geometry(f"300x250+{x}+{y}")
        
        # Create calendar interface
        self.create_calendar_interface()
        
    def create_calendar_interface(self):
        """Create the calendar interface inside the popup"""
        # Header frame for navigation
        header_frame = ctk.CTkFrame(self.popup)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Previous month button
        prev_btn = ctk.CTkButton(header_frame, text="<", width=30,
                               command=self.prev_month)
        prev_btn.pack(side="left")
        
        # Month/Year label
        month_year_text = f"{calendar.month_name[self.current_date.month]} {self.current_date.year}"
        self.month_label = ctk.CTkLabel(header_frame, text=month_year_text, font=("Arial", 14, "bold"))
        self.month_label.pack(side="left", expand=True)
        
        # Next month button
        next_btn = ctk.CTkButton(header_frame, text=">", width=30,
                               command=self.next_month)
        next_btn.pack(side="right")
        
        # Calendar frame
        cal_frame = ctk.CTkFrame(self.popup)
        cal_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            day_label = ctk.CTkLabel(cal_frame, text=day, font=("Arial", 10, "bold"))
            day_label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
        
        # Configure grid weights
        for i in range(7):
            cal_frame.grid_columnconfigure(i, weight=1)
        for i in range(7):  # 6 weeks + header
            cal_frame.grid_rowconfigure(i, weight=1)
        
        # Create calendar days
        self.create_calendar_days(cal_frame)
        
        # Button frame
        btn_frame = ctk.CTkFrame(self.popup)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        # Today button
        today_btn = ctk.CTkButton(btn_frame, text="Today", 
                                command=self.select_today)
        today_btn.pack(side="left", padx=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel",
                                 command=self.close_calendar)
        cancel_btn.pack(side="right", padx=5)
        
    def create_calendar_days(self, parent):
        """Create the calendar day buttons"""
        # Clear existing day buttons
        for widget in parent.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()
        
        # Get calendar for current month
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Create day buttons
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days from other months
                    continue
                
                # Create date for this day
                day_date = datetime(self.current_date.year, self.current_date.month, day)
                
                # Determine button appearance
                is_today = day_date.date() == datetime.now().date()
                is_selected = (self.selected_date and 
                             day_date.date() == self.selected_date.date())
                
                # Create button
                day_btn = ctk.CTkButton(parent, text=str(day), width=30, height=25,
                                      command=lambda d=day_date: self.select_date(d))
                
                # Style the button based on state
                if is_today:
                    day_btn.configure(fg_color="#1f538d")  # Blue for today
                elif is_selected:
                    day_btn.configure(fg_color="#165a2e")  # Green for selected
                
                day_btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky="nsew")
    
    def prev_month(self):
        """Navigate to previous month"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        """Navigate to next month"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def update_calendar(self):
        """Update the calendar display"""
        # Update month/year label
        month_year_text = f"{calendar.month_name[self.current_date.month]} {self.current_date.year}"
        self.month_label.configure(text=month_year_text)
        
        # Recreate calendar days
        cal_frame = None
        for widget in self.popup.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.popup.winfo_children()[0]:
                cal_frame = widget
                break
        
        if cal_frame:
            self.create_calendar_days(cal_frame)
    
    def select_date(self, date):
        """Select a specific date"""
        self.selected_date = date
        # Format date as dd/mm/yy
        formatted_date = date.strftime('%d/%m/%y')
        self.date_var.set(formatted_date)
        
        # Call callback if provided
        if self.callback:
            self.callback(date)
        
        # Close the calendar
        self.close_calendar()
    
    def select_today(self):
        """Select today's date"""
        today = datetime.now()
        self.select_date(today)
    
    def close_calendar(self):
        """Close the calendar popup"""
        if self.popup:
            self.popup.destroy()
            self.popup = None


class DateFieldWithCalendar:
    """A date input field with integrated calendar popup"""
    
    def __init__(self, master, row, column, label_text, date_var, **kwargs):
        """
        Create a date field with calendar popup
        
        Args:
            master: Parent widget
            row: Grid row position
            column: Grid column position  
            label_text: Label text for the field
            date_var: tkinter StringVar for the date value
            **kwargs: Additional arguments for customization
        """
        self.master = master
        self.date_var = date_var
        
        # Create label
        self.label = ctk.CTkLabel(master, text=label_text)
        self.label.grid(row=row, column=column, sticky="w", padx=5, pady=2)
        
        # Create frame for entry and button
        self.field_frame = ctk.CTkFrame(master)
        self.field_frame.grid(row=row, column=column+1, sticky="ew", padx=5, pady=2)
        
        # Configure grid
        self.field_frame.grid_columnconfigure(0, weight=1)
        
        # Create entry field
        self.entry = ctk.CTkEntry(self.field_frame, textvariable=date_var, 
                                placeholder_text="dd/mm/yy")
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Create calendar button
        self.cal_button = ctk.CTkButton(self.field_frame, text="📅", width=30,
                                      command=self.show_calendar)
        self.cal_button.grid(row=0, column=1)
        
        # Create calendar widget
        self.calendar = CalendarWidget(master, date_var, self.on_date_selected)
    
    def show_calendar(self):
        """Show the calendar popup"""
        self.calendar.show_calendar()
    
    def on_date_selected(self, date):
        """Callback when date is selected from calendar"""
        # Additional processing can be added here if needed
        pass
    
    def get_date(self):
        """Get the current date value"""
        return self.date_var.get()
    
    def set_date(self, date_str):
        """Set the date value"""
        self.date_var.set(date_str)
    
    def clear(self):
        """Clear the date field"""
        self.date_var.set("")


# Utility functions for date handling
def parse_date_from_display(date_str):
    """
    Parse date from display format (dd/mm/yy) to datetime object
    
    Args:
        date_str: Date string in dd/mm/yy format
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        if '/' in date_str and len(date_str) <= 8:
            return datetime.strptime(date_str, '%d/%m/%y')
        elif '-' in date_str and len(date_str) == 10:
            return datetime.strptime(date_str, '%Y-%m-%d')
        return None
    except ValueError:
        return None


def format_date_for_display(date_obj):
    """
    Format datetime object to display format (dd/mm/yy)
    
    Args:
        date_obj: datetime object
        
    Returns:
        Formatted date string
    """
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime('%d/%m/%y')
    return str(date_obj)


def format_date_for_storage(date_obj):
    """
    Format datetime object for database storage
    
    Args:
        date_obj: datetime object
        
    Returns:
        Formatted date for database storage
    """
    if hasattr(date_obj, 'strftime'):
        return date_obj
    return date_obj