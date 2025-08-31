"""
Comprehensive Logging Configuration for Business Dashboard
Provides detailed logging for debugging and issue tracking in production
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
import traceback
import json


class BusinessDashboardLogger:
    """Enhanced logging system for Business Dashboard with multiple log levels and handlers"""
    
    def __init__(self, app_name="BusinessDashboard"):
        self.app_name = app_name
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create different log files for different purposes
        self.log_files = {
            'main': self.log_dir / f"{app_name}.log",
            'error': self.log_dir / f"{app_name}_errors.log",
            'database': self.log_dir / f"{app_name}_database.log",
            'user_activity': self.log_dir / f"{app_name}_user_activity.log",
            'performance': self.log_dir / f"{app_name}_performance.log",
            'debug': self.log_dir / f"{app_name}_debug.log"
        }
        
        # Setup loggers
        self.setup_loggers()
        
    def setup_loggers(self):
        """Setup multiple specialized loggers"""
        
        # Main application logger
        self.main_logger = self._create_logger(
            'main_app',
            self.log_files['main'],
            logging.INFO,
            include_console=True
        )
        
        # Error logger (for critical issues)
        self.error_logger = self._create_logger(
            'error_tracker',
            self.log_files['error'],
            logging.ERROR,
            include_console=False
        )
        
        # Database operations logger
        self.db_logger = self._create_logger(
            'database',
            self.log_files['database'],
            logging.DEBUG,
            include_console=False
        )
        
        # User activity logger
        self.activity_logger = self._create_logger(
            'user_activity',
            self.log_files['user_activity'],
            logging.INFO,
            include_console=False
        )
        
        # Performance logger
        self.performance_logger = self._create_logger(
            'performance',
            self.log_files['performance'],
            logging.INFO,
            include_console=False
        )
        
        # Debug logger (detailed debugging info)
        self.debug_logger = self._create_logger(
            'debug',
            self.log_files['debug'],
            logging.DEBUG,
            include_console=False
        )
    
    def _create_logger(self, name, log_file, level, include_console=False):
        """Create a logger with file and optionally console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create detailed formatter
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Console handler (for main logger only)
        if include_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(levelname)s:%(name)s:%(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def log_app_start(self):
        """Log application startup"""
        self.main_logger.info("="*80)
        self.main_logger.info(f"BUSINESS DASHBOARD STARTED - {datetime.now()}")
        self.main_logger.info(f"Python Version: {sys.version}")
        self.main_logger.info(f"Platform: {sys.platform}")
        self.main_logger.info(f"Working Directory: {os.getcwd()}")
        self.main_logger.info("="*80)
    
    def log_app_shutdown(self):
        """Log application shutdown"""
        self.main_logger.info("="*80)
        self.main_logger.info(f"BUSINESS DASHBOARD SHUTDOWN - {datetime.now()}")
        self.main_logger.info("="*80)
    
    def log_error(self, error, context="", include_traceback=True):
        """Log errors with detailed context"""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc() if include_traceback else None
        }
        
        # Log to both main and error logs
        self.main_logger.error(f"ERROR in {context}: {error}")
        self.error_logger.error(json.dumps(error_info, indent=2))
        
        if include_traceback:
            self.error_logger.error(f"Traceback:\n{traceback.format_exc()}")
    
    def log_database_operation(self, operation, collection, data=None, result=None, duration=None):
        """Log database operations"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'collection': collection,
            'data_summary': self._summarize_data(data) if data else None,
            'result_summary': self._summarize_data(result) if result else None,
            'duration_ms': duration
        }
        
        self.db_logger.info(json.dumps(log_data))
        
        if duration and duration > 1000:  # Log slow operations (>1 second)
            self.performance_logger.warning(
                f"SLOW DATABASE OPERATION: {operation} on {collection} took {duration}ms"
            )
    
    def log_user_activity(self, action, details=None, user_context=None):
        """Log user activities and interactions"""
        activity_data = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'user_context': user_context
        }
        
        self.activity_logger.info(json.dumps(activity_data))
    
    def log_performance(self, operation, duration, details=None):
        """Log performance metrics"""
        perf_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration_ms': duration,
            'details': details
        }
        
        self.performance_logger.info(json.dumps(perf_data))
        
        # Log warnings for slow operations
        if duration > 5000:  # 5 seconds
            self.main_logger.warning(f"SLOW OPERATION: {operation} took {duration}ms")
    
    def log_debug(self, message, data=None):
        """Log detailed debugging information"""
        debug_data = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'data': self._summarize_data(data) if data else None
        }
        
        self.debug_logger.debug(json.dumps(debug_data))
    
    def log_gui_event(self, event_type, component, details=None):
        """Log GUI events and user interactions"""
        self.log_user_activity(
            action=f"GUI_{event_type}",
            details={'component': component, 'details': details}
        )
    
    def log_data_operation(self, operation, module, record_count=None, success=True, error=None):
        """Log data management operations"""
        if success:
            self.main_logger.info(
                f"DATA_OPERATION: {operation} in {module} - {record_count} records"
            )
        else:
            self.log_error(
                error or Exception("Data operation failed"),
                context=f"{operation} in {module}"
            )
    
    def _summarize_data(self, data):
        """Create a summary of data for logging (avoid logging sensitive info)"""
        if data is None:
            return None
        
        if isinstance(data, dict):
            return {
                'type': 'dict',
                'keys': list(data.keys()),
                'size': len(data)
            }
        elif isinstance(data, list):
            return {
                'type': 'list',
                'size': len(data),
                'sample_types': [type(item).__name__ for item in data[:3]]
            }
        elif hasattr(data, '__len__'):
            return {
                'type': type(data).__name__,
                'size': len(data)
            }
        else:
            return {
                'type': type(data).__name__,
                'str_repr': str(data)[:100]  # First 100 chars
            }
    
    def get_log_summary(self, hours=24):
        """Get a summary of recent logs for troubleshooting"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'period_hours': hours,
            'log_files': {}
        }
        
        for log_type, log_file in self.log_files.items():
            if log_file.exists():
                summary['log_files'][log_type] = {
                    'size_bytes': log_file.stat().st_size,
                    'last_modified': datetime.fromtimestamp(
                        log_file.stat().st_mtime
                    ).isoformat()
                }
        
        return summary
    
    def cleanup_old_logs(self, days_to_keep=30):
        """Clean up old log files"""
        try:
            import time
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)
            
            cleaned_files = []
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    cleaned_files.append(str(log_file))
            
            if cleaned_files:
                self.main_logger.info(f"Cleaned up {len(cleaned_files)} old log files")
            
        except Exception as e:
            self.log_error(e, "cleanup_old_logs")


# Global logger instance
dashboard_logger = None


def get_logger():
    """Get the global logger instance"""
    global dashboard_logger
    if dashboard_logger is None:
        dashboard_logger = BusinessDashboardLogger()
    return dashboard_logger


def log_function_call(func):
    """Decorator to log function calls and performance"""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        start_time = datetime.now()
        
        try:
            # Log function entry
            logger.debug_logger.debug(
                f"FUNCTION_CALL: {func.__name__} started with args={len(args)}, kwargs={list(kwargs.keys())}"
            )
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Log successful completion
            duration = (datetime.now() - start_time).total_seconds() * 1000
            logger.log_performance(
                operation=f"function_{func.__name__}",
                duration=duration,
                details={'success': True}
            )
            
            return result
            
        except Exception as e:
            # Log error
            duration = (datetime.now() - start_time).total_seconds() * 1000
            logger.log_error(
                e,
                context=f"function_{func.__name__}",
                include_traceback=True
            )
            logger.log_performance(
                operation=f"function_{func.__name__}",
                duration=duration,
                details={'success': False, 'error': str(e)}
            )
            raise
    
    return wrapper


# Convenience functions
def log_info(message, context=""):
    """Quick info logging"""
    get_logger().main_logger.info(f"{context}: {message}" if context else message)


def log_error(error, context=""):
    """Quick error logging"""
    get_logger().log_error(error, context)


def log_debug(message, data=None):
    """Quick debug logging"""
    get_logger().log_debug(message, data)


def log_user_action(action, details=None):
    """Quick user activity logging"""
    get_logger().log_user_activity(action, details)
