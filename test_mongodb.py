"""
MongoDB Atlas Connection Test Script
Run this to verify your MongoDB Atlas setup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mongodb_atlas_connection():
    """Test MongoDB Atlas connection with detailed feedback"""
    print("MongoDB Atlas Connection Test")
    print("=" * 50)
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
        
        print("✅ PyMongo imported successfully")
        
        # Try to load configuration
        try:
            from config import MONGODB_URI, MONGODB_DATABASE
            print("✅ Configuration loaded from config.py")
            connection_string = MONGODB_URI
            database_name = MONGODB_DATABASE
        except ImportError:
            print("⚠️ Config.py not found, using environment variables")
            connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            database_name = os.getenv('MONGODB_DATABASE', 'hr_management_db')
        
        print(f"🔄 Database name: {database_name}")
        
        # Hide password in connection string for display
        display_conn = connection_string
        if '@' in display_conn and '://' in display_conn:
            parts = display_conn.split('://')
            if len(parts) == 2 and '@' in parts[1]:
                auth_part = parts[1].split('@')[0]
                if ':' in auth_part:
                    user_pass = auth_part.split(':')
                    display_conn = f"{parts[0]}://{user_pass[0]}:***@{parts[1].split('@', 1)[1]}"
        
        print(f"🔄 Connecting to: {display_conn}")
        
        # Test connection to MongoDB Atlas
        print("\n🔄 Testing connection to MongoDB Atlas...")
        
        try:
            # Create client with longer timeout for Atlas
            client = MongoClient(connection_string, serverSelectionTimeoutMS=10000)
            
            # Test the connection
            print("🔄 Pinging server...")
            client.admin.command('ping')
            print("✅ Connection successful!")
            
            # Get server info
            server_info = client.server_info()
            print(f"✅ MongoDB Version: {server_info['version']}")
            
            # List databases
            databases = client.list_database_names()
            print(f"✅ Available databases: {databases}")
            
            # Test HR database
            hr_db = client[database_name]
            collections = hr_db.list_collection_names()
            print(f"✅ HR database collections: {collections}")
            
            if not collections:
                print("ℹ️ No collections found - database will be created when you add data")
            else:
                # Show collection counts
                for collection in collections:
                    try:
                        count = hr_db[collection].count_documents({})
                        print(f"   📊 {collection}: {count} documents")
                    except Exception as e:
                        print(f"   ❌ Error counting {collection}: {e}")
            
            client.close()
            return True
            
        except ServerSelectionTimeoutError as e:
            print(f"❌ Connection timeout: {e}")
            print("\nTroubleshooting Atlas Connection:")
            print("1. Check your internet connection")
            print("2. Verify your connection string is correct")
            print("3. Ensure your IP address is whitelisted in Atlas")
            print("4. Check username and password")
            print("5. Verify cluster is running in Atlas dashboard")
            return False
            
        except ConnectionFailure as e:
            print(f"❌ Connection failed: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("PyMongo is not installed. Run: pip install pymongo")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def setup_atlas_connection():
    """Help user set up Atlas connection"""
    print("\n" + "=" * 50)
    print("MongoDB Atlas Setup Guide")
    print("=" * 50)
    
    print("""
📋 Steps to set up MongoDB Atlas:

1. 🌐 Go to https://www.mongodb.com/cloud/atlas
2. 🔐 Sign in to your MongoDB Atlas account
3. 🗂️ Select your cluster
4. 🔗 Click 'Connect' button
5. 👤 Choose 'Connect your application'
6. 🐍 Select 'Python' driver version 3.6+
7. 📋 Copy the connection string

📝 Your connection string should look like:
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority

🔧 Setup methods:

Method 1 - Environment Variables (Recommended):
1. Create a .env file in this directory
2. Add: MONGODB_URI=your_connection_string_here
3. Add: MONGODB_DATABASE=hr_management_db

Method 2 - Direct Configuration:
1. Edit config.py file
2. Replace MONGODB_URI with your connection string

⚠️ Important Atlas Settings:
- Whitelist your IP address (0.0.0.0/0 for development)
- Create a database user with read/write permissions
- Choose a strong password
- Note down your cluster name and database name

🔒 Security Notes:
- Never commit your .env file to version control
- Use environment variables in production
- Regularly rotate your database passwords
""")

def check_env_file():
    """Check if .env file exists and is configured"""
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        with open('.env', 'r') as f:
            content = f.read()
            
        if 'MONGODB_URI=' in content and 'your_username' not in content:
            print("✅ .env file appears to be configured")
            return True
        else:
            print("⚠️ .env file exists but may not be configured properly")
            return False
    else:
        print("⚠️ .env file not found")
        print("📋 You can copy .env.template to .env and configure it")
        return False

if __name__ == "__main__":
    print("🚀 Starting MongoDB Atlas connection test...\n")
    
    # Check environment file
    print("🔍 Checking environment configuration...")
    env_ok = check_env_file()
    
    print("\n" + "-" * 50)
    
    # Test connection
    success = test_mongodb_atlas_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 MongoDB Atlas connection test PASSED!")
        print("✅ You can now run the HR Management System")
        print("\nNext steps:")
        print("1. Run: python migrate_to_mongo.py (if you have Excel data)")
        print("2. Run: python app_mongo.py (for web interface)")
        print("3. Run: python gui_launcher.py (for desktop GUI)")
    else:
        print("❌ MongoDB Atlas connection test FAILED!")
        
        if not env_ok:
            setup_atlas_connection()
        else:
            print("\nPlease check your MongoDB Atlas configuration:")
            print("- Verify connection string in .env file")
            print("- Check IP whitelist in Atlas dashboard")
            print("- Verify username and password")
            print("- Ensure cluster is running")
    
    input("\nPress Enter to exit...")
