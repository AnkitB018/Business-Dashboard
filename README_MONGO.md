# HR Management System - MongoDB Edition

## Overview
This is a comprehensive HR Management System built with Python Dash and MongoDB. The system allows you to manage employees, attendance, stock/inventory, purchases, and sales with interactive dashboards and reports.

## Features

### Core Modules
- **Employee Management**: Add, edit, delete employee records
- **Attendance Tracking**: Daily attendance with status tracking (Present, Absent, Leave, Half Day, Overtime)
- **Stock Management**: Inventory tracking with automatic updates
- **Purchase Management**: Record purchases and auto-update stock
- **Sales Management**: Process sales with stock validation
- **Reports & Analytics**: Interactive charts and dashboards

### Technical Features
- **MongoDB Database**: Scalable NoSQL database with proper schemas
- **Web Interface**: Modern Dash web application
- **Desktop GUI**: Native Windows interface using tkinter/customtkinter
- **Data Migration**: Seamless migration from Excel to MongoDB
- **Executable Ready**: Can be packaged into standalone executable

## Installation

### Prerequisites
1. **Python 3.8+**
2. **MongoDB** (Community Edition)

### Step 1: Install MongoDB
1. Download MongoDB Community Edition from https://www.mongodb.com/download-center/community
2. Install MongoDB and start the service
3. MongoDB should be running on `localhost:27017`

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database (First Time Setup)
```bash
python migrate_to_mongo.py
```

This will:
- Connect to MongoDB
- Create necessary collections with schemas
- Migrate data from your Excel file (if exists)

## Usage

### Method 1: Web Interface (Recommended)
```bash
python app_mongo.py
```
Then open your browser to `http://127.0.0.1:8050`

### Method 2: Desktop GUI
```bash
python gui_launcher.py
```

## File Structure

```
Business-Dashboard/
├── app_mongo.py              # Main web application
├── gui_launcher.py           # Desktop GUI launcher
├── database.py               # MongoDB connection and operations
├── data_service.py           # Business logic and data operations
├── data_page_mongo.py        # Data management interface
├── reports_page_mongo.py     # Reports and analytics
├── settings_page.py          # Application settings
├── migrate_to_mongo.py       # Data migration script
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── business_data.xlsx        # Sample/migration data (Excel)
└── README.md                 # This file
```

## Data Migration

If you have existing data in Excel format:

1. Place your `business_data.xlsx` file in the project directory
2. Run the migration script:
   ```bash
   python migrate_to_mongo.py
   ```
3. The script will preview your data and ask for confirmation
4. All data will be transferred to MongoDB with proper validation

### Excel File Format
Your Excel file should have these sheets:
- **Employees**: employee_id, name, email, phone, department, position, joining_date, salary
- **Attendance**: date, employee_id, employee_name, status, overtime_hours
- **Stock**: item_name, category, current_quantity, unit_cost_average
- **Purchases**: date, item_name, category, quantity, unit_price, total_price
- **Sales**: date, item_name, category, quantity, unit_price, customer_name, customer_phone

## Database Schema

### Collections
1. **employees**: Employee master data
2. **attendance**: Daily attendance records
3. **stock**: Inventory/stock items
4. **purchases**: Purchase transactions
5. **sales**: Sales transactions

Each collection has validation schemas to ensure data integrity.

## Creating Executable

To create a standalone executable:

### Using PyInstaller
```bash
pip install pyinstaller
pyinstaller --onefile --windowed gui_launcher.py
```

### Using auto-py-to-exe (GUI)
```bash
pip install auto-py-to-exe
auto-py-to-exe
```

Select `gui_launcher.py` as the script and configure as needed.

## Configuration

Edit `config.py` to customize:
- Database connection settings
- Application host/port
- GUI appearance
- Logging settings

## Troubleshooting

### MongoDB Connection Issues
1. Ensure MongoDB service is running
2. Check if port 27017 is available
3. Verify MongoDB installation

### Module Import Errors
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version (3.8+ required)

### Data Migration Issues
1. Verify Excel file format and sheet names
2. Check for data type mismatches
3. Review migration logs for specific errors

## Development

### Adding New Features
1. Update database schemas in `database.py`
2. Add business logic in `data_service.py`
3. Create UI components in respective page files
4. Register callbacks for interactivity

### Testing
Run the application in debug mode:
```bash
python app_mongo.py
```

## Support

For issues and questions:
1. Check the logs in the application
2. Verify MongoDB connection
3. Review error messages in the console

## License

This project is for educational and business use.

## Changelog

### v1.0 - MongoDB Edition
- Migrated from Excel to MongoDB
- Added desktop GUI interface
- Improved data validation and schemas
- Enhanced reporting capabilities
- Added executable packaging support
