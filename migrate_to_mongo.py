"""
Migration script to transfer data from Excel to MongoDB
Run this script to migrate your existing Excel data to MongoDB
"""

import pandas as pd
import os
import sys
from datetime import datetime
from database import initialize_database, get_db_manager
from data_service import DataMigration
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_excel_file(excel_file="business_data.xlsx"):
    """Check if Excel file exists and has required sheets"""
    if not os.path.exists(excel_file):
        logger.error(f"Excel file '{excel_file}' not found in current directory")
        return False
    
    try:
        # Check if file can be read
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        required_sheets = ["Employees", "Attendance", "Stock", "Purchases", "Sales"]
        existing_sheets = list(excel_data.keys())
        
        logger.info(f"Found sheets in Excel file: {existing_sheets}")
        
        missing_sheets = [sheet for sheet in required_sheets if sheet not in existing_sheets]
        if missing_sheets:
            logger.warning(f"Missing sheets: {missing_sheets}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return False

def preview_data(excel_file="business_data.xlsx"):
    """Preview the data that will be migrated"""
    try:
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        print("\n" + "="*60)
        print("DATA PREVIEW")
        print("="*60)
        
        for sheet_name, df in excel_data.items():
            print(f"\n{sheet_name} Sheet:")
            print(f"  - Rows: {len(df)}")
            print(f"  - Columns: {list(df.columns)}")
            
            if not df.empty:
                print(f"  - Sample data:")
                print(df.head(2).to_string(index=False))
        
        print("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Error previewing data: {e}")

def main():
    """Main migration function"""
    print("HR Management System - Data Migration Tool")
    print("==========================================")
    
    # Check MongoDB connection
    logger.info("Checking MongoDB connection...")
    db_manager = get_db_manager()
    
    if not db_manager.connect():
        logger.error("Cannot connect to MongoDB. Please ensure MongoDB is running.")
        print("\nMongoDB Connection Failed!")
        print("Please:")
        print("1. Install MongoDB if not installed")
        print("2. Start MongoDB service")
        print("3. Ensure MongoDB is running on default port (27017)")
        return False
    
    logger.info("✅ Connected to MongoDB successfully")
    
    # Initialize database
    logger.info("Initializing database collections...")
    if not initialize_database():
        logger.error("Failed to initialize database")
        return False
    
    logger.info("✅ Database initialized successfully")
    
    # Check Excel file
    excel_file = "business_data.xlsx"
    logger.info(f"Checking Excel file: {excel_file}")
    
    if not check_excel_file(excel_file):
        logger.error("Excel file check failed")
        return False
    
    logger.info("✅ Excel file validation passed")
    
    # Preview data
    preview_data(excel_file)
    
    # Confirm migration
    response = input("\nDo you want to proceed with the migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled.")
        return False
    
    # Perform migration
    logger.info("Starting data migration...")
    migration = DataMigration(excel_file)
    
    try:
        if migration.migrate_from_excel():
            logger.info("✅ Data migration completed successfully!")
            
            # Show migration summary
            print("\n" + "="*60)
            print("MIGRATION SUMMARY")
            print("="*60)
            
            collections = ["employees", "attendance", "stock", "purchases", "sales"]
            for collection in collections:
                try:
                    count = len(db_manager.find_documents(collection))
                    print(f"{collection.capitalize()}: {count} records")
                except Exception as e:
                    print(f"{collection.capitalize()}: Error counting records - {e}")
            
            print("\n✅ Migration completed successfully!")
            print("You can now run the HR Management System with MongoDB.")
            print("\nTo start the application:")
            print("1. python app_mongo.py  (for web interface)")
            print("2. python gui_launcher.py  (for desktop GUI)")
            
            return True
            
        else:
            logger.error("❌ Data migration failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return False
    
    finally:
        # Close database connection
        db_manager.disconnect()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nMigration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
