#!/usr/bin/env python3
"""
Test script to verify customer management UI works correctly
"""

import sys
import os
from tkinter import messagebox

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_service import HRDataService

def test_customer_data():
    """Test if customer data can be retrieved properly"""
    try:
        # Initialize data service
        service = HRDataService()
        
        # Test getting customers
        customers = service.get_customers()
        print(f"✅ Successfully retrieved {len(customers)} customers")
        
        if not customers.empty:
            print("📋 Customer data preview:")
            for _, customer in customers.iterrows():
                print(f"  - {customer.get('name', 'N/A')} | {customer.get('contact_number', 'N/A')} | Due: ₹{customer.get('due_payment', 0):.2f}")
        else:
            print("⚠️ No customers found in database")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing customer data: {str(e)}")
        return False

def test_customer_methods():
    """Test if all customer management methods exist"""
    try:
        service = HRDataService()
        
        # Check if all required methods exist
        methods = [
            'get_customers',
            'add_customer', 
            'update_customer',
            'delete_customer',
            'calculate_customer_due_payment',
            'get_customer_by_name',
            'update_all_customer_due_payments'
        ]
        
        for method in methods:
            if hasattr(service, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing methods: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Customer Management System")
    print("=" * 50)
    
    # Test data service methods
    if test_customer_methods():
        print("\n✅ All customer management methods found")
    else:
        print("\n❌ Some customer management methods are missing")
        
    # Test data retrieval
    if test_customer_data():
        print("\n✅ Customer data retrieval works correctly")
    else:
        print("\n❌ Customer data retrieval failed")
        
    print("\n🏁 Customer management test completed!")
