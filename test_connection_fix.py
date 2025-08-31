"""
Test script to verify the MongoDB test connection functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_connection_function():
    """Test the improved connection test functionality"""
    print("🧪 Testing MongoDB Connection Test Functionality")
    print("=" * 55)
    
    try:
        # Test PyMongo direct connection (same approach as the fixed test)
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        uri = os.getenv('MONGODB_URI', '')
        database = os.getenv('MONGODB_DATABASE', 'DesignoDB')
        
        if not uri:
            print("❌ No MONGODB_URI found in environment variables")
            return False
            
        print(f"📊 Testing connection to database: {database}")
        print(f"🔗 Using URI: {uri[:50]}..." if len(uri) > 50 else f"🔗 Using URI: {uri}")
        print()
        
        # Test connection with same approach as the fixed test
        print("🔄 Testing connection...")
        test_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        try:
            # Test ping
            print("  - Testing ping...")
            test_client.admin.command('ping')
            print("  ✅ Ping successful")
            
            # Test database access
            print("  - Testing database access...")
            test_db = test_client[database]
            collections = test_db.list_collection_names()
            print(f"  ✅ Database access successful")
            print(f"  📋 Found {len(collections)} collections: {', '.join(collections[:5])}")
            
            print()
            print("🎉 Connection test successful!")
            print(f"✅ Database: {database}")
            print(f"✅ Collections: {len(collections)}")
            
            return True
            
        except OperationFailure as e:
            if "authentication failed" in str(e).lower():
                print("❌ Authentication failed - Check username/password")
            else:
                print(f"❌ Database operation failed: {str(e)}")
            return False
                
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            if "dns" in str(e).lower():
                print("❌ DNS error - Check cluster URL")
            else:
                print("❌ Network error - Check internet connection")
            return False
                
        finally:
            test_client.close()
            print("🔒 Test connection closed")
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_database_manager_methods():
    """Test the new ping and list_collections methods"""
    print("\n🧪 Testing MongoDBManager New Methods")
    print("=" * 40)
    
    try:
        from database import get_db_manager
        
        db_manager = get_db_manager()
        
        # Test ping method
        print("🔄 Testing ping method...")
        ping_result = db_manager.ping()
        print(f"  ✅ Ping result: {ping_result}")
        
        # Test list_collections method
        print("🔄 Testing list_collections method...")
        collections = db_manager.list_collections()
        print(f"  ✅ Collections found: {len(collections)}")
        print(f"  📋 Collection names: {', '.join(collections)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database manager methods: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 MongoDB Test Connection Functionality Test")
    print("=" * 60)
    
    # Test 1: Direct connection approach (same as fixed test)
    test1_result = test_connection_function()
    
    # Test 2: New database manager methods
    test2_result = test_database_manager_methods()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"  🧪 Direct Connection Test: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"  🧪 Database Manager Methods: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED - Test connection functionality is working!")
    else:
        print("\n❌ Some tests failed - Please check the implementation")
    print("=" * 60)

if __name__ == "__main__":
    main()
