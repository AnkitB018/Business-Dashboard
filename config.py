# MongoDB Atlas Configuration
# Copy your connection string from MongoDB Atlas here

# Example format (replace with your actual values):
# MONGODB_URI = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database-name>?retryWrites=true&w=majority"

# For development, you can also set this as an environment variable
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
