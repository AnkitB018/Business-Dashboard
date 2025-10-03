"""
Bonus Calculation System - Independent Implementation
This module provides bonus calculation logic for yearly bonus calculations.
Formula: Total earned amount * bonus_rate (default 8.33%)
"""

from datetime import datetime, date, timedelta
import pandas as pd
from typing import Dict, Optional, Tuple
import logging
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

class BonusCalculator:
    """
    Bonus calculation system for yearly bonus calculations.
    Calculates total earned amount from joining/last bonus date and applies bonus rate.
    """
    
    def __init__(self, data_service):
        """
        Initialize with data service for database access
        
        Args:
            data_service: Instance of DataService for database operations
        """
        self.data_service = data_service
        self.default_bonus_rate = 8.33  # Default bonus rate percentage
    
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
    
    def get_employee_bonus_period(self, employee: Dict) -> Tuple[date, date]:
        """
        Get the bonus calculation period for an employee (from joining/last_bonus to today)
        
        Args:
            employee: Employee dictionary with joining_date and last_bonus_paid fields
            
        Returns:
            Tuple[date, date]: (start_date, end_date) for bonus calculation
        """
        try:
            today = date.today()
            
            # Get last_bonus_paid date or joining_date
            last_bonus_paid = employee.get('last_bonus_paid')
            joining_date = employee.get('joining_date') or employee.get('hire_date') or employee.get('join_date')
            
            if last_bonus_paid and last_bonus_paid != joining_date:
                # Start from day after last bonus payment
                if isinstance(last_bonus_paid, str):
                    try:
                        start_date = datetime.strptime(last_bonus_paid, "%Y-%m-%d").date()
                    except ValueError:
                        start_date = datetime.fromisoformat(last_bonus_paid.replace('Z', '')).date()
                elif hasattr(last_bonus_paid, 'date'):
                    start_date = last_bonus_paid.date()
                else:
                    start_date = last_bonus_paid
                
                start_date = start_date + timedelta(days=1)  # Start from next day
            else:
                # Start from joining date (first time calculation)
                if joining_date:
                    if isinstance(joining_date, str):
                        try:
                            start_date = datetime.strptime(joining_date, "%Y-%m-%d").date()
                        except ValueError:
                            start_date = datetime.fromisoformat(joining_date.replace('Z', '')).date()
                    elif hasattr(joining_date, 'date'):
                        start_date = joining_date.date()
                    else:
                        start_date = joining_date
                else:
                    # Fallback: 1 year ago (should not happen with proper migration)
                    start_date = today - timedelta(days=365)
            
            return start_date, today
            
        except Exception as e:
            logger.error(f"Error getting bonus period: {e}")
            return today - timedelta(days=365), today
    
    def calculate_time_until_next_bonus(self, employee: Dict) -> Dict:
        """
        Calculate time remaining until next bonus payment (1 year from joining or last bonus)
        
        Args:
            employee: Employee dictionary with joining_date and last_bonus_paid fields
            
        Returns:
            Dict: Contains months, days, and next_bonus_date
        """
        try:
            today = date.today()
            
            # Get the reference date (joining or last bonus)
            last_bonus_paid = employee.get('last_bonus_paid')
            joining_date = employee.get('joining_date') or employee.get('hire_date') or employee.get('join_date')
            
            if last_bonus_paid and last_bonus_paid != joining_date:
                # Next bonus is 1 year from last bonus payment
                if isinstance(last_bonus_paid, str):
                    try:
                        reference_date = datetime.strptime(last_bonus_paid, "%Y-%m-%d").date()
                    except ValueError:
                        reference_date = datetime.fromisoformat(last_bonus_paid.replace('Z', '')).date()
                elif hasattr(last_bonus_paid, 'date'):
                    reference_date = last_bonus_paid.date()
                else:
                    reference_date = last_bonus_paid
                
                next_bonus_date = reference_date + relativedelta(years=1)
            else:
                # Next bonus is 1 year from joining date (first time)
                if joining_date:
                    if isinstance(joining_date, str):
                        try:
                            reference_date = datetime.strptime(joining_date, "%Y-%m-%d").date()
                        except ValueError:
                            reference_date = datetime.fromisoformat(joining_date.replace('Z', '')).date()
                    elif hasattr(joining_date, 'date'):
                        reference_date = joining_date.date()
                    else:
                        reference_date = joining_date
                    
                    next_bonus_date = reference_date + relativedelta(years=1)
                else:
                    # Fallback
                    next_bonus_date = today + relativedelta(years=1)
            
            # Calculate difference
            if next_bonus_date <= today:
                # Bonus is due or overdue
                return {
                    'months': 0,
                    'days': 0,
                    'next_bonus_date': next_bonus_date,
                    'is_due': True
                }
            
            # Calculate months and days remaining
            diff = relativedelta(next_bonus_date, today)
            
            return {
                'months': diff.months + (diff.years * 12),
                'days': diff.days,
                'next_bonus_date': next_bonus_date,
                'is_due': False
            }
            
        except Exception as e:
            logger.error(f"Error calculating time until next bonus: {e}")
            return {
                'months': 0,
                'days': 0,
                'next_bonus_date': today,
                'is_due': True
            }
    
    def calculate_employee_bonus(self, employee: Dict, bonus_rate: float = None) -> Dict:
        """
        Calculate bonus for an employee based on total earnings since joining/last bonus
        
        Args:
            employee: Employee dictionary
            bonus_rate: Bonus rate percentage (default: 8.33%)
            
        Returns:
            Dict: Bonus calculation results
        """
        try:
            if bonus_rate is None:
                bonus_rate = self.default_bonus_rate
            
            # Get employee info
            emp_id = employee.get('employee_id', 'Unknown')
            emp_name = employee.get('name', 'Unknown')
            daily_wage = float(employee.get('daily_wage', 0))
            
            if daily_wage <= 0:
                return {
                    'error': 'Employee daily wage not set or invalid',
                    'employee_id': emp_id,
                    'employee_name': emp_name
                }
            
            # Get bonus calculation period
            start_date, end_date = self.get_employee_bonus_period(employee)
            
            # Get attendance data for the period
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Get all attendance records for this employee
            all_attendance_df = self.data_service.get_attendance({"employee_id": emp_id})
            
            # Filter by date range
            attendance_df = pd.DataFrame()
            if not all_attendance_df.empty:
                all_attendance_df['date_converted'] = pd.to_datetime(all_attendance_df['date'])
                mask = (all_attendance_df['date_converted'] >= start_datetime) & (all_attendance_df['date_converted'] <= end_datetime)
                attendance_df = all_attendance_df[mask]
            
            # Calculate totals
            total_days = 0
            total_hours_worked = 0.0
            total_exception_hours = 0.0
            total_overtime_hours = 0.0  # For display only
            total_earned = 0.0
            hourly_rate = daily_wage / 8  # Same formula as wage calculation
            
            for _, record in attendance_df.iterrows():
                if record.get('status') in ['Present', 'Overtime']:
                    total_days += 1
                    
                    # Calculate hours worked
                    time_in = record.get('time_in', '')
                    time_out = record.get('time_out', '')
                    hours_worked = self.calculate_total_hours_worked(time_in, time_out)
                    
                    # Exception hours = 1 for each present day (as per user requirement)
                    exception_hours = 1.0
                    
                    # Calculate effective hours (total - exception)
                    effective_hours = max(0, hours_worked - exception_hours)
                    
                    # Calculate overtime for display only
                    daily_overtime = max(0, hours_worked - 8.0)
                    total_overtime_hours += daily_overtime
                    
                    # Add to totals
                    total_hours_worked += hours_worked
                    total_exception_hours += exception_hours
                    total_earned += effective_hours * hourly_rate
            
            # Calculate bonus
            bonus_amount = total_earned * (bonus_rate / 100)
            
            # Calculate time until next bonus
            time_info = self.calculate_time_until_next_bonus(employee)
            
            return {
                'employee_id': emp_id,
                'employee_name': emp_name,
                'daily_wage': daily_wage,
                'hourly_rate': hourly_rate,
                'period_start': start_date.strftime('%Y-%m-%d'),
                'period_end': end_date.strftime('%Y-%m-%d'),
                'work_days': total_days,
                'total_hours_worked': total_hours_worked,
                'total_exception_hours': total_exception_hours,
                'total_overtime_hours': total_overtime_hours,  # For display only
                'effective_hours': total_hours_worked - total_exception_hours,
                'total_earned': total_earned,
                'bonus_rate': bonus_rate,
                'bonus_amount': bonus_amount,
                'months_remaining': time_info['months'],
                'days_remaining': time_info['days'],
                'next_bonus_date': time_info['next_bonus_date'].strftime('%Y-%m-%d'),
                'is_bonus_due': time_info['is_due']
            }
            
        except Exception as e:
            logger.error(f"Error calculating bonus for employee {employee.get('employee_id', 'Unknown')}: {e}")
            return {
                'error': f'Failed to calculate bonus: {str(e)}',
                'employee_id': employee.get('employee_id', 'Unknown'),
                'employee_name': employee.get('name', 'Unknown')
            }
    
    def reset_employee_bonus(self, employee_id: str) -> bool:
        """
        Mark bonus as paid for an employee (sets last_bonus_paid to today)
        
        Args:
            employee_id: Employee ID
            
        Returns:
            bool: True if successful
        """
        try:
            today = date.today()
            
            # Update employee record with last_bonus_paid
            result = self.data_service.update_employee(employee_id, {
                'last_bonus_paid': today.strftime('%Y-%m-%d')
            })
            
            if result > 0:
                logger.info(f"Bonus payment recorded for employee {employee_id}")
                return True
            else:
                logger.error(f"Failed to update bonus payment for employee {employee_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error resetting bonus for employee {employee_id}: {e}")
            return False
    
    def calculate_bonus_by_id(self, employee_id: str, bonus_rate: float = None) -> Dict:
        """
        Calculate bonus for an employee by their ID (wrapper method)
        
        Args:
            employee_id: Employee ID string
            bonus_rate: Bonus rate percentage (default: 8.33%)
            
        Returns:
            Dict: Bonus calculation results
        """
        try:
            # Get employee data
            employees_df = self.data_service.get_employees({"employee_id": employee_id})
            if employees_df.empty:
                return {
                    'error': f'Employee with ID {employee_id} not found',
                    'employee_id': employee_id,
                    'employee_name': 'Unknown'
                }
            
            employee_dict = employees_df.iloc[0].to_dict()
            return self.calculate_employee_bonus(employee_dict, bonus_rate)
            
        except Exception as e:
            logger.error(f"Error calculating bonus for employee {employee_id}: {e}")
            return {
                'error': f'Failed to calculate bonus: {str(e)}',
                'employee_id': employee_id,
                'employee_name': 'Unknown'
            }