# Business Dashboard - Installation & Setup Guide

## Table of Contents
1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Pre-Installation Checklist](#pre-installation-checklist)
4. [MongoDB Setup](#mongodb-setup)
5. [Application Installation](#application-installation)
6. [Initial Configuration](#initial-configuration)
7. [Verification Steps](#verification-steps)
8. [Troubleshooting Installation](#troubleshooting-installation)
9. [Uninstallation Guide](#uninstallation-guide)
10. [Advanced Configuration](#advanced-configuration)

---

## Overview

This guide provides step-by-step instructions for installing and setting up the Business Dashboard application. Whether you're setting up for a single user or multiple users in an organization, this guide will help you get the system running smoothly.

### Installation Methods
- **🎯 Recommended**: Standalone Executable (for end users)
- **👨‍💻 Advanced**: Source Code Installation (for developers)
- **🏢 Enterprise**: Network Deployment (for multiple users)

### Time Required
- **Basic Setup**: 15-30 minutes
- **Complete Configuration**: 45-60 minutes
- **Testing and Verification**: 15 minutes

---

## System Requirements

### Minimum System Requirements

#### Hardware
- **Processor**: Intel i3 / AMD Ryzen 3 or equivalent
- **RAM**: 4 GB minimum
- **Storage**: 500 MB free space
- **Display**: 1366x768 resolution minimum
- **Network**: Internet connection for MongoDB setup

#### Software
- **Operating System**: Windows 10 (version 1903 or later)
- **Database**: MongoDB 5.0 or later
- **Runtime**: Included with executable (Python 3.13+ if running from source)

### Recommended System Requirements

#### Hardware
- **Processor**: Intel i5 / AMD Ryzen 5 or better
- **RAM**: 8 GB or more
- **Storage**: 2 GB free space
- **Display**: 1920x1080 resolution or higher
- **Network**: Stable internet connection

#### Software
- **Operating System**: Windows 11
- **Database**: MongoDB 7.0 or later
- **Antivirus**: Windows Defender or compatible security software

---

## Pre-Installation Checklist

### Before You Begin
- [ ] **System Administrator Access**: Ensure you have administrator rights
- [ ] **Network Access**: Verify internet connectivity
- [ ] **Firewall Configuration**: Check firewall settings
- [ ] **Antivirus Exclusions**: Add application folder to exclusions
- [ ] **Backup Existing Data**: If upgrading from a previous version
- [ ] **Close Running Applications**: Especially database-related programs

### Information You'll Need
- [ ] **MongoDB Connection Details**:
  - Host address (localhost for local installation)
  - Port number (default: 27017)
  - Database name preference
  - Username and password (if authentication required)
- [ ] **Application Settings**:
  - Installation directory preference
  - Log level preference
  - User access requirements

---

## MongoDB Setup

### Option 1: Local MongoDB Installation (Recommended for Single User)

#### Download and Install MongoDB Community Edition

1. **Visit MongoDB Download Center**:
   - Go to: https://www.mongodb.com/try/download/community
   - Select "Windows" platform
   - Choose "msi" package

2. **Run the Installer**:
   - Double-click the downloaded .msi file
   - Choose "Complete" installation type
   - **Important**: Check "Install MongoDB as a Service"
   - **Important**: Check "Install MongoDB Compass" (GUI tool)

3. **Complete Installation**:
   - Click "Install" and wait for completion
   - Allow Windows Firewall exceptions when prompted

#### Verify MongoDB Installation

1. **Check Service Status**:
   - Open Windows Services (services.msc)
   - Find "MongoDB" service
   - Ensure status is "Running"

2. **Test Connection**:
   - Open Command Prompt as Administrator
   - Run: `mongo --version`
   - Should display MongoDB version information

### Option 2: MongoDB Atlas (Cloud Database)

#### Create Atlas Account
1. **Visit MongoDB Atlas**: https://www.mongodb.com/atlas
2. **Sign up** for a free account
3. **Create a new cluster** (M0 Sandbox is free)
4. **Configure network access**:
   - Add your IP address to whitelist
   - Or allow access from anywhere (0.0.0.0/0) for testing

#### Get Connection String
1. **Click "Connect"** on your cluster
2. **Choose "Connect your application"**
3. **Copy the connection string**
4. **Note down**:
   - Host address
   - Username and password
   - Database name

### Option 3: Existing MongoDB Server

If you have an existing MongoDB server:
- [ ] **Note the host address** (IP or domain name)
- [ ] **Note the port number** (usually 27017)
- [ ] **Obtain username and password** (if authentication is enabled)
- [ ] **Test connectivity** from the target machine

---

## Application Installation

### Method 1: Standalone Executable Installation (Recommended)

#### Download Application
1. **Obtain BusinessDashboard.exe** from the provided source
2. **Choose installation location** (e.g., `C:\Program Files\BusinessDashboard\`)
3. **Create application folder** if it doesn't exist

#### Install Application
1. **Copy the executable** to your chosen directory
2. **Create desktop shortcut** (optional):
   - Right-click on BusinessDashboard.exe
   - Select "Create shortcut"
   - Move shortcut to desktop

3. **Set up configuration files**:
   - The application will create necessary files on first run
   - Ensure the folder has write permissions

#### Verify Installation
1. **Right-click** on BusinessDashboard.exe
2. **Select "Properties"**
3. **Go to "Compatibility" tab**
4. **Ensure "Run as administrator"** is unchecked (unless required)

### Method 2: Source Code Installation (For Developers)

#### Prerequisites
1. **Install Python 3.13+**:
   - Download from: https://www.python.org/downloads/
   - **Important**: Check "Add Python to PATH" during installation
   - **Important**: Choose "Add Python to environment variables"

2. **Install Git** (optional, for cloning repository):
   - Download from: https://git-scm.com/download/win

#### Download Source Code
```powershell
# Option A: Clone from repository
git clone <repository-url>
cd Business-Dashboard

# Option B: Download and extract ZIP file
# Extract to desired directory
cd Business-Dashboard
```

#### Set Up Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip
```

#### Install Dependencies
```powershell
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Create Configuration Files
```powershell
# Copy environment template
copy .env.example .env

# Edit .env file with your settings
notepad .env
```

---

## Initial Configuration

### Step 1: First Application Launch

#### Using Executable
1. **Double-click** BusinessDashboard.exe
2. **Allow Windows Firewall** access if prompted
3. **Wait for application** to load (may take 30-60 seconds on first run)

#### Using Source Code
```powershell
# Ensure virtual environment is activated
.venv\Scripts\Activate.ps1

# Run the application
python app_gui.py
```

### Step 2: Database Configuration

#### Open Settings Tab
1. **Click on "Settings" tab** in the application
2. **Navigate to "Database Settings" section**

#### Configure MongoDB Connection

**For Local MongoDB**:
```
Host: localhost
Port: 27017
Database Name: business_dashboard
Username: (leave blank)
Password: (leave blank)
```

**For MongoDB Atlas**:
```
Host: <your-cluster-url>
Port: 27017
Database Name: <your-database-name>
Username: <your-username>
Password: <your-password>
```

**For Remote MongoDB Server**:
```
Host: <server-ip-or-domain>
Port: <port-number>
Database Name: <database-name>
Username: <username>
Password: <password>
```

### Step 3: Test Database Connection

1. **Click "Test Connection"** button
2. **Wait for result**:
   - ✅ **Success**: "Connection successful!" message
   - ❌ **Failed**: Error message with details

3. **If connection fails**:
   - Double-check all connection parameters
   - Verify MongoDB is running
   - Check network connectivity
   - Review firewall settings

### Step 4: Save Configuration

1. **Click "Save Database Settings"** button
2. **Wait for confirmation**: "Settings saved successfully!"
3. **Restart application** to apply changes (if prompted)

---

## Verification Steps

### Test 1: Application Startup
- [ ] Application opens without errors
- [ ] All three tabs are visible (Data Management, Reports, Settings)
- [ ] No error messages in the interface
- [ ] Application responds to clicks and navigation

### Test 2: Database Connectivity
- [ ] Database connection test passes
- [ ] Settings save successfully
- [ ] No database-related error messages
- [ ] Connection parameters are persistent after restart

### Test 3: Core Functionality
#### Add Test Employee
1. **Go to Data Management tab**
2. **Fill in employee form**:
   ```
   Name: Test Employee
   Employee ID: TEST001
   Department: IT
   Position: Test Position
   Salary: 50000
   Hire Date: Today's date
   Phone: 555-0123
   Email: test@company.com
   Address: Test Address
   ```
3. **Click "Add Employee"**
4. **Verify employee appears** in the list

#### Test Reports
1. **Go to Reports tab**
2. **Check if statistics display** (may show "No data" initially)
3. **Verify charts area loads** without errors

### Test 4: Data Persistence
1. **Close the application** completely
2. **Restart the application**
3. **Verify test employee** still appears in the list
4. **Check that settings** are preserved

---

## Troubleshooting Installation

### Common Installation Issues

#### Issue: "Application failed to start"
**Symptoms**: Double-clicking executable does nothing or shows error

**Solutions**:
1. **Run as Administrator**:
   - Right-click BusinessDashboard.exe
   - Select "Run as administrator"

2. **Check System Requirements**:
   - Verify Windows 10 version 1903+
   - Ensure sufficient RAM and disk space

3. **Antivirus Interference**:
   - Add application folder to antivirus exclusions
   - Temporarily disable real-time protection for testing

4. **Missing System Libraries**:
   - Install Visual C++ Redistributable
   - Update Windows to latest version

#### Issue: "MongoDB connection failed"
**Symptoms**: Database test connection fails

**Solutions**:
1. **Local MongoDB Issues**:
   ```powershell
   # Check if MongoDB service is running
   Get-Service -Name MongoDB
   
   # Start MongoDB service if stopped
   Start-Service -Name MongoDB
   ```

2. **Network Issues**:
   - Test network connectivity: `ping <mongodb-host>`
   - Check firewall rules for port 27017
   - Verify VPN/proxy settings

3. **Authentication Issues**:
   - Verify username and password
   - Check database user permissions
   - Ensure database exists

#### Issue: "Permission denied" errors
**Symptoms**: Application can't save settings or create files

**Solutions**:
1. **Folder Permissions**:
   - Right-click application folder
   - Properties → Security → Edit
   - Give "Full control" to current user

2. **Alternative Location**:
   - Move application to user documents folder
   - Avoid system directories like Program Files

#### Issue: Python/Source Code Issues
**Symptoms**: Errors when running from source code

**Solutions**:
1. **Python Version**:
   ```powershell
   # Check Python version
   python --version
   # Should be 3.13 or later
   ```

2. **Virtual Environment**:
   ```powershell
   # Recreate virtual environment
   Remove-Item -Recurse -Force .venv
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Dependencies**:
   ```powershell
   # Update all packages
   pip install --upgrade -r requirements.txt
   ```

### Advanced Troubleshooting

#### Enable Debug Logging
1. **Edit .env file** (create if doesn't exist):
   ```
   LOG_LEVEL=DEBUG
   ```
2. **Restart application**
3. **Check logs** in `logs/` folder
4. **Review detailed error messages**

#### Network Diagnostics
```powershell
# Test MongoDB connectivity
telnet <mongodb-host> 27017

# Check DNS resolution
nslookup <mongodb-host>

# Test with MongoDB connection string
# (requires MongoDB tools)
mongosh "mongodb://<host>:<port>/<database>"
```

#### System Information
```powershell
# Check system specs
systeminfo

# Check available disk space
Get-PSDrive -PSProvider FileSystem

# Check running services
Get-Service | Where-Object {$_.Name -like "*mongo*"}
```

---

## Uninstallation Guide

### Remove Application

#### Executable Installation
1. **Close the application** completely
2. **Delete application folder** and all contents
3. **Remove desktop shortcuts**
4. **Clean up Start Menu entries** (if any)

#### Source Code Installation
1. **Close the application**
2. **Deactivate virtual environment**:
   ```powershell
   deactivate
   ```
3. **Delete project folder** and all contents

### Remove MongoDB (Optional)

⚠️ **Warning**: Only do this if MongoDB is not used by other applications

#### Local MongoDB
1. **Stop MongoDB service**:
   ```powershell
   Stop-Service -Name MongoDB
   ```
2. **Uninstall via Control Panel**:
   - Programs → Uninstall a program
   - Find and uninstall MongoDB
3. **Remove data directories**:
   - `C:\Program Files\MongoDB\`
   - `C:\data\db\` (default data directory)

### Clean Up Configuration
1. **Remove .env files** (if desired)
2. **Remove log files** (in logs/ directory)
3. **Clean up user data** (if switching to different system)

---

## Advanced Configuration

### Network Deployment

#### Shared Database Setup
For multiple users sharing the same database:

1. **Set up central MongoDB server**
2. **Configure network access** and security
3. **Provide connection details** to all users
4. **Ensure consistent application versions**

#### Security Configuration
```env
# .env file with security settings
MONGO_HOST=secure-mongodb-server.company.com
MONGO_PORT=27017
MONGO_DB=company_hr_system
MONGO_USERNAME=hr_user
MONGO_PASSWORD=secure_password_here
LOG_LEVEL=INFO
```

### Performance Tuning

#### For Large Datasets
```env
# Optimized settings for large data
MONGO_POOL_SIZE=10
MONGO_TIMEOUT=30000
LOG_LEVEL=WARNING
CACHE_SIZE=100
```

#### For Slow Networks
```env
# Settings for slow/unreliable networks
MONGO_TIMEOUT=60000
RETRY_ATTEMPTS=5
CONNECTION_POOL_MIN=1
CONNECTION_POOL_MAX=5
```

### Backup Configuration

#### Automated Backups
1. **Create backup script** for MongoDB:
   ```powershell
   # backup_script.ps1
   $date = Get-Date -Format "yyyy-MM-dd"
   mongodump --host localhost --port 27017 --db business_dashboard --out "C:\Backups\MongoDB\$date"
   ```

2. **Schedule with Task Scheduler**:
   - Open Task Scheduler
   - Create Basic Task
   - Set to run daily/weekly
   - Action: Start PowerShell script

#### Configuration Backup
```powershell
# Backup configuration files
$date = Get-Date -Format "yyyy-MM-dd"
Copy-Item .env "backups\.env.$date"
Copy-Item logs\ "backups\logs-$date\" -Recurse
```

---

## Next Steps

### Post-Installation Tasks
- [ ] **Train Users**: Provide user manual and basic training
- [ ] **Set Up Backups**: Implement regular backup procedures
- [ ] **Monitor Performance**: Check application and database performance
- [ ] **Plan Maintenance**: Schedule regular maintenance windows
- [ ] **Document Configuration**: Keep record of all settings and customizations

### Ongoing Maintenance
- [ ] **Regular Updates**: Check for application updates
- [ ] **Database Maintenance**: Monitor database size and performance
- [ ] **Log Review**: Periodically review log files for issues
- [ ] **Security Checks**: Review and update security settings
- [ ] **User Feedback**: Collect feedback and plan improvements

---

*Installation Guide Version: 1.0*  
*Last Updated: September 9, 2025*  
*Compatible with Business Dashboard v1.0.0*

**Congratulations!** 🎉 Your Business Dashboard should now be fully installed and configured. If you encounter any issues not covered in this guide, please refer to the Technical Documentation or User Manual for additional help.
