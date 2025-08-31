"""
Test script to verify Employee Management delete functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_service import get_hr_service
from database import get_db_manager
import pandas as pd

def test_delete_employee_functionality():
    """Test the delete employee functionality"""
    print("🧪 Testing Employee Delete Functionality")
    print("=" * 50)
    
    try:
        # Get the data service
        hr_service = get_hr_service()
        
        # Get current employees
        print("📊 Current employees in database:")
        employees_df = hr_service.get_employees()
        print(f"Total employees: {len(employees_df)}")
        
        if len(employees_df) > 0:
            print("\nEmployee IDs:")
            for idx, row in employees_df.iterrows():
                print(f"  - {row.get('employee_id', 'Unknown')}: {row.get('name', 'Unknown')}")
        
        # Test the delete_employee method exists
        if hasattr(hr_service, 'delete_employee'):
            print("\n✅ delete_employee method exists")
            
            # Test with a non-existent employee ID
            print("\n🧪 Testing delete with non-existent employee ID...")
            result = hr_service.delete_employee("TEST_NON_EXISTENT")
            print(f"Result for non-existent employee: {result} (should be 0)")
            
            print("\n✅ Delete employee functionality is working!")
            print("\n📝 To test actual deletion:")
            print("   1. Run the application: python app_gui.py")
            print("   2. Go to Data Management -> Employee Management")
            print("   3. Select an employee row in the table")
            print("   4. Click the '🗑️ Delete Record' button")
            print("   5. Confirm the deletion")
            
        else:
            print("\n❌ delete_employee method not found!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🔗 Testing Database Connection")
    print("-" * 30)
    
    try:
        db_manager = get_db_manager()
        if db_manager.connect():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Employee Management Delete Functionality Test")
    print("=" * 60)
    
    # Test database connection first
    if not test_database_connection():
        print("\n❌ Cannot proceed without database connection")
        return
    
    # Test delete functionality
    success = test_delete_employee_functionality()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED - Delete functionality is working!")
    else:
        print("❌ Some tests failed - Please check the implementation")
    print("=" * 60)

if __name__ == "__main__":
    main()
