"""
New Wage Calculation System - Isolated Implementation
This module provides the new wage calculation logic without modifying existing code.
"""

from datetime import datetime, date, timedelta
import pandas as pd
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class NewWageCalculator:
    """
    New wage calculation system using exception hours instead of overtime hours.
    Formula: [(total hours worked) - (total exception hours)] * (daily wage/8)
    """
    
    def __init__(self, data_service):
        """
        Initialize with data service for database access
        
        Args:
            data_service: Instance of DataService for database operations
        """
        self.data_service = data_service
    
    def calculate_total_hours_worked(self, time_in: str, time_out: str) -> float:
        """
        Calculate total hours worked from time_in and time_out strings
        
        Args:
            time_in: Time in format like "07:00", "08:30 AM", etc.
            time_out: Time out format like "17:00", "05:30 PM", etc.
            
        Returns:
            float: Total hours worked (e.g., 8.5 for 8 hours 30 minutes)
        """
        try:
            if not time_in or not time_out or time_in == "--:--" or time_out == "--:--":
                return 0.0
            
            # Parse time strings (handle both 12-hour and 24-hour formats)
            def parse_time(time_str):
                time_str = time_str.strip()
                
                # Handle 12-hour format (e.g., "08:30 AM")
                if 'AM' in time_str.upper() or 'PM' in time_str.upper():
                    time_part = time_str.replace(' AM', '').replace(' PM', '').replace('AM', '').replace('PM', '').strip()
                    hour, minute = map(int, time_part.split(':'))
                    
                    if 'PM' in time_str.upper() and hour != 12:
                        hour += 12
                    elif 'AM' in time_str.upper() and hour == 12:
                        hour = 0
                        
                    return hour, minute
                
                # Handle 24-hour format (e.g., "17:30")
                else:
                    hour, minute = map(int, time_str.split(':'))
                    return hour, minute
            
            in_hour, in_minute = parse_time(time_in)
            out_hour, out_minute = parse_time(time_out)
            
            # Convert to total minutes
            in_total_minutes = in_hour * 60 + in_minute
            out_total_minutes = out_hour * 60 + out_minute
            
            # Handle next day scenario (e.g., night shift)
            if out_total_minutes < in_total_minutes:
                out_total_minutes += 24 * 60  # Add 24 hours
            
            # Calculate difference in hours
            diff_minutes = out_total_minutes - in_total_minutes
            hours_worked = diff_minutes / 60.0
            
            return max(0, hours_worked)  # Ensure non-negative
            
        except Exception as e:
            logger.error(f"Error calculating hours worked: {e}")
            return 0.0
    
    def get_employee_wage_period(self, employee: Dict) -> Tuple[date, date]:
        """
        Get the wage calculation period for an employee (from last_paid to today)
        
        Args:
            employee: Employee dictionary with last_paid field
            
        Returns:
            Tuple[date, date]: (start_date, end_date) for wage calculation
        """
        try:
            today = date.today()
            
            # Get last_paid date
            last_paid = employee.get('last_paid')
            
            if not last_paid:
                # For new employees, use hire_date as start
                hire_date = employee.get('hire_date')
                if hire_date:
                    if isinstance(hire_date, str):
                        start_date = datetime.strptime(hire_date, "%Y-%m-%d").date()
                    elif isinstance(hire_date, datetime):
                        start_date = hire_date.date()
                    else:
                        start_date = hire_date
                else:
                    # Fallback: last 30 days
                    start_date = today - timedelta(days=30)
            else:
                # Convert last_paid to date
                if isinstance(last_paid, str):
                    try:
                        start_date = datetime.strptime(last_paid, "%Y-%m-%d").date()
                    except ValueError:
                        start_date = datetime.fromisoformat(last_paid.replace('Z', '')).date()
                elif isinstance(last_paid, datetime):
                    start_date = last_paid.date()
                else:
                    start_date = last_paid
                
                # Start from day after last_paid
                start_date = start_date + timedelta(days=1)
            
            return start_date, today
            
        except Exception as e:
            logger.error(f"Error getting wage period: {e}")
            # Fallback to last 30 days
            return today - timedelta(days=30), today
    
    def calculate_employee_wage_new_system(self, employee: Dict) -> Dict:
        """
        Calculate employee wage using the new system
        
        Args:
            employee: Employee dictionary with required fields
            
        Returns:
            Dict: Calculation results with all details
        """
        try:
            emp_id = employee.get('employee_id')
            daily_wage = employee.get('daily_wage', 0)
            
            if not emp_id or not daily_wage:
                raise ValueError("Employee ID and daily wage are required")
            
            # Get wage calculation period
            start_date, end_date = self.get_employee_wage_period(employee)
            
            # Get attendance records for the period
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            all_attendance_df = self.data_service.get_attendance({"employee_id": emp_id})
            
            # Filter by date range
            attendance_df = pd.DataFrame()
            if not all_attendance_df.empty:
                all_attendance_df['date_converted'] = pd.to_datetime(all_attendance_df['date'])
                mask = (all_attendance_df['date_converted'] >= start_datetime) & (all_attendance_df['date_converted'] <= end_datetime)
                attendance_df = all_attendance_df[mask]
            
            # Calculate totals using new system
            total_hours_worked = 0.0
            total_exception_hours = 0.0
            total_overtime_hours = 0.0  # For display only, not used in wage calculation
            work_days = 0
            
            for _, record in attendance_df.iterrows():
                status = record.get('status', '').lower()
                
                # Skip non-working statuses
                if status in ['absent', 'leave']:
                    continue
                
                work_days += 1
                
                # Calculate hours worked from time_in and time_out
                time_in = record.get('time_in', '')
                time_out = record.get('time_out', '')
                hours_worked = self.calculate_total_hours_worked(time_in, time_out)
                total_hours_worked += hours_worked
                
                # Exception hours = 1 for each present day (as requested by user)
                total_exception_hours += 1.0
                
                # Calculate overtime hours for display only (hours > 8 = overtime)
                daily_overtime = max(0, hours_worked - 8.0)
                total_overtime_hours += daily_overtime
            
            # Calculate wage using original formula
            # Wage = [(total hours worked) - (total exception hours)] * (daily wage/8)
            # Where exception hours = number of present days (1 per present day)
            effective_hours = max(0, total_hours_worked - total_exception_hours)
            hourly_rate = daily_wage / 8.0
            total_wage = effective_hours * hourly_rate
            
            return {
                'employee_id': emp_id,
                'employee_name': employee.get('name', 'Unknown'),
                'daily_wage': daily_wage,
                'hourly_rate': hourly_rate,
                'period_start': start_date,
                'period_end': end_date,
                'work_days': work_days,
                'total_hours_worked': total_hours_worked,
                'total_exception_hours': total_exception_hours,
                'total_overtime_hours': total_overtime_hours,  # New: include overtime hours
                'effective_hours': effective_hours,
                'total_wage': total_wage,
                'calculation_method': 'new_system'
            }
            
        except Exception as e:
            logger.error(f"Error calculating wage for employee {employee.get('employee_id', 'unknown')}: {e}")
            return {
                'employee_id': employee.get('employee_id', 'unknown'),
                'employee_name': employee.get('name', 'Unknown'),
                'error': str(e),
                'total_wage': 0,
                'calculation_method': 'new_system'
            }
    
    def calculate_all_employees_total_wage(self) -> Dict:
        """
        Calculate total wage for all active employees using new system
        
        Returns:
            Dict: Summary of all employees' wages
        """
        try:
            # Get all employees (no status filter since employees don't have status field)
            employees_df = self.data_service.get_employees()
            
            if employees_df.empty:
                return {
                    'total_employees': 0,
                    'total_wage': 0,
                    'employees': [],
                    'calculation_method': 'new_system'
                }
            
            total_wage = 0
            employee_results = []
            
            for _, employee in employees_df.iterrows():
                result = self.calculate_employee_wage_new_system(employee.to_dict())
                employee_results.append(result)
                total_wage += result.get('total_wage', 0)
            
            return {
                'total_employees': len(employee_results),
                'total_wage': total_wage,
                'employees': employee_results,
                'calculation_method': 'new_system'
            }
            
        except Exception as e:
            logger.error(f"Error calculating total wages: {e}")
            return {
                'total_employees': 0,
                'total_wage': 0,
                'employees': [],
                'error': str(e),
                'calculation_method': 'new_system'
            }