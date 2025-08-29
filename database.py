import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Import configuration
try:
    from config import MONGODB_URI, MONGODB_DATABASE
except ImportError:
    # Fallback configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'hr_management_db')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        self.connection_string = connection_string or MONGODB_URI
        self.database_name = database_name or MONGODB_DATABASE
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self) -> bool:
        """
        Establish connection to MongoDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            logger.info(f"Successfully connected to MongoDB: {self.database_name}")
            return True
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def create_collections(self):
        """
        Create all necessary collections with validation schemas
        """
        try:
            # Employees collection schema
            employees_schema = {
                "bsonType": "object",
                "required": ["employee_id", "name", "email"],
                "properties": {
                    "employee_id": {"bsonType": "string"},
                    "name": {"bsonType": "string"},
                    "email": {"bsonType": "string"},
                    "phone": {"bsonType": "string"},
                    "department": {"bsonType": "string"},
                    "position": {"bsonType": "string"},
                    "joining_date": {"bsonType": "date"},
                    "salary": {"bsonType": "number"},
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
                    "status": {"enum": ["Present", "Absent", "Leave", "Half Day", "Overtime"]},
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
            
            # Sales collection schema
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
            
            # Create collections with schemas
            collections_config = {
                "employees": employees_schema,
                "attendance": attendance_schema,
                "stock": stock_schema,
                "purchases": purchases_schema,
                "sales": sales_schema
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
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Employees indexes
            self.db.employees.create_index("employee_id", unique=True)
            self.db.employees.create_index("email", unique=True)
            
            # Attendance indexes
            self.db.attendance.create_index([("employee_id", 1), ("date", 1)], unique=True)
            self.db.attendance.create_index("date")
            
            # Stock indexes
            self.db.stock.create_index("item_name", unique=True)
            self.db.stock.create_index("category")
            
            # Purchases indexes
            self.db.purchases.create_index("date")
            self.db.purchases.create_index("item_name")
            
            # Sales indexes
            self.db.sales.create_index("date")
            self.db.sales.create_index("item_name")
            self.db.sales.create_index("customer_phone")
            
            logger.info("Indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # CRUD Operations
    
    def insert_document(self, collection_name: str, document: Dict) -> str:
        """
        Insert a document into specified collection
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            
        Returns:
            str: Inserted document ID
        """
        try:
            document['created_at'] = datetime.now()
            if 'updated_at' not in document:
                document['updated_at'] = datetime.now()
            
            result = self.db[collection_name].insert_one(document)
            logger.info(f"Document inserted into {collection_name}: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document into {collection_name}: {e}")
            raise
    
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
        try:
            filter_dict = filter_dict or {}
            cursor = self.db[collection_name].find(filter_dict)
            if limit:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                doc['_id'] = str(doc['_id'])
            
            return documents
        except Exception as e:
            logger.error(f"Error finding documents in {collection_name}: {e}")
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
            update_dict['updated_at'] = datetime.now()
            result = self.db[collection_name].update_many(
                filter_dict, 
                {"$set": update_dict}
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
            result = self.db[collection_name].delete_many(filter_dict)
            logger.info(f"Deleted {result.deleted_count} documents from {collection_name}")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents from {collection_name}: {e}")
            return 0
    
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
