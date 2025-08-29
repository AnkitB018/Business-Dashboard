# 🚀 MongoDB Atlas Setup Guide for HR Management System

## Quick Setup (5 minutes)

### Step 1: Get Your MongoDB Atlas Connection String

1. Go to your **MongoDB Atlas Dashboard**: https://cloud.mongodb.com/
2. Select your **Cluster**
3. Click the **"Connect"** button
4. Choose **"Connect your application"**
5. Select **Python** and version **3.6+**
6. **Copy** the connection string (it looks like this):
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/<database>?retryWrites=true&w=majority
   ```

### Step 2: Configure the Application

**Option A: Using .env file (Recommended)**

1. Copy the template file:
   ```bash
   copy .env.template .env
   ```

2. Edit the `.env` file and replace with your actual values:
   ```
   MONGODB_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/hr_management_db?retryWrites=true&w=majority
   MONGODB_DATABASE=hr_management_db
   ```

**Option B: Direct configuration**

1. Edit `config.py` file
2. Find the line with `MONGODB_URI` and replace with your connection string

### Step 3: Test the Connection

Run the test script:
```bash
python test_mongodb.py
```

If successful, you should see:
```
🎉 MongoDB Atlas connection test PASSED!
```

### Step 4: Initialize the Database

```bash
python migrate_to_mongo.py
```

### Step 5: Run the Application

Choose one option:

**Web Interface:**
```bash
python app_mongo.py
```
Then open: http://127.0.0.1:8050

**Desktop GUI:**
```bash
python gui_launcher.py
```

**Windows Batch File:**
```bash
run_hr_system.bat
```

---

## 🔧 MongoDB Atlas Configuration Checklist

### ✅ Security Settings

1. **Network Access** (IP Whitelist):
   - Go to "Network Access" in Atlas
   - Add IP Address: `0.0.0.0/0` (allows access from anywhere - for development)
   - For production: Add only your specific IP addresses

2. **Database Access** (Users):
   - Go to "Database Access" in Atlas
   - Create a user with "Read and write to any database" privileges
   - Use a strong password
   - Note down username and password

### ✅ Connection Settings

1. **Cluster Status**: Ensure your cluster is running (green status)
2. **Connection String**: Must include:
   - Correct username and password
   - Correct cluster URL
   - Database name (hr_management_db)
   - SSL enabled (retryWrites=true&w=majority)

---

## 🐛 Troubleshooting

### Connection Issues

**Error: "ServerSelectionTimeoutError"**
- Check your internet connection
- Verify IP whitelist in Atlas
- Confirm cluster is running

**Error: "Authentication failed"**
- Check username and password in connection string
- Verify user exists in Database Access
- Ensure user has proper permissions

**Error: "No module named 'pymongo'"**
- Run: `pip install pymongo`
- Or use the virtual environment pip

### Configuration Issues

**Error: "Config file not found"**
- Ensure .env file exists in project root
- Check .env file has correct format
- No spaces around = sign in .env file

**Error: "Invalid connection string"**
- Ensure no extra characters in connection string
- Check all parts are properly formatted
- Verify database name is included

---

## 📝 Example .env File

```bash
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://hruser:mypassword123@cluster0.abc123.mongodb.net/hr_management_db?retryWrites=true&w=majority
MONGODB_DATABASE=hr_management_db

# Optional settings
DEBUG_MODE=True
SECRET_KEY=my-secret-key-for-production
```

---

## 🎯 Next Steps After Setup

1. **Data Migration**: If you have existing Excel data, run the migration
2. **User Testing**: Test all features (employees, attendance, stock, etc.)
3. **Backup Strategy**: Set up regular data exports
4. **Production Deployment**: Create executable for client distribution

---

## 📞 Support

If you encounter issues:

1. Run `python test_mongodb.py` for detailed diagnostics
2. Check the application logs
3. Verify Atlas dashboard shows active connections
4. Test connection string in MongoDB Compass (optional GUI tool)

---

**🎉 You're all set! The HR Management System is ready to use with MongoDB Atlas.**
