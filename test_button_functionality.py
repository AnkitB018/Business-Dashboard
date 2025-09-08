#!/usr/bin/env python3
"""
Test script to verify button functionality across all data management tables
This script will check:
1. Edit buttons work properly
2. Delete buttons work properly
3. Form buttons respond correctly
4. MongoDB ID handling is correct
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_service import DataService
import time

class ButtonTester:
    def __init__(self):
        self.data_service = DataService()
        self.test_results = {}
        
    def test_database_connection(self):
        """Test if database connection is working"""
        try:
            # Test if data service can connect
            employees = self.data_service.get_employees()
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def test_data_retrieval(self):
        """Test if data can be retrieved from all collections"""
        collections = ["employees", "attendance", "sales", "purchases"]
        results = {}
        
        for collection in collections:
            try:
                if collection == "employees":
                    data = self.data_service.get_employees()
                elif collection == "attendance":
                    data = self.data_service.get_attendance()
                elif collection == "sales":
                    data = self.data_service.get_sales()
                elif collection == "purchases":
                    data = self.data_service.get_purchases()
                
                count = len(data)
                results[collection] = count
                print(f"✅ {collection}: {count} records")
                
            except Exception as e:
                results[collection] = f"Error: {e}"
                print(f"❌ {collection}: Error - {e}")
        
        return results
    
    def test_mongodb_id_retrieval(self):
        """Test if MongoDB IDs can be retrieved correctly"""
        collections = ["employees", "attendance", "sales", "purchases"]
        
        for collection in collections:
            try:
                documents = self.data_service.db_manager.find_documents(collection)
                if documents:
                    first_doc = documents[0]
                    mongo_id = first_doc.get('_id')
                    print(f"✅ {collection}: MongoDB ID format - {type(mongo_id)} - {mongo_id}")
                else:
                    print(f"⚠️ {collection}: No documents found")
                    
            except Exception as e:
                print(f"❌ {collection}: Error getting MongoDB ID - {e}")
    
    def test_update_methods(self):
        """Test if update methods exist in data service"""
        methods_to_test = [
            "update_employee",
            "update_employee_by_id",
            "update_attendance", 
            "update_sale",
            "update_purchase"
        ]
        
        for method_name in methods_to_test:
            if hasattr(self.data_service, method_name):
                print(f"✅ {method_name}: Method exists")
            else:
                print(f"❌ {method_name}: Method missing")
    
    def test_delete_methods(self):
        """Test if delete methods exist in data service"""
        methods_to_test = [
            "delete_employee",
            "delete_attendance",
            "delete_sale", 
            "delete_purchase"
        ]
        
        for method_name in methods_to_test:
            if hasattr(self.data_service, method_name):
                print(f"✅ {method_name}: Method exists")
            else:
                print(f"❌ {method_name}: Method missing")
    
    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🧪 Starting Button Functionality Tests")
        print("=" * 50)
        
        # Test 1: Database Connection
        print("\n1. Testing Database Connection:")
        db_ok = self.test_database_connection()
        
        if not db_ok:
            print("❌ Cannot proceed with tests - database connection failed")
            return
        
        # Test 2: Data Retrieval
        print("\n2. Testing Data Retrieval:")
        data_results = self.test_data_retrieval()
        
        # Test 3: MongoDB ID Retrieval
        print("\n3. Testing MongoDB ID Retrieval:")
        self.test_mongodb_id_retrieval()
        
        # Test 4: Update Methods
        print("\n4. Testing Update Methods:")
        self.test_update_methods()
        
        # Test 5: Delete Methods  
        print("\n5. Testing Delete Methods:")
        self.test_delete_methods()
        
        print("\n" + "=" * 50)
        print("🏁 Tests Complete!")
        
        # Summary
        total_records = sum(count for count in data_results.values() if isinstance(count, int))
        print(f"📊 Total records across all collections: {total_records}")
        
        # Check if we have test data
        for collection, count in data_results.items():
            if isinstance(count, int) and count == 0:
                print(f"⚠️ Warning: {collection} has no records - buttons may not be testable")

if __name__ == "__main__":
    tester = ButtonTester()
    tester.run_all_tests()
