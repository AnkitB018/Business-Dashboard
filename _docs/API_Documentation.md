# Business Dashboard - API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Data Service API](#data-service-api)
3. [Database Manager API](#database-manager-api)
4. [Configuration API](#configuration-api)
5. [Logger API](#logger-api)
6. [Error Handling](#error-handling)
7. [Data Models](#data-models)
8. [Code Examples](#code-examples)
9. [Extension Points](#extension-points)
10. [Future API Plans](#future-api-plans)

---

## Overview

This document describes the internal API structure of the Business Dashboard application. While the current version is a desktop application, this API documentation serves developers who want to understand the codebase, extend functionality, or potentially develop integrations.

### API Design Principles
- **Separation of Concerns**: Clear separation between GUI, business logic, and data layers
- **Error Handling**: Comprehensive error handling with logging
- **Data Validation**: Input validation at multiple levels
- **Extensibility**: Designed for future enhancements and integrations
- **Type Safety**: Consistent data types and structures

### Current Architecture
```
GUI Layer (CustomTkinter)
    ↓
Business Logic Layer (HRDataService)
    ↓
Data Access Layer (DatabaseManager)
    ↓
Database Layer (MongoDB)
```

---

## Data Service API

The `HRDataService` class provides the main business logic API for the application.

### Class: HRDataService

#### Constructor
```python
class HRDataService:
    def __init__(self, db_manager: DatabaseManager, logger: logging.Logger)
```

**Parameters:**
- `db_manager`: DatabaseManager instance for database operations
- `logger`: Logger instance for operation logging

**Example:**
```python
from data_service import HRDataService
from database import DatabaseManager
import logging

db_manager = DatabaseManager()
logger = logging.getLogger('BusinessDashboard')
hr_service = HRDataService(db_manager, logger)
```

### Employee Management Methods

#### add_employee()
```python
def add_employee(self, employee_data: dict) -> dict
```

**Purpose**: Add a new employee to the database

**Parameters:**
- `employee_data` (dict): Employee information dictionary

**Returns:**
- `dict`: Result with success status and employee ID or error message

**Employee Data Structure:**
```python
{
    "name": str,           # Required: Employee full name
    "employee_id": str,    # Required: Unique employee identifier
    "department": str,     # Required: Department name
    "position": str,       # Required: Job position
    "salary": float,       # Required: Salary amount
    "hire_date": str,      # Required: Hire date (YYYY-MM-DD format)
    "phone": str,          # Optional: Phone number
    "email": str,          # Optional: Email address
    "address": str         # Optional: Physical address
}
```

**Example:**
```python
employee = {
    "name": "John Doe",
    "employee_id": "EMP001",
    "department": "Engineering",
    "position": "Software Developer",
    "salary": 75000.0,
    "hire_date": "2025-01-15",
    "phone": "555-0123",
    "email": "john.doe@company.com",
    "address": "123 Main St, City, State"
}

result = hr_service.add_employee(employee)
print(result)  # {"success": True, "employee_id": "EMP001"}
```

#### get_all_employees()
```python
def get_all_employees() -> list
```

**Purpose**: Retrieve all employees from the database

**Returns:**
- `list`: List of employee dictionaries

**Example:**
```python
employees = hr_service.get_all_employees()
for employee in employees:
    print(f"{employee['name']} - {employee['department']}")
```

#### update_employee()
```python
def update_employee(self, employee_id: str, updated_data: dict) -> dict
```

**Purpose**: Update existing employee information

**Parameters:**
- `employee_id` (str): Unique employee identifier
- `updated_data` (dict): Dictionary with updated fields

**Returns:**
- `dict`: Result with success status or error message

**Example:**
```python
updates = {
    "salary": 80000.0,
    "position": "Senior Software Developer"
}
result = hr_service.update_employee("EMP001", updates)
```

#### delete_employee()
```python
def delete_employee(self, employee_id: str) -> dict
```

**Purpose**: Delete an employee and all associated data

**Parameters:**
- `employee_id` (str): Unique employee identifier

**Returns:**
- `dict`: Result with success status or error message

**Example:**
```python
result = hr_service.delete_employee("EMP001")
```

#### search_employees()
```python
def search_employees(self, search_term: str, search_field: str = "name") -> list
```

**Purpose**: Search employees by specific field

**Parameters:**
- `search_term` (str): Search query
- `search_field` (str): Field to search in ("name", "department", "position", "employee_id")

**Returns:**
- `list`: List of matching employee dictionaries

**Example:**
```python
# Search by name
results = hr_service.search_employees("John", "name")

# Search by department
results = hr_service.search_employees("Engineering", "department")
```

### Attendance Management Methods

#### add_attendance()
```python
def add_attendance(self, employee_id: str, attendance_data: dict) -> dict
```

**Purpose**: Add attendance record for an employee

**Parameters:**
- `employee_id` (str): Employee identifier
- `attendance_data` (dict): Attendance information

**Attendance Data Structure:**
```python
{
    "date": str,           # Required: Date in YYYY-MM-DD format
    "status": str,         # Required: "Present", "Absent", "Leave", "Overtime"
    "hours_worked": float  # Optional: Number of hours worked
}
```

**Example:**
```python
attendance = {
    "date": "2025-09-09",
    "status": "Present",
    "hours_worked": 8.0
}
result = hr_service.add_attendance("EMP001", attendance)
```

#### get_employee_attendance()
```python
def get_employee_attendance(self, employee_id: str, start_date: str = None, end_date: str = None) -> list
```

**Purpose**: Get attendance records for an employee

**Parameters:**
- `employee_id` (str): Employee identifier
- `start_date` (str, optional): Start date filter (YYYY-MM-DD)
- `end_date` (str, optional): End date filter (YYYY-MM-DD)

**Returns:**
- `list`: List of attendance records

### Statistics Methods

#### get_employee_statistics()
```python
def get_employee_statistics() -> dict
```

**Purpose**: Get comprehensive employee statistics

**Returns:**
- `dict`: Statistics including counts, averages, and distributions

**Example Response:**
```python
{
    "total_employees": 150,
    "average_salary": 65000.0,
    "department_distribution": {
        "Engineering": 45,
        "Sales": 30,
        "HR": 10,
        "Marketing": 25
    },
    "highest_paid_employee": {
        "name": "Jane Smith",
        "salary": 120000.0
    },
    "attendance_summary": {
        "total_present_days": 1200,
        "total_absent_days": 50,
        "attendance_rate": 96.0
    }
}
```

#### get_financial_statistics()
```python
def get_financial_statistics() -> dict
```

**Purpose**: Get financial and business statistics

**Returns:**
- `dict`: Financial metrics and data for reporting

### Data Validation Methods

#### validate_employee_data()
```python
def validate_employee_data(self, employee_data: dict) -> tuple[bool, str]
```

**Purpose**: Validate employee data before database operations

**Parameters:**
- `employee_data` (dict): Employee data to validate

**Returns:**
- `tuple`: (is_valid: bool, error_message: str)

**Example:**
```python
is_valid, error_msg = hr_service.validate_employee_data(employee_data)
if not is_valid:
    print(f"Validation error: {error_msg}")
```

---

## Database Manager API

The `DatabaseManager` class handles all direct database operations.

### Class: DatabaseManager

#### Constructor
```python
class DatabaseManager:
    def __init__(self, connection_string: str = None)
```

**Parameters:**
- `connection_string` (str, optional): MongoDB connection string

#### Connection Methods

#### connect()
```python
def connect(self) -> bool
```

**Purpose**: Establish database connection

**Returns:**
- `bool`: True if connection successful, False otherwise

#### test_connection()
```python
def test_connection(self) -> dict
```

**Purpose**: Test database connectivity

**Returns:**
- `dict`: Connection test result with status and details

#### Data Operations

#### insert_document()
```python
def insert_document(self, collection_name: str, document: dict) -> str
```

**Purpose**: Insert a document into specified collection

**Parameters:**
- `collection_name` (str): Name of the collection
- `document` (dict): Document to insert

**Returns:**
- `str`: Inserted document ID

#### find_documents()
```python
def find_documents(self, collection_name: str, query: dict = None, projection: dict = None) -> list
```

**Purpose**: Find documents matching query

**Parameters:**
- `collection_name` (str): Collection name
- `query` (dict, optional): Query filter
- `projection` (dict, optional): Field projection

**Returns:**
- `list`: List of matching documents

#### update_document()
```python
def update_document(self, collection_name: str, query: dict, update: dict) -> int
```

**Purpose**: Update documents matching query

**Parameters:**
- `collection_name` (str): Collection name
- `query` (dict): Query filter
- `update` (dict): Update operations

**Returns:**
- `int`: Number of documents updated

#### delete_document()
```python
def delete_document(self, collection_name: str, query: dict) -> int
```

**Purpose**: Delete documents matching query

**Parameters:**
- `collection_name` (str): Collection name
- `query` (dict): Query filter

**Returns:**
- `int`: Number of documents deleted

---

## Configuration API

The configuration system manages application settings and environment variables.

### Functions

#### load_config()
```python
def load_config() -> dict
```

**Purpose**: Load configuration from environment variables

**Returns:**
- `dict`: Configuration dictionary

#### get_database_config()
```python
def get_database_config() -> dict
```

**Purpose**: Get database-specific configuration

**Returns:**
- `dict`: Database configuration parameters

#### get_application_path()
```python
def get_application_path() -> str
```

**Purpose**: Get the application directory path (works in both development and executable environments)

**Returns:**
- `str`: Path to application directory

### Configuration Structure
```python
{
    "database": {
        "host": "localhost",
        "port": 27017,
        "name": "business_dashboard",
        "username": "",
        "password": ""
    },
    "application": {
        "name": "Business Dashboard",
        "log_level": "INFO",
        "version": "1.0.0"
    }
}
```

---

## Logger API

The logging system provides comprehensive logging capabilities.

### Functions

#### setup_logger()
```python
def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger
```

**Purpose**: Set up and configure logger instance

**Parameters:**
- `name` (str): Logger name
- `log_level` (str): Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

**Returns:**
- `logging.Logger`: Configured logger instance

### Log Files Structure
```
logs/
├── BusinessDashboard.log              # General application logs
├── BusinessDashboard_database.log     # Database operation logs
├── BusinessDashboard_debug.log        # Debug information
├── BusinessDashboard_errors.log       # Error-specific logs
├── BusinessDashboard_performance.log  # Performance metrics
└── BusinessDashboard_user_activity.log # User interaction logs
```

### Usage Examples
```python
import logging
from logger_config import setup_logger

# Set up logger
logger = setup_logger("BusinessDashboard.module_name")

# Log different levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

---

## Error Handling

### Exception Types

#### Custom Exceptions
```python
class DatabaseConnectionError(Exception):
    """Raised when database connection fails"""
    pass

class ValidationError(Exception):
    """Raised when data validation fails"""
    pass

class EmployeeNotFoundError(Exception):
    """Raised when employee is not found"""
    pass
```

### Error Response Format
```python
{
    "success": False,
    "error": {
        "type": "ValidationError",
        "message": "Employee ID is required",
        "details": {
            "field": "employee_id",
            "value": null,
            "expected": "non-empty string"
        }
    }
}
```

### Error Handling Patterns
```python
try:
    result = hr_service.add_employee(employee_data)
    if result["success"]:
        print("Employee added successfully")
    else:
        print(f"Error: {result['error']['message']}")
except ValidationError as e:
    logger.error(f"Validation error: {e}")
except DatabaseConnectionError as e:
    logger.error(f"Database error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

---

## Data Models

### Employee Model
```python
class Employee:
    def __init__(self):
        self.id: str = None
        self.name: str = ""
        self.employee_id: str = ""
        self.department: str = ""
        self.position: str = ""
        self.salary: float = 0.0
        self.hire_date: str = ""
        self.phone: str = ""
        self.email: str = ""
        self.address: str = ""
        self.attendance_records: list = []
        
    def to_dict(self) -> dict:
        """Convert employee to dictionary"""
        return {
            "_id": self.id,
            "name": self.name,
            "employee_id": self.employee_id,
            "department": self.department,
            "position": self.position,
            "salary": self.salary,
            "hire_date": self.hire_date,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "attendance_records": self.attendance_records
        }
```

### Attendance Model
```python
class AttendanceRecord:
    def __init__(self):
        self.date: str = ""
        self.status: str = ""  # Present, Absent, Leave, Overtime
        self.hours_worked: float = 0.0
        
    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "status": self.status,
            "hours_worked": self.hours_worked
        }
```

---

## Code Examples

### Complete Employee Management Example
```python
from data_service import HRDataService
from database import DatabaseManager
from logger_config import setup_logger

# Initialize components
logger = setup_logger("BusinessDashboard.example")
db_manager = DatabaseManager()
hr_service = HRDataService(db_manager, logger)

# Add new employee
employee_data = {
    "name": "Alice Johnson",
    "employee_id": "EMP002",
    "department": "Marketing",
    "position": "Marketing Manager",
    "salary": 70000.0,
    "hire_date": "2025-02-01",
    "phone": "555-0456",
    "email": "alice.johnson@company.com",
    "address": "456 Oak Street, City, State"
}

# Validate and add employee
is_valid, error_msg = hr_service.validate_employee_data(employee_data)
if is_valid:
    result = hr_service.add_employee(employee_data)
    if result["success"]:
        print(f"Employee added with ID: {result['employee_id']}")
        
        # Add attendance record
        attendance = {
            "date": "2025-09-09",
            "status": "Present",
            "hours_worked": 8.0
        }
        attendance_result = hr_service.add_attendance("EMP002", attendance)
        
        # Get employee statistics
        stats = hr_service.get_employee_statistics()
        print(f"Total employees: {stats['total_employees']}")
        
    else:
        print(f"Failed to add employee: {result['error']['message']}")
else:
    print(f"Validation failed: {error_msg}")
```

### Database Query Example
```python
from database import DatabaseManager

db_manager = DatabaseManager()

# Custom query example
query = {"department": "Engineering", "salary": {"$gte": 60000}}
projection = {"name": 1, "position": 1, "salary": 1}

engineers = db_manager.find_documents("employees", query, projection)
for engineer in engineers:
    print(f"{engineer['name']}: {engineer['position']} - ${engineer['salary']}")
```

---

## Extension Points

### Adding New Data Types
To add new data types (e.g., Projects, Departments):

1. **Create data model** in new module
2. **Extend HRDataService** with new methods
3. **Add GUI components** for new data type
4. **Update database schema** as needed

### Custom Reporting
To add custom reports:

1. **Extend HRDataService** with new statistics methods
2. **Add chart generation** in reports module
3. **Create GUI components** for new reports

### Integration Points
The application can be extended with:
- **REST API** layer for web integration
- **Export/Import** functionality
- **Email notifications**
- **Audit logging**
- **Role-based access control**

---

## Future API Plans

### REST API (Planned)
Future versions may include a REST API for web integration:

```python
# Planned REST endpoints
GET    /api/employees           # Get all employees
POST   /api/employees           # Add new employee
GET    /api/employees/{id}      # Get specific employee
PUT    /api/employees/{id}      # Update employee
DELETE /api/employees/{id}      # Delete employee

GET    /api/attendance/{id}     # Get employee attendance
POST   /api/attendance/{id}     # Add attendance record

GET    /api/statistics          # Get system statistics
GET    /api/reports/{type}      # Generate specific report
```

### Webhook Support (Planned)
Future integration capabilities:
- Employee lifecycle events
- Attendance threshold alerts
- Report generation notifications

### Plugin System (Planned)
Extensible plugin architecture for:
- Custom data sources
- Additional report types
- Integration with external systems

---

*API Documentation Version: 1.0*  
*Last Updated: September 9, 2025*  
*Compatible with Business Dashboard v1.0.0*

This API documentation serves as a foundation for understanding the current codebase and planning future enhancements. As the application evolves, this documentation will be updated to reflect new capabilities and integration points.
