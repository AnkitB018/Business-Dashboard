# Business Dashboard - Clean Project Structure

## 🧹 **Cleanup Summary**
This project has been cleaned up to remove unnecessary files and duplicates.

## 📁 **Current Project Structure**

### **Core Application Files:**
- `app_gui.py` - Main GUI application entry point
- `config.py` - Application configuration settings
- `database.py` - MongoDB database connection and operations
- `data_service.py` - Data service layer for business logic
- `requirements.txt` - Python package dependencies

### **GUI Components:**
- `data_page_gui.py` - Data management interface
- `reports_page_gui.py` - Reports and analytics interface  
- `settings_page_gui.py` - Settings and configuration interface

### **Data Generation Tools:**
- `generate_local_data.py` - Generate local sample data
- `generate_sample_data.py` - Generate comprehensive sample datasets

### **Sample Data:**
- `sample_data/` - Contains Excel files with sample data
  - `employees.xlsx` - Sample employee records
  - `attendance.xlsx` - Sample attendance data
  - `stock.xlsx` - Sample inventory data
  - `sales.xlsx` - Sample sales records
  - `purchases.xlsx` - Sample purchase data
  - `business_data_complete.xlsx` - Complete business dataset

### **Launcher:**
- `run_business_dashboard.bat` - Windows batch file to launch the application

### **Documentation:**
- `README.md` - Project documentation
- `.env` - Environment configuration (MongoDB credentials)

## 🗑️ **Files Removed:**
- `data_page_gui_new.py` (duplicate)
- `reports_page_gui_new.py` (duplicate)
- `settings_page.py` (old version)
- `business_data.xlsx` (redundant sample data)
- `run_hr_gui.bat` (duplicate launcher)
- `__pycache__/` (Python cache files)
- All `.csv` files in sample_data (kept only `.xlsx`)
- Multiple documentation files (ENHANCEMENT_COMPLETE.md, etc.)

## 🚀 **How to Run:**
1. Double-click `run_business_dashboard.bat`
2. Or run: `python app_gui.py`

## 💾 **Database:**
- Uses MongoDB Atlas cloud database
- Connection configured in `.env` file
- Sample data can be generated using the data generation tools

---
*Last updated: August 30, 2025*
