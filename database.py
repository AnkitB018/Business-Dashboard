import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from bson import ObjectId
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import time

# Import enhanced logging
from logger_config import get_logger, log_function_call, log_info, log_error

# Import configuration
try:
    from config import MONGODB_URI, MONGODB_DATABASE
except ImportError:
    # Fallback configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'hr_management_db')

# Import database configuration
try:
    from database_config import get_database_config
except ImportError:
    get_database_config = None

# Initialize enhanced logging
dashboard_logger = get_logger()
logger = dashboard_logger.db_logger

class MongoDBManager:
    """
    MongoDB connection and operations manager for HR Management System
    """
    
    def __init__(self, connection_string: str = None, database_name: str = None):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string (defaults to config or local)
            database_name: Name of the database to use
        """
        # Try to get user configuration first
        if get_database_config and not connection_string:
            user_config = get_database_config()
            if user_config and user_config.get('configured'):
                self.connection_string = user_config.get('mongodb_uri')
                self.database_name = user_config.get('database_name')
            else:
                self.connection_string = connection_string or MONGODB_URI
                self.database_name = database_name or MONGODB_DATABASE
        else:
            self.connection_string = connection_string or MONGODB_URI
            self.database_name = database_name or MONGODB_DATABASE
            
        self.client = None
        self.db = None
        self.connect()
    
    @log_function_call
    def connect(self) -> bool:
        """
        Establish connection to MongoDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        start_time = time.time()
        try:
            log_info(f"Attempting to connect to MongoDB database: {self.database_name}", "DB_CONNECT")
            dashboard_logger.log_database_operation("connect", "database", {"database": self.database_name})
            
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            
            duration = (time.time() - start_time) * 1000
            log_info(f"Successfully connected to MongoDB: {self.database_name} in {duration:.2f}ms", "DB_CONNECT")
            dashboard_logger.log_database_operation("connect", "database", 
                                                   {"database": self.database_name}, 
                                                   {"success": True}, duration)
            return True
            
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            duration = (time.time() - start_time) * 1000
            log_error(e, "DB_CONNECT")
            dashboard_logger.log_database_operation("connect", "database", 
                                                   {"database": self.database_name}, 
                                                   {"success": False, "error": str(e)}, duration)
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def ping(self):
        """Test database connectivity"""
        try:
            if self.client is None:
                return False
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database ping failed: {e}")
            return False
    
    def list_collections(self):
        """List all collections in the database"""
        try:
            if self.db is None:
                return []
            return self.db.list_collection_names()
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def create_collections(self):
        """
        Create all necessary collections with validation schemas
        """
        try:
            # Employees collection schema
            employees_schema = {
                "bsonType": "object",
                "required": ["employee_id", "name"],
                "properties": {
                    "employee_id": {"bsonType": "string"},
                    "name": {"bsonType": "string"},
                    "aadhar_no": {"bsonType": "string"},
                    "phone": {"bsonType": "string"},
                    "department": {"bsonType": "string"},
                    "position": {"bsonType": "string"},
                    "daily_wage": {"bsonType": "number"},
                    "hire_date": {"bsonType": "date"},
                    "last_paid": {"bsonType": ["date", "null"]},
                    "status": {"enum": ["active", "inactive", "terminated"]},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
            
            # Attendance collection schema
            attendance_schema = {
                "bsonType": "object",
                "required": ["employee_id", "date", "status"],
                "properties": {
                    "employee_id": {"bsonType": "string"},
                    "employee_name": {"bsonType": "string"},
                    "date": {"bsonType": "date"},
                    "status": {"enum": ["Present", "Absent", "Leave", "Half Day", "Overtime", "Late", "Remote Work"]},
                    "in_time": {"bsonType": "string"},
                    "out_time": {"bsonType": "string"},
                    "hours": {"bsonType": "string"},
                    "overtime_hours": {"bsonType": "number"},
                    "notes": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
            
            # Stock collection schema
            stock_schema = {
                "bsonType": "object",
                "required": ["item_name", "category"],
                "properties": {
                    "item_name": {"bsonType": "string"},
                    "category": {"bsonType": "string"},
                    "current_quantity": {"bsonType": "number"},
                    "unit_cost_average": {"bsonType": "number"},
                    "minimum_stock": {"bsonType": "number"},
                    "supplier": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"}
                }
            }
            
            # Purchases collection schema
            purchases_schema = {
                "bsonType": "object",
                "required": ["date", "item_name", "quantity", "unit_price"],
                "properties": {
                    "date": {"bsonType": "date"},
                    "item_name": {"bsonType": "string"},
                    "category": {"bsonType": "string"},
                    "quantity": {"bsonType": "number"},
                    "unit_price": {"bsonType": "number"},
                    "total_price": {"bsonType": "number"},
                    "supplier": {"bsonType": "string"},
                    "invoice_number": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
            
            # Sales collection schema (legacy - kept for compatibility)
            sales_schema = {
                "bsonType": "object",
                "required": ["date", "item_name", "quantity", "unit_price"],
                "properties": {
                    "date": {"bsonType": "date"},
                    "item_name": {"bsonType": "string"},
                    "category": {"bsonType": "string"},
                    "quantity": {"bsonType": "number"},
                    "unit_price": {"bsonType": "number"},
                    "total_price": {"bsonType": "number"},
                    "customer_name": {"bsonType": "string"},
                    "customer_phone": {"bsonType": "string"},
                    "customer_email": {"bsonType": "string"},
                    "created_at": {"bsonType": "date"}
                }
            }
            
            # Orders collection schema (new system)
            orders_schema = {
                "bsonType": "object",
                "required": ["order_id", "customer_name", "item_name", "quantity", "unit_price"],
                "properties": {
                    "order_id": {"bsonType": "string"},
                    "customer_name": {"bsonType": "string"},
                    "customer_phone": {"bsonType": "string"},
                    "customer_address": {"bsonType": "string"},
                    "item_name": {"bsonType": "string"},
                    "quantity": {"bsonType": "number"},
                    "unit_price": {"bsonType": "number"},
                    "total_amount": {"bsonType": "number"},
                    "advance_payment": {"bsonType": "number"},
                    "due_amount": {"bsonType": "number"},
                    "order_status": {"enum": ["Pending", "Processing", "Ready", "Delivered", "Cancelled", "Paid"]},
                    "payment_method": {"enum": ["Cash", "Card", "UPI", "Bank Transfer", "Cheque"]},
                    "order_date": {"bsonType": "string"},
                    "due_date": {"bsonType": "string"},
                    "created_date": {"bsonType": "string"},
                    "updated_date": {"bsonType": "string"}
                }
            }
            
            # Transactions collection schema (new system)
            transactions_schema = {
                "bsonType": "object",
                "required": ["transaction_id", "order_id", "payment_date"],
                "properties": {
                    "transaction_id": {"bsonType": "string"},
                    "order_id": {"bsonType": "string"},
                    "payment_amount": {"bsonType": "number"},  # Legacy field for backward compatibility
                    "amount": {"bsonType": "number"},  # New standardized field
                    "payment_date": {"bsonType": "string"},
                    "payment_method": {"enum": ["Cash", "Card", "UPI", "Bank Transfer", "Cheque"]},
                    "transaction_type": {"enum": ["advance_payment", "payment", "refund"]},
                    "notes": {"bsonType": "string"},
                    "created_date": {"bsonType": "string"}
                }
            }
            
            # Create collections with schemas
            collections_config = {
                "employees": employees_schema,
                "attendance": attendance_schema,
                "stock": stock_schema,
                "purchases": purchases_schema,
                "sales": sales_schema,
                "orders": orders_schema,
                "transactions": transactions_schema
            }
            
            for collection_name, schema in collections_config.items():
                if collection_name not in self.db.list_collection_names():
                    self.db.create_collection(
                        collection_name,
                        validator={"$jsonSchema": schema}
                    )
                    logger.info(f"Created collection: {collection_name}")
                else:
                    logger.info(f"Collection already exists: {collection_name}")
            
            # Create indexes for better performance
            self._create_indexes()
            return True
            
        except Exception as e:
            logger.error(f"Error creating collections: {e}")
            return False
    
    def update_collection_validation(self):
        """Update validation schema for existing collections and migrate data"""
        try:
            logger.info("Starting optimized database migration...")
            
            # Run migrations with timeout and error handling
            migrations = [
                ("employees", self._migrate_employees_schema_fast),
                ("attendance", self._migrate_attendance_schema_fast),
                ("transactions", self._migrate_transactions_schema_fast)
            ]
            
            for collection_name, migration_func in migrations:
                try:
                    logger.info(f"Migrating {collection_name}...")
                    migration_func()
                    logger.info(f"✓ {collection_name} migration completed")
                except Exception as e:
                    logger.warning(f"⚠ {collection_name} migration failed: {e}")
                    # Continue with other migrations even if one fails
                    continue
            
            logger.info("Database migration completed")
            return True
            
        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            return False
    
    def _migrate_employees_schema_fast(self):
        """Fast employees schema migration - skip if already correct"""
        try:
            # Quick check: try a simple operation to see if schema is already correct
            test_doc = {"employee_id": "TEST_MIGRATION", "name": "Test"}
            try:
                result = self.db.employees.insert_one(test_doc)
                self.db.employees.delete_one({"_id": result.inserted_id})
                logger.info("Employees schema already correct, skipping migration")
                return
            except Exception:
                pass  # Schema needs migration
            
            # Only migrate if necessary - check if email is required
            try:
                # Try to update schema without dropping collection first
                employees_schema = {
                    "bsonType": "object",
                    "required": ["employee_id", "name"],
                    "properties": {
                        "employee_id": {"bsonType": "string"},
                        "name": {"bsonType": "string"},
                        "aadhar_no": {"bsonType": "string"},
                        "phone": {"bsonType": "string"},
                        "department": {"bsonType": "string"},
                        "position": {"bsonType": "string"},
                        "daily_wage": {"bsonType": "number"},
                        "hire_date": {"bsonType": "date"},
                        "last_paid": {"bsonType": ["date", "null"]},
                        "status": {"enum": ["active", "inactive", "terminated"]},
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"}
                    }
                }
                
                self.db.command({
                    "collMod": "employees",
                    "validator": {"$jsonSchema": employees_schema}
                })
                logger.info("Updated employees schema successfully")
            except Exception as e:
                logger.info(f"Schema update failed, employees collection may need recreation: {e}")
                # Don't recreate collection automatically - leave existing data intact
                
        except Exception as e:
            logger.warning(f"Employees migration error: {e}")
    
    def _migrate_attendance_schema_fast(self):
        """Fast attendance schema migration - remove exception_hours and ensure overtime_hour field"""
        try:
            # Step 1: Remove exception_hours field from all records (since we hardcode it to 1)
            logger.info("Removing exception_hours field from attendance records...")
            
            count_with_exception_hours = self.db.attendance.count_documents({
                "exception_hours": {"$exists": True}
            })
            
            if count_with_exception_hours > 0:
                logger.info(f"Found {count_with_exception_hours} records with exception_hours field to remove")
                
                # Remove the exception_hours field from all documents
                result = self.db.attendance.update_many(
                    {"exception_hours": {"$exists": True}},
                    {"$unset": {"exception_hours": ""}}
                )
                
                logger.info(f"Successfully removed exception_hours field from {result.modified_count} records")
            else:
                logger.info("No records found with exception_hours field")
            
            # Step 2: Ensure overtime_hour field exists and has default value
            logger.info("Ensuring overtime_hour field exists in attendance records...")
            
            count_without_overtime = self.db.attendance.count_documents({
                "overtime_hour": {"$exists": False}
            })
            
            if count_without_overtime > 0:
                logger.info(f"Found {count_without_overtime} records missing overtime_hour field")
                
                # Add overtime_hour field with default value 0 to records that don't have it
                result = self.db.attendance.update_many(
                    {"overtime_hour": {"$exists": False}},
                    {"$set": {"overtime_hour": 0}}
                )
                
                logger.info(f"Successfully added overtime_hour field to {result.modified_count} records")
            else:
                logger.info("All attendance records already have overtime_hour field")
            
            # Step 3: Ensure basic time fields exist for compatibility (but not exception_hours)
            sample_records = list(self.db.attendance.find({}).limit(5))
            if not sample_records:
                logger.info("No attendance records to migrate")
                return
                
            needs_basic_migration = False
            for record in sample_records:
                # Check for basic time fields (but NOT exception_hours)
                if any(field not in record for field in ['time_in', 'time_out']):
                    needs_basic_migration = True
                    break
            
            if needs_basic_migration:
                logger.info("Adding missing time fields to attendance records...")
                
                # Use bulk operations for efficiency
                bulk_operations = []
                
                # Find records missing basic time fields
                missing_fields_query = {
                    "$or": [
                        {"time_in": {"$exists": False}},
                        {"time_out": {"$exists": False}}
                    ]
                }
                
                # Process in batches to avoid memory issues
                batch_size = 100
                processed = 0
                
                cursor = self.db.attendance.find(missing_fields_query)
                
                for record in cursor:
                    update_data = {}
                    if 'time_in' not in record:
                        update_data['time_in'] = ""
                    if 'time_out' not in record:
                        update_data['time_out'] = ""
                    
                    if update_data:
                        bulk_operations.append({
                            "updateOne": {
                                "filter": {"_id": record["_id"]},
                                "update": {"$set": update_data}
                            }
                        })
                    
                    processed += 1
                    
                    # Execute bulk operations in batches
                    if len(bulk_operations) >= batch_size:
                        self.db.attendance.bulk_write(bulk_operations)
                        bulk_operations = []
                        logger.info(f"Processed {processed} attendance records...")
                
                # Execute remaining operations
                if bulk_operations:
                    self.db.attendance.bulk_write(bulk_operations)
                
                logger.info(f"Added missing time fields to {processed} attendance records")
            else:
                logger.info("All attendance records have required time fields")
                
        except Exception as e:
            logger.warning(f"Attendance migration error: {e}")
    
    def _migrate_transactions_schema_fast(self):
        """Fast transactions schema migration - migrate payment_amount to amount"""
        try:
            # Check if migration is needed
            needs_migration = self.db.transactions.count_documents({
                "payment_amount": {"$exists": True},
                "amount": {"$exists": False}
            })
            
            if needs_migration == 0:
                logger.info("All transactions already use standardized amount field")
                return
            
            logger.info(f"Found {needs_migration} transactions to migrate")
            
            # Use bulk operations for efficiency
            bulk_operations = []
            
            # Process transactions that need migration
            cursor = self.db.transactions.find({
                "payment_amount": {"$exists": True},
                "amount": {"$exists": False}
            })
            
            for transaction in cursor:
                bulk_operations.append({
                    "updateOne": {
                        "filter": {"_id": transaction["_id"]},
                        "update": {"$set": {"amount": transaction["payment_amount"]}}
                    }
                })
                
                # Process in batches
                if len(bulk_operations) >= 50:
                    self.db.transactions.bulk_write(bulk_operations)
                    bulk_operations = []
            
            # Execute remaining operations
            if bulk_operations:
                self.db.transactions.bulk_write(bulk_operations)
            
            logger.info(f"Successfully migrated {needs_migration} transactions to use amount field")
                
        except Exception as e:
            logger.warning(f"Transactions migration error: {e}")
    
    def remove_exception_hours_column(self):
        """Remove exception_hours column from attendance table"""
        try:
            logger.info("Starting removal of exception_hours column from attendance...")
            
            # Count how many records have the exception_hours field
            count_with_exception_hours = self.db.attendance.count_documents({
                "exception_hours": {"$exists": True}
            })
            
            if count_with_exception_hours == 0:
                logger.info("No records found with exception_hours field")
                return
            
            logger.info(f"Found {count_with_exception_hours} records with exception_hours field")
            
            # Remove the exception_hours field from all documents
            result = self.db.attendance.update_many(
                {"exception_hours": {"$exists": True}},
                {"$unset": {"exception_hours": ""}}
            )
            
            logger.info(f"Successfully removed exception_hours field from {result.modified_count} records")
            
        except Exception as e:
            logger.error(f"Error removing exception_hours column: {e}")
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Employees indexes
            self.db.employees.create_index("employee_id", unique=True)
            self.db.employees.create_index("aadhar_no")
            
            # Attendance indexes
            self.db.attendance.create_index([("employee_id", 1), ("date", 1)], unique=True)
            self.db.attendance.create_index("date")
            
            # Stock indexes
            self.db.stock.create_index("item_name", unique=True)
            self.db.stock.create_index("category")
            
            # Purchases indexes
            self.db.purchases.create_index("date")
            self.db.purchases.create_index("item_name")
            
            # Sales indexes (legacy)
            self.db.sales.create_index("date")
            self.db.sales.create_index("item_name")
            self.db.sales.create_index("customer_phone")
            
            # Orders indexes (new system)
            self.db.orders.create_index("order_id", unique=True)
            self.db.orders.create_index("customer_phone")
            self.db.orders.create_index("order_date")
            self.db.orders.create_index("order_status")
            self.db.orders.create_index("due_date")
            
            # Transactions indexes (new system)
            self.db.transactions.create_index("transaction_id", unique=True)
            self.db.transactions.create_index("order_id")
            self.db.transactions.create_index("payment_date")
            self.db.transactions.create_index("payment_method")
            
            logger.info("Indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # CRUD Operations
    
    @log_function_call
    def insert_document(self, collection_name: str, document: Dict) -> str:
        """
        Insert a document into specified collection
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            str: Inserted document ID
        """
        start_time = time.time()
        try:
            if self.db is None:
                log_error(Exception("Database connection not established"), "DB_INSERT")
                return None
                
            # Add timestamps
            document['created_at'] = datetime.now()
            if 'updated_at' not in document:
                document['updated_at'] = datetime.now()
            
            log_info(f"Inserting document into {collection_name}", "DB_INSERT")
            result = self.db[collection_name].insert_one(document)
            
            duration = (time.time() - start_time) * 1000
            log_info(f"Document inserted into {collection_name}: {result.inserted_id} in {duration:.2f}ms", "DB_INSERT")
            dashboard_logger.log_database_operation("insert", collection_name, document, 
                                                   {"inserted_id": str(result.inserted_id)}, duration)
            
            return str(result.inserted_id)
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_error(e, f"DB_INSERT_{collection_name}")
            dashboard_logger.log_database_operation("insert", collection_name, document, 
                                                   {"success": False, "error": str(e)}, duration)
            raise
    
    @log_function_call
    def find_documents(self, collection_name: str, filter_dict: Dict = None, limit: int = None) -> List[Dict]:
        """
        Find documents in specified collection
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria
            limit: Maximum number of documents to return
            
        Returns:
            List[Dict]: List of documents
        """
        start_time = time.time()
        try:
            if self.db is None:
                log_error(Exception("Database connection not established"), "DB_FIND")
                return []
                
            filter_dict = filter_dict or {}
            log_info(f"Querying {collection_name} with filter: {filter_dict}", "DB_FIND")
            
            cursor = self.db[collection_name].find(filter_dict)
            if limit:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                doc['_id'] = str(doc['_id'])
            
            duration = (time.time() - start_time) * 1000
            log_info(f"Found {len(documents)} documents in {collection_name} in {duration:.2f}ms", "DB_FIND")
            dashboard_logger.log_database_operation("find", collection_name, filter_dict, 
                                                   {"count": len(documents)}, duration)
            
            return documents
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_error(e, f"DB_FIND_{collection_name}")
            dashboard_logger.log_database_operation("find", collection_name, filter_dict, 
                                                   {"success": False, "error": str(e)}, duration)
            return []
    
    def update_document(self, collection_name: str, filter_dict: Dict, update_dict: Dict) -> int:
        """
        Update documents in specified collection
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria
            update_dict: Update operations
            
        Returns:
            int: Number of modified documents
        """
        try:
            if self.db is None:
                logger.error("Database connection not established")
                return 0
            
            # Convert string _id to ObjectId if present
            if '_id' in filter_dict and isinstance(filter_dict['_id'], str):
                try:
                    filter_dict['_id'] = ObjectId(filter_dict['_id'])
                except Exception as e:
                    logger.error(f"Invalid ObjectId string: {filter_dict['_id']}")
                    return 0
            
            # Handle both direct field updates and MongoDB operations
            if '$set' in update_dict:
                # If $set operation is provided, add updated_at to it
                update_dict['$set']['updated_at'] = datetime.now()
                final_update = update_dict
            else:
                # If direct field update, wrap in $set with updated_at
                update_dict['updated_at'] = datetime.now()
                final_update = {"$set": update_dict}
                
            result = self.db[collection_name].update_many(
                filter_dict, 
                final_update
            )
            logger.info(f"Updated {result.modified_count} documents in {collection_name}")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating documents in {collection_name}: {e}")
            return 0
    
    def delete_documents(self, collection_name: str, filter_dict: Dict) -> int:
        """
        Delete documents from specified collection
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria
            
        Returns:
            int: Number of deleted documents
        """
        try:
            if self.db is None:
                logger.error("Database connection not established")
                return 0
                
            result = self.db[collection_name].delete_many(filter_dict)
            logger.info(f"Deleted {result.deleted_count} documents from {collection_name}")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents from {collection_name}: {e}")
            return 0
    
    def delete_document(self, collection_name: str, filter_dict: Dict) -> bool:
        """
        Delete a single document from specified collection
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria
            
        Returns:
            bool: True if document was deleted, False otherwise
        """
        try:
            if self.db is None:
                logger.error("Database connection not established")
                return False
                
            result = self.db[collection_name].delete_one(filter_dict)
            if result.deleted_count > 0:
                logger.info(f"Deleted 1 document from {collection_name}")
                return True
            else:
                logger.warning(f"No document found to delete from {collection_name}")
                return False
        except Exception as e:
            logger.error(f"Error deleting document from {collection_name}: {e}")
            return False
    
    def delete_many_documents(self, collection_name: str, filter_dict: Dict) -> int:
        """
        Alias for delete_documents method for consistency
        """
        return self.delete_documents(collection_name, filter_dict)
    
    def get_collection_as_dataframe(self, collection_name: str, filter_dict: Dict = None) -> pd.DataFrame:
        """
        Get collection data as pandas DataFrame
        
        Args:
            collection_name: Name of the collection
            filter_dict: Filter criteria
            
        Returns:
            pd.DataFrame: Collection data as DataFrame
        """
        try:
            documents = self.find_documents(collection_name, filter_dict)
            if not documents:
                return pd.DataFrame()
            
            df = pd.DataFrame(documents)
            # Remove MongoDB _id column for display
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            
            return df
        except Exception as e:
            logger.error(f"Error converting {collection_name} to DataFrame: {e}")
            return pd.DataFrame()
    
    def string_to_objectid(self, id_string: str) -> ObjectId:
        """Convert string ID to MongoDB ObjectId"""
        try:
            return ObjectId(id_string)
        except Exception as e:
            logger.error(f"Error converting string to ObjectId: {e}")
            raise ValueError(f"Invalid ObjectId string: {id_string}")
    
    def objectid_to_string(self, object_id: ObjectId) -> str:
        """Convert MongoDB ObjectId to string"""
        return str(object_id)


# Singleton instance
db_manager = None

def get_db_manager() -> MongoDBManager:
    """Get singleton instance of MongoDB manager"""
    global db_manager
    if db_manager is None:
        db_manager = MongoDBManager()
    return db_manager

def initialize_database():
    """Initialize database with collections and sample data"""
    db_mgr = get_db_manager()
    if db_mgr.connect():
        return db_mgr.create_collections()
    return False
