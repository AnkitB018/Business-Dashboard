# Business Dashboard Logging System

This comprehensive logging system provides detailed tracking and debugging capabilities for the Business Dashboard application, especially useful for production deployments and client-side debugging.

## 🎯 Features

### Multi-Layer Logging
- **Main Application Logger**: Tracks application lifecycle, UI interactions, and general operations
- **Error Tracker**: Detailed error logging with stack traces and context
- **Database Logger**: MongoDB operations with timing and performance metrics  
- **User Activity Logger**: Tracks all user interactions and business operations
- **Performance Logger**: Function execution times and performance bottlenecks
- **Debug Logger**: Detailed debugging information for development

### Production-Ready Capabilities
- **Automatic Log Rotation**: 10MB file size limit with backup retention
- **Performance Monitoring**: Function decorators for automatic timing
- **Error Correlation**: Links errors with user actions and system state
- **Remote Debugging**: Comprehensive logs for troubleshooting deployed applications

## 📁 File Structure

```
logs/
├── main_app.log          # Application lifecycle and general operations
├── error_tracker.log     # Error and exception tracking
├── database.log          # Database operations and performance
├── user_activity.log     # User interactions and business operations
├── performance.log       # Function timing and performance metrics
├── debug.log            # Detailed debugging information
├── archive/             # Rotated log backups
└── exports/             # Log analysis exports
```

## 🚀 Quick Start

### 1. Initialize Logging System
```bash
python setup_logging.py
```

### 2. View Logs
```bash
python log_viewer.py
```

### 3. Integrate with Your Code
```python
from logger_config import BusinessDashboardLogger

# Initialize logger
dashboard_logger = BusinessDashboardLogger()

# Use function decorators for automatic logging
@dashboard_logger.log_function_call
def my_function():
    pass

# Manual logging
dashboard_logger.log_user_activity("john_doe", "add_employee", "Added new employee", {"name": "Jane Smith"})
dashboard_logger.log_performance("database_query", 150, {"collection": "employees"})
```

## 📊 Log Viewer Features

The `log_viewer.py` tool provides:

### Visual Log Analysis
- **Raw Log View**: Complete log files with syntax highlighting
- **Structured View**: Organized table format for easy browsing
- **Error Analysis**: Automatic error grouping and frequency analysis
- **Performance Analysis**: Slow operation detection and timing analysis

### Filtering & Search
- **Text Filtering**: Search across all log content
- **Level Filtering**: Filter by DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Real-time Updates**: Refresh logs without restarting the viewer
- **Export Functionality**: Save filtered results for sharing

### Usage Examples
```bash
# View all logs
python log_viewer.py

# Analyze specific time period (within the GUI)
# 1. Select log file from dropdown
# 2. Use filters to find specific issues
# 3. Double-click entries for detailed view
# 4. Export results for sharing with developers
```

## 🔧 Advanced Configuration

### Logger Customization
```python
# Custom logger instance
logger = BusinessDashboardLogger(
    log_dir="custom_logs",
    max_file_size=20 * 1024 * 1024,  # 20MB
    backup_count=10
)

# Get specific loggers
main_logger = logger.get_main_logger()
error_logger = logger.get_error_logger()
```

### Performance Monitoring
```python
# Manual performance logging
start_time = time.time()
# ... your code ...
duration = (time.time() - start_time) * 1000
logger.log_performance("custom_operation", duration, {"param": "value"})

# Automatic with decorator
@logger.log_function_call
def slow_function():
    time.sleep(2)  # Will be logged as slow operation
```

### User Activity Tracking
```python
# Track business operations
logger.log_user_activity(
    user_id="user123",
    action="purchase_order", 
    description="Created purchase order PO-001",
    context={"amount": 1500.00, "supplier": "ABC Corp"}
)

# Track UI interactions
logger.log_user_activity(
    user_id="user123",
    action="view_report",
    description="Opened sales report",
    context={"report_type": "monthly", "date_range": "2024-01"}
)
```

## 🚨 Production Deployment

### Pre-Deployment Checklist
1. **Run Setup**: Execute `python setup_logging.py`
2. **Test Logging**: Verify all loggers are working
3. **Check Permissions**: Ensure write access to logs directory
4. **Configure Rotation**: Adjust file sizes if needed for storage constraints

### Client-Side Debugging
When issues occur on client machines:

1. **Collect Logs**: Retrieve the entire `logs/` directory
2. **Use Log Viewer**: Open logs with `python log_viewer.py`
3. **Analyze Issues**: 
   - Check Error Analysis tab for exception patterns
   - Review Performance tab for slow operations
   - Use filters to isolate specific timeframes
4. **Export Evidence**: Save filtered results for development team

### Remote Support Workflow
```bash
# Client runs this to package logs
zip -r support_logs_$(date +%Y%m%d).zip logs/

# Developer receives logs and analyzes
python log_viewer.py
# 1. Load received log files
# 2. Filter by error timeframe
# 3. Export analysis results
# 4. Provide fix recommendations
```

## 📋 Log Format

### Standard Log Entry
```
2024-01-15 14:30:25 | INFO | data_service | add_employee:45 | Successfully added employee: Jane Smith
```

### JSON Performance Log
```json
{
  "timestamp": "2024-01-15 14:30:25",
  "operation": "database_insert",
  "duration_ms": 145,
  "context": {"collection": "employees", "document_size": 1024}
}
```

### User Activity Log
```json
{
  "timestamp": "2024-01-15 14:30:25",
  "user_id": "john_doe",
  "action": "add_employee",
  "description": "Added new employee",
  "context": {"name": "Jane Smith", "department": "Sales"},
  "session_id": "sess_12345"
}
```

## 🛠 Troubleshooting

### Common Issues

**Logs not appearing**
- Check file permissions in logs directory
- Verify logger initialization in your code
- Run `python setup_logging.py` to reinitialize

**Log viewer not opening files**
- Ensure log files exist in logs/ directory
- Check file encoding (should be UTF-8)
- Try refreshing the file list in the viewer

**Performance impact**
- Logging is optimized for minimal overhead
- Disable DEBUG level in production if needed
- Monitor log file sizes and rotation

### Performance Optimization
```python
# Disable debug logging in production
import logging
logging.getLogger().setLevel(logging.INFO)

# Reduce context data for high-frequency operations
logger.log_performance("quick_op", duration, {})  # Minimal context
```

## 📈 Monitoring & Alerts

### Key Metrics to Monitor
- **Error Rate**: Frequency of ERROR/CRITICAL entries
- **Performance**: Operations taking >1000ms
- **User Activity**: Patterns indicating issues
- **Database Performance**: Slow queries and connection issues

### Alert Thresholds
- **Critical**: >10 errors per minute
- **Warning**: Operations >5 seconds
- **Info**: Unusual user activity patterns

## 🔄 Maintenance

### Regular Tasks
1. **Archive Old Logs**: Move old rotated logs to long-term storage
2. **Monitor Disk Usage**: Ensure adequate space for logging
3. **Review Performance**: Identify optimization opportunities
4. **Update Documentation**: Keep troubleshooting guides current

### Log Retention Policy
- **Active Logs**: Keep current + 5 rotated files (≈60MB total)
- **Archive**: Monthly archives for 12 months
- **Compliance**: Adjust retention based on business requirements

## 📞 Support

For issues with the logging system:
1. Check this documentation first
2. Review sample log entries in logs/ directory
3. Use log_viewer.py to analyze patterns
4. Contact development team with exported log analysis

---

*This logging system is designed to provide comprehensive visibility into application behavior for effective production support and debugging.*
