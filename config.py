# MongoDB Atlas Configuration
# Copy your connection string from MongoDB Atlas here

# Example format (replace with your actual values):
# MONGODB_URI = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database-name>?retryWrites=true&w=majority"

# Application version for auto-updates
APP_VERSION = "2.1.0"
GITHUB_REPO = "AnkitB018/Business-Dashboard"

# For development, you can also set this as an environment variable
import os
import sys
from dotenv import load_dotenv

def get_application_path(filename=""):
    """Get the correct path for application files, works for both development and executable"""
    try:
        # For PyInstaller executable
        if hasattr(sys, '_MEIPASS'):
            # When running as executable, look in the directory where the .exe is located
            base_path = os.path.dirname(sys.executable)
        else:
            # When running as script, use the script's directory
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        if filename:
            file_path = os.path.join(base_path, filename)
            # If file doesn't exist in base path, try current working directory as fallback
            if not os.path.exists(file_path):
                fallback_path = os.path.join(os.getcwd(), filename)
                if os.path.exists(fallback_path):
                    return fallback_path
            return file_path
        else:
            return base_path
            
    except Exception:
        # Fallback to current working directory
        return os.path.join(os.getcwd(), filename) if filename else os.getcwd()

# Load environment variables from .env file
env_file_path = get_application_path(".env")
load_dotenv(env_file_path)

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'hr_management_db')

# If you prefer to set it directly (not recommended for production):
# MONGODB_URI = "your_atlas_connection_string_here"

# Application Configuration
APP_HOST = "127.0.0.1"
APP_PORT = 8050
DEBUG_MODE = True  # Set to False for production

# GUI Configuration
GUI_THEME = "blue"  # blue, green, dark-blue
GUI_APPEARANCE = "System"  # System, Dark, Light

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Data Configuration
EXCEL_FILE = "business_data.xlsx"
BACKUP_ENABLED = True
BACKUP_INTERVAL_DAYS = 7

# Security (for production)
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Atlas-specific settings
ATLAS_CLUSTER_NAME = os.getenv('ATLAS_CLUSTER_NAME', '')
ATLAS_DATABASE_USER = os.getenv('ATLAS_DATABASE_USER', '')
ATLAS_DATABASE_PASSWORD = os.getenv('ATLAS_DATABASE_PASSWORD', '')
