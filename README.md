# 🏢 Business Dashboard - Enterprise Edition

A comprehensive business management system built with Python and CustomTkinter, featuring modern UI design and MongoDB Atlas integration.

## ✨ Features

### 📊 **Data Management**
- **Employee Management:** Complete CRUD operations for employee records
- **Attendance Tracking:** Comprehensive attendance system with calendar view
- **Inventory Management:** Stock tracking with automatic purchase/sales integration
- **Financial Records:** Sales and purchase management

### 📈 **Reports & Analytics**
- **Interactive Calendar:** Visual attendance tracking with color-coded status
- **Employee Analytics:** Detailed employee performance metrics
- **Financial Reports:** Revenue, expenses, and profit analysis
- **Inventory Dashboard:** Stock levels, reorder alerts, and trends

### ⚙️ **Settings & Configuration**
- **Database Management:** MongoDB Atlas configuration and connection
- **Data Import/Export:** Excel-based backup and restore functionality
- **Theme Toggle:** Dark/Light mode support
- **System Preferences:** Customizable application settings

## 🚀 **Quick Start**

### Prerequisites
- Python 3.8+
- MongoDB Atlas account (free tier available)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AnkitB018/Business-Dashboard.git
   cd Business-Dashboard
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database:**
   - Create a `.env` file with your MongoDB Atlas connection string
   - Or use the Settings page to configure the database

5. **Run the application:**
   ```bash
   python app_gui.py
   # or
   run_business_dashboard.bat  # Windows
   ```

## 🗂️ **Project Structure**

```
Business-Dashboard/
├── app_gui.py              # Main application entry point
├── data_page_gui.py        # Data management interface
├── reports_page_gui.py     # Reports and analytics interface
├── settings_page_gui.py    # Settings and configuration
├── data_service.py         # Business logic and data operations
├── database.py             # MongoDB Atlas connection manager
├── config.py               # Application configuration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── sample_data/           # Sample data files for testing
└── README.md              # This file
```

## 🎨 **Modern UI Design**

- **CustomTkinter Framework:** Modern, native-looking interface
- **Professional Color Scheme:** Carefully chosen colors for optimal UX
- **Responsive Layout:** Adapts to different screen sizes
- **Theme Support:** Built-in dark/light mode toggle
- **Visual Feedback:** Hover effects, status indicators, and animations

## 🔧 **Technical Stack**

- **Frontend:** CustomTkinter (Modern Tkinter alternative)
- **Backend:** Python with pandas for data processing
- **Database:** MongoDB Atlas (Cloud database)
- **Visualization:** Matplotlib, Seaborn for charts and graphs
- **Data Export:** Excel support via openpyxl

## 📝 **Usage**

1. **Data Management:** Use the Data tab to add employees, record attendance, manage inventory
2. **View Reports:** Check the Reports tab for analytics and calendar views
3. **Configure System:** Use Settings tab for database setup and data management
4. **Export Data:** Backup your data to Excel files for external use

## 🛠️ **Development**

### Adding New Features
- Follow the modular structure established in the codebase
- Use the existing color scheme and UI patterns
- Ensure database operations go through `data_service.py`

### Database Schema
The application uses MongoDB with the following collections:
- `employees` - Employee records
- `attendance` - Daily attendance data
- `stock` - Inventory items
- `sales` - Sales transactions
- `purchases` - Purchase records

## � **License**

**© 2025 Antrocraft and Arolive Build. All Rights Reserved.**

This software is proprietary and licensed exclusively to M/s Designo (Owner: Anupam Das) for internal business operations. 

**⚠️ IMPORTANT**: Unauthorized use, copying, distribution, or sharing is strictly prohibited.

For complete license terms, see [LICENSE.md](LICENSE.md)

## 📧 **Support**

**Licensed Business Entity**: M/s Designo  
**Owner**: Anupam Das  

**Software Created by**: Antrocraft and Arolive Build  
**Owned by**: Ankit Banerjee and Aritra Banerjee  

For technical support or licensing inquiries, please contact the appropriate representatives.

---

**Built with ❤️ by Antrocraft and Arolive Build**  
**© 2025 - All Rights Reserved**
