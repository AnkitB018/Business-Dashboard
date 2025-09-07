import pandas as pd
from database import get_db_manager
from datetime import datetime, date
from typing import Dict, List, Optional
from logger_config import get_logger, log_function_call, log_info, log_error

# Initialize enhanced logging
dashboard_logger = get_logger()
logger = dashboard_logger.main_logger

class DataMigration:
    """
    Handles migration from Excel to MongoDB
    """
    
    def __init__(self, excel_file: str = "business_data.xlsx"):
        self.excel_file = excel_file
        self.db_manager = get_db_manager()
    
    def migrate_from_excel(self) -> bool:
        """
        Migrate all data from Excel file to MongoDB
        
        Returns:
            bool: True if migration successful
        """
        try:
            # Read all sheets from Excel
            excel_data = pd.read_excel(self.excel_file, sheet_name=None)
            
            migration_mapping = {
                "Employees": self._migrate_employees,
                "Attendance": self._migrate_attendance,
                "Purchases": self._migrate_purchases,
                "Sales": self._migrate_sales
            }
            
            for sheet_name, migrate_func in migration_mapping.items():
                if sheet_name in excel_data:
                    df = excel_data[sheet_name]
                    if not df.empty:
                        success = migrate_func(df)
                        if success:
                            logger.info(f"Successfully migrated {sheet_name}")
                        else:
                            logger.error(f"Failed to migrate {sheet_name}")
                            return False
                else:
                    logger.warning(f"Sheet {sheet_name} not found in Excel file")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def _migrate_employees(self, df: pd.DataFrame) -> bool:
        """Migrate employees data"""
        try:
            for _, row in df.iterrows():
                employee_doc = {
                    "employee_id": str(row.get("Employee id", "")),
                    "name": str(row.get("Name", "")),
                    "email": str(row.get("Email", "")),
                    "phone": str(row.get("Phone", "")),
                    "department": str(row.get("Department", "")),
                    "position": str(row.get("Position", "")),
                    "salary": float(row.get("Salary", 0)) if pd.notna(row.get("Salary")) else 0,
                    "status": "active"
                }
                
                # Handle joining date
                joining_date = row.get("Joining Date")
                if pd.notna(joining_date):
                    if isinstance(joining_date, str):
                        employee_doc["joining_date"] = datetime.strptime(joining_date, "%Y-%m-%d")
                    else:
                        employee_doc["joining_date"] = joining_date
                
                # Check if employee already exists
                existing = self.db_manager.find_documents(
                    "employees", 
                    {"employee_id": employee_doc["employee_id"]}
                )
                
                if not existing:
                    self.db_manager.insert_document("employees", employee_doc)
            
            return True
        except Exception as e:
            logger.error(f"Error migrating employees: {e}")
            return False
    
    def _migrate_attendance(self, df: pd.DataFrame) -> bool:
        """Migrate attendance data"""
        try:
            for _, row in df.iterrows():
                attendance_doc = {
                    "employee_id": str(row.get("Employee id", "")),
                    "employee_name": str(row.get("Name", "")),
                    "status": str(row.get("Status", "")),
                    "overtime_hours": float(row.get("Overtime Hours", 0)) if pd.notna(row.get("Overtime Hours")) else 0
                }
                
                # Handle date
                attendance_date = row.get("Date")
                if pd.notna(attendance_date):
                    if isinstance(attendance_date, str):
                        attendance_doc["date"] = datetime.strptime(attendance_date, "%Y-%m-%d")
                    else:
                        attendance_doc["date"] = attendance_date
                
                # Check if record already exists
                existing = self.db_manager.find_documents(
                    "attendance", 
                    {
                        "employee_id": attendance_doc["employee_id"],
                        "date": attendance_doc["date"]
                    }
                )
                
                if not existing:
                    self.db_manager.insert_document("attendance", attendance_doc)
            
            return True
        except Exception as e:
            logger.error(f"Error migrating attendance: {e}")
            return False
    
    def _migrate_purchases(self, df: pd.DataFrame) -> bool:
        """Migrate purchases data"""
        try:
            for _, row in df.iterrows():
                purchase_doc = {
                    "item_name": str(row.get("Item Name", "")),
                    "category": str(row.get("Category", "")),
                    "quantity": float(row.get("Quantity", 0)) if pd.notna(row.get("Quantity")) else 0,
                    "unit_price": float(row.get("Unit Price", 0)) if pd.notna(row.get("Unit Price")) else 0,
                    "total_price": float(row.get("Total Price", 0)) if pd.notna(row.get("Total Price")) else 0
                }
                
                # Handle date
                purchase_date = row.get("Date")
                if pd.notna(purchase_date):
                    if isinstance(purchase_date, str):
                        purchase_doc["date"] = datetime.strptime(purchase_date, "%Y-%m-%d")
                    else:
                        purchase_doc["date"] = purchase_date
                
                # Calculate total price if not provided
                if purchase_doc["total_price"] == 0:
                    purchase_doc["total_price"] = purchase_doc["quantity"] * purchase_doc["unit_price"]
                
                self.db_manager.insert_document("purchases", purchase_doc)
            
            return True
        except Exception as e:
            logger.error(f"Error migrating purchases: {e}")
            return False
    
    def _migrate_sales(self, df: pd.DataFrame) -> bool:
        """Migrate sales data"""
        try:
            for _, row in df.iterrows():
                sales_doc = {
                    "item_name": str(row.get("Item Name", "")),
                    "category": str(row.get("Category", "")),
                    "quantity": float(row.get("Quantity", 0)) if pd.notna(row.get("Quantity")) else 0,
                    "unit_price": float(row.get("Unit Price", 0)) if pd.notna(row.get("Unit Price")) else 0,
                    "customer_name": str(row.get("Customer Name", "")),
                    "customer_phone": str(row.get("Customer Phone", ""))
                }
                
                # Handle date
                sales_date = row.get("Date")
                if pd.notna(sales_date):
                    if isinstance(sales_date, str):
                        sales_doc["date"] = datetime.strptime(sales_date, "%Y-%m-%d")
                    else:
                        sales_doc["date"] = sales_date
                
                # Calculate total price
                sales_doc["total_price"] = sales_doc["quantity"] * sales_doc["unit_price"]
                
                self.db_manager.insert_document("sales", sales_doc)
            
            return True
        except Exception as e:
            logger.error(f"Error migrating sales: {e}")
            return False


class HRDataService: 
    """
    Service layer for HR data operations
    """
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager if db_manager else get_db_manager()
    
    # Employee operations
    def get_employees(self, filter_dict: Dict = None) -> pd.DataFrame:
        """Get employees as DataFrame"""
        return self.db_manager.get_collection_as_dataframe("employees", filter_dict)
    
    @log_function_call
    def add_employee(self, employee_data: Dict) -> str:
        """Add new employee"""
        try:
            log_info(f"Adding new employee: {employee_data.get('employee_id', 'unknown')}", "DATA_SERVICE")
            dashboard_logger.log_user_activity("EMPLOYEE_ADD_START", {"employee_id": employee_data.get('employee_id')})
            
            # Ensure employee_id is unique
            existing = self.db_manager.find_documents("employees", {"employee_id": employee_data["employee_id"]})
            if existing:
                error_msg = f"Employee ID {employee_data['employee_id']} already exists"
                log_error(ValueError(error_msg), "DATA_SERVICE")
                dashboard_logger.log_user_activity("EMPLOYEE_ADD_FAILED", {"employee_id": employee_data.get('employee_id'), "reason": "duplicate"})
                raise ValueError(error_msg)
            
            result = self.db_manager.insert_document("employees", employee_data)
            log_info(f"Employee added successfully: {employee_data.get('employee_id')}", "DATA_SERVICE")
            dashboard_logger.log_user_activity("EMPLOYEE_ADD_SUCCESS", {"employee_id": employee_data.get('employee_id'), "result_id": result})
            dashboard_logger.log_data_operation("add_employee", "employees", 1, True)
            
            return result
            
        except Exception as e:
            log_error(e, "DATA_SERVICE_ADD_EMPLOYEE")
            dashboard_logger.log_user_activity("EMPLOYEE_ADD_ERROR", {"employee_id": employee_data.get('employee_id'), "error": str(e)})
            dashboard_logger.log_data_operation("add_employee", "employees", 0, False, e)
            raise
    
    def delete_employee(self, employee_id: str) -> int:
        """Delete employee record by employee ID"""
        try:
            log_info(f"Deleting employee: {employee_id}", "DATA_SERVICE")
            dashboard_logger.log_user_activity("EMPLOYEE_DELETE_START", {"employee_id": employee_id})
            
            # Check if employee exists
            existing = self.db_manager.find_documents("employees", {"employee_id": employee_id})
            if not existing:
                error_msg = f"Employee ID {employee_id} not found"
                log_error(ValueError(error_msg), "DATA_SERVICE")
                dashboard_logger.log_user_activity("EMPLOYEE_DELETE_FAILED", {"employee_id": employee_id, "reason": "not_found"})
                return 0
            
            # Delete the employee
            result = self.db_manager.delete_documents("employees", {"employee_id": employee_id})
            
            if result > 0:
                log_info(f"Employee deleted successfully: {employee_id}", "DATA_SERVICE")
                dashboard_logger.log_user_activity("EMPLOYEE_DELETE_SUCCESS", {"employee_id": employee_id, "deleted_count": result})
                dashboard_logger.log_data_operation("delete_employee", "employees", result, True)
            else:
                log_error(Exception("Delete operation failed"), "DATA_SERVICE")
                dashboard_logger.log_user_activity("EMPLOYEE_DELETE_FAILED", {"employee_id": employee_id, "reason": "delete_failed"})
                dashboard_logger.log_data_operation("delete_employee", "employees", 0, False)
            
            return result
            
        except Exception as e:
            log_error(e, "DATA_SERVICE_DELETE_EMPLOYEE")
            dashboard_logger.log_user_activity("EMPLOYEE_DELETE_ERROR", {"employee_id": employee_id, "error": str(e)})
            dashboard_logger.log_data_operation("delete_employee", "employees", 0, False, e)
            raise

    @log_function_call
    def update_employee(self, employee_id: str, employee_data: Dict) -> int:
        """Update employee record by employee ID"""
        try:
            # Ensure employee_id is a string
            employee_id = str(employee_id)
            log_info(f"Updating employee: {employee_id}", "DATA_SERVICE")
            dashboard_logger.log_user_activity("EMPLOYEE_UPDATE_START", {"employee_id": employee_id})
            
            # Check if employee exists
            existing = self.db_manager.find_documents("employees", {"employee_id": employee_id})
            
            if not existing:
                error_msg = f"Employee ID {employee_id} not found"
                log_error(ValueError(error_msg), "DATA_SERVICE")
                dashboard_logger.log_user_activity("EMPLOYEE_UPDATE_FAILED", {"employee_id": employee_id, "reason": "not_found"})
                return 0
            
            # Update the employee
            result = self.db_manager.update_document("employees", {"employee_id": employee_id}, employee_data)
            
            if result > 0:
                log_info(f"Employee updated successfully: {employee_id}", "DATA_SERVICE")
                dashboard_logger.log_user_activity("EMPLOYEE_UPDATE_SUCCESS", {"employee_id": employee_id, "updated_count": result})
                dashboard_logger.log_data_operation("update_employee", "employees", result, True)
            else:
                log_error(Exception("Update operation failed"), "DATA_SERVICE")
                dashboard_logger.log_user_activity("EMPLOYEE_UPDATE_FAILED", {"employee_id": employee_id, "reason": "update_failed"})
                dashboard_logger.log_data_operation("update_employee", "employees", 0, False)
            
            return result
            
        except Exception as e:
            log_error(e, "DATA_SERVICE_UPDATE_EMPLOYEE")
            dashboard_logger.log_user_activity("EMPLOYEE_UPDATE_ERROR", {"employee_id": employee_id, "error": str(e)})
            dashboard_logger.log_data_operation("update_employee", "employees", 0, False, e)
            raise

    @log_function_call
    def add_attendance(self, attendance_data: Dict) -> str:
        """Add attendance record"""
        try:
            emp_id = attendance_data.get("employee_id", "unknown")
            date_val = attendance_data.get("date", "unknown")
            log_info(f"Adding attendance for employee {emp_id} on {date_val}", "DATA_SERVICE")
            dashboard_logger.log_user_activity("ATTENDANCE_ADD_START", {"employee_id": emp_id, "date": str(date_val)})
            
            # Check for duplicate entries
            existing = self.db_manager.find_documents(
                "attendance", 
                {
                    "employee_id": attendance_data["employee_id"],
                    "date": attendance_data["date"]
                }
            )
            if existing:
                error_msg = "Attendance record already exists for this employee and date"
                log_error(ValueError(error_msg), "DATA_SERVICE")
                dashboard_logger.log_user_activity("ATTENDANCE_ADD_FAILED", {"employee_id": emp_id, "date": str(date_val), "reason": "duplicate"})
                raise ValueError(error_msg)
            
            result = self.db_manager.insert_document("attendance", attendance_data)
            log_info(f"Attendance added successfully for employee {emp_id}", "DATA_SERVICE")
            dashboard_logger.log_user_activity("ATTENDANCE_ADD_SUCCESS", {"employee_id": emp_id, "date": str(date_val), "result_id": result})
            dashboard_logger.log_data_operation("add_attendance", "attendance", 1, True)
            
            return result
            
        except Exception as e:
            log_error(e, "DATA_SERVICE_ADD_ATTENDANCE")
            dashboard_logger.log_user_activity("ATTENDANCE_ADD_ERROR", {"employee_id": emp_id, "date": str(date_val), "error": str(e)})
            dashboard_logger.log_data_operation("add_attendance", "attendance", 0, False, e)
            raise
    
    def get_attendance(self, filter_dict: Dict = None) -> pd.DataFrame:
        """Get attendance records as DataFrame"""
        return self.db_manager.get_collection_as_dataframe("attendance", filter_dict)
    
    def delete_attendance(self, filter_dict: Dict) -> int:
        """Delete attendance records"""
        return self.db_manager.delete_documents("attendance", filter_dict)
    
    @log_function_call
    def update_attendance(self, attendance_id: str, attendance_data: Dict) -> int:
        """Update attendance record by attendance ID"""
        try:
            log_info(f"Updating attendance: {attendance_id}", "DATA_SERVICE")
            dashboard_logger.log_user_activity("ATTENDANCE_UPDATE_START", {"attendance_id": attendance_id})
            
            # Check if attendance record exists
            existing = self.db_manager.find_documents("attendance", {"_id": self.db_manager.string_to_objectid(attendance_id)})
            
            if not existing:
                error_msg = f"Attendance record {attendance_id} not found"
                log_error(ValueError(error_msg), "DATA_SERVICE")
                dashboard_logger.log_user_activity("ATTENDANCE_UPDATE_FAILED", {"attendance_id": attendance_id, "reason": "not_found"})
                return 0
            
            # Update the attendance record
            result = self.db_manager.update_document("attendance", {"_id": self.db_manager.string_to_objectid(attendance_id)}, attendance_data)
            
            if result > 0:
                log_info(f"Attendance updated successfully: {attendance_id}", "DATA_SERVICE")
                dashboard_logger.log_user_activity("ATTENDANCE_UPDATE_SUCCESS", {"attendance_id": attendance_id, "updated_count": result})
                dashboard_logger.log_data_operation("update_attendance", "attendance", result, True)
            else:
                log_error(Exception("Update operation failed"), "DATA_SERVICE")
                dashboard_logger.log_user_activity("ATTENDANCE_UPDATE_FAILED", {"attendance_id": attendance_id, "reason": "update_failed"})
                dashboard_logger.log_data_operation("update_attendance", "attendance", 0, False)
            
            return result
            
        except Exception as e:
            log_error(e, "DATA_SERVICE_UPDATE_ATTENDANCE")
            dashboard_logger.log_user_activity("ATTENDANCE_UPDATE_ERROR", {"attendance_id": attendance_id, "error": str(e)})
            dashboard_logger.log_data_operation("update_attendance", "attendance", 0, False, e)
            raise
    
    # Purchase operations
    def get_purchases(self, filter_dict: Dict = None) -> pd.DataFrame:
        """Get purchases as DataFrame"""
        return self.db_manager.get_collection_as_dataframe("purchases", filter_dict)
    
    def add_purchase(self, purchase_data: Dict) -> str:
        """Add purchase record"""
        # Add purchase record
        purchase_id = self.db_manager.insert_document("purchases", purchase_data)
        
        return purchase_id
    
    def delete_purchase(self, filter_dict: Dict) -> int:
        """Delete purchase records"""
        return self.db_manager.delete_documents("purchases", filter_dict)
    
    @log_function_call
    def update_purchase(self, purchase_id: str, purchase_data: Dict) -> int:
        """Update purchase record by purchase ID"""
        try:
            log_info(f"Updating purchase: {purchase_id}", "DATA_SERVICE")
            dashboard_logger.log_user_activity("PURCHASE_UPDATE_START", {"purchase_id": purchase_id})
            
            # Check if purchase record exists
            existing = self.db_manager.find_documents("purchases", {"_id": self.db_manager.string_to_objectid(purchase_id)})
            
            if not existing:
                error_msg = f"Purchase record {purchase_id} not found"
                log_error(ValueError(error_msg), "DATA_SERVICE")
                dashboard_logger.log_user_activity("PURCHASE_UPDATE_FAILED", {"purchase_id": purchase_id, "reason": "not_found"})
                return 0
            
            # Update the purchase record
            result = self.db_manager.update_document("purchases", {"_id": self.db_manager.string_to_objectid(purchase_id)}, purchase_data)
            
            if result > 0:
                log_info(f"Purchase updated successfully: {purchase_id}", "DATA_SERVICE")
                dashboard_logger.log_user_activity("PURCHASE_UPDATE_SUCCESS", {"purchase_id": purchase_id, "updated_count": result})
                dashboard_logger.log_data_operation("update_purchase", "purchases", result, True)
            else:
                log_error(Exception("Update operation failed"), "DATA_SERVICE")
                dashboard_logger.log_user_activity("PURCHASE_UPDATE_FAILED", {"purchase_id": purchase_id, "reason": "update_failed"})
                dashboard_logger.log_data_operation("update_purchase", "purchases", 0, False)
            
            return result
            
        except Exception as e:
            log_error(e, "DATA_SERVICE_UPDATE_PURCHASE")
            dashboard_logger.log_user_activity("PURCHASE_UPDATE_ERROR", {"purchase_id": purchase_id, "error": str(e)})
            dashboard_logger.log_data_operation("update_purchase", "purchases", 0, False, e)
            raise
    
    # Sales operations
    def get_sales(self, filter_dict: Dict = None) -> pd.DataFrame:
        """Get sales as DataFrame"""
        return self.db_manager.get_collection_as_dataframe("sales", filter_dict)
    
    def add_sale(self, sale_data: Dict) -> str:
        """Add sale record"""
        # Add sale record
        sale_id = self.db_manager.insert_document("sales", sale_data)
        
        return sale_id
    
    def delete_sale(self, filter_dict: Dict) -> int:
        """Delete sale records"""
        return self.db_manager.delete_documents("sales", filter_dict)
    
    @log_function_call
    def update_sale(self, sale_id: str, sale_data: Dict) -> int:
        """Update sale record by sale ID"""
        try:
            log_info(f"Updating sale: {sale_id}", "DATA_SERVICE")
            dashboard_logger.log_user_activity("SALE_UPDATE_START", {"sale_id": sale_id})
            
            # Check if sale record exists
            existing = self.db_manager.find_documents("sales", {"_id": self.db_manager.string_to_objectid(sale_id)})
            
            if not existing:
                error_msg = f"Sale record {sale_id} not found"
                log_error(ValueError(error_msg), "DATA_SERVICE")
                dashboard_logger.log_user_activity("SALE_UPDATE_FAILED", {"sale_id": sale_id, "reason": "not_found"})
                return 0
            
            # Update the sale record
            result = self.db_manager.update_document("sales", {"_id": self.db_manager.string_to_objectid(sale_id)}, sale_data)
            
            if result > 0:
                log_info(f"Sale updated successfully: {sale_id}", "DATA_SERVICE")
                dashboard_logger.log_user_activity("SALE_UPDATE_SUCCESS", {"sale_id": sale_id, "updated_count": result})
                dashboard_logger.log_data_operation("update_sale", "sales", result, True)
                
                # Update stock after sale modification if needed
                if any(key in sale_data for key in ['item_name', 'quantity']):
                    # You might want to implement stock adjustment logic here
                    pass
            else:
                log_error(Exception("Update operation failed"), "DATA_SERVICE")
                dashboard_logger.log_user_activity("SALE_UPDATE_FAILED", {"sale_id": sale_id, "reason": "update_failed"})
                dashboard_logger.log_data_operation("update_sale", "sales", 0, False)
            
            return result
            
        except Exception as e:
            log_error(e, "DATA_SERVICE_UPDATE_SALE")
            dashboard_logger.log_user_activity("SALE_UPDATE_ERROR", {"sale_id": sale_id, "error": str(e)})
            dashboard_logger.log_data_operation("update_sale", "sales", 0, False, e)
            raise
    

    
    # Database utilities
    def get_storage_usage(self) -> Dict:
        """Get MongoDB storage usage information"""
        try:
            database = self.db_manager.db
            
            # Get database stats
            stats = database.command('dbStats')
            
            # Calculate usage
            storage_size_mb = round(stats['storageSize'] / (1024*1024), 2)
            data_size_mb = round(stats['dataSize'] / (1024*1024), 2) 
            index_size_mb = round(stats['indexSize'] / (1024*1024), 2)
            total_size_mb = round((stats['storageSize'] + stats['indexSize']) / (1024*1024), 2)
            
            # Check if this is Atlas (free tier has 512MB limit)
            host_info = str(database.client.address)
            is_atlas = 'mongodb.net' in host_info or 'atlas' in host_info.lower()
            
            if is_atlas:
                limit_mb = 512.0
                usage_percentage = min(100, round((total_size_mb / limit_mb) * 100, 1))
                remaining_mb = max(0, limit_mb - total_size_mb)
            else:
                # Local MongoDB - assume large limit for display
                limit_mb = 10000.0  # 10GB assumption for local
                usage_percentage = min(100, round((total_size_mb / limit_mb) * 100, 1))
                remaining_mb = limit_mb - total_size_mb
            
            return {
                'storage_size_mb': storage_size_mb,
                'data_size_mb': data_size_mb,
                'index_size_mb': index_size_mb,
                'total_size_mb': total_size_mb,
                'limit_mb': limit_mb,
                'usage_percentage': usage_percentage,
                'remaining_mb': remaining_mb,
                'is_atlas': is_atlas,
                'database_name': database.name
            }
        except Exception as e:
            logger.error(f"Error getting storage usage: {e}")
            return {
                'storage_size_mb': 0,
                'data_size_mb': 0,
                'index_size_mb': 0,
                'total_size_mb': 0,
                'limit_mb': 512,
                'usage_percentage': 0,
                'remaining_mb': 512,
                'is_atlas': True,
                'database_name': 'Unknown',
                'error': str(e)
            }

# Singleton instance
hr_service = None

def get_hr_service() -> HRDataService:
    """Get singleton instance of HR service"""
    global hr_service
    if hr_service is None:
        hr_service = HRDataService()
    return hr_service

class DataService:
    """Enhanced DataService with Orders and Transactions support"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.hr_service = get_hr_service()
    
    # ====== ORDERS MANAGEMENT ======
    
    def add_order(self, order_data):
        """Add a new order to the database"""
        try:
            # Ensure order_date is set
            if 'order_date' not in order_data:
                order_data['order_date'] = date.today().strftime("%Y-%m-%d")
            
            # Add created timestamp
            order_data['created_date'] = datetime.now().isoformat()
            
            result = self.db_manager.insert_document("orders", order_data)
            return result
        except Exception as e:
            logger.error(f"Failed to add order: {str(e)}")
            return None
    
    def get_all_orders(self):
        """Get all orders from database"""
        try:
            orders = self.db_manager.find_documents("orders", {})
            # Sort by created date, newest first
            orders.sort(key=lambda x: x.get('created_date', ''), reverse=True)
            return orders
        except Exception as e:
            logger.error(f"Failed to get orders: {str(e)}")
            return []
    
    def get_order_by_id(self, order_id):
        """Get specific order by order ID"""
        try:
            order = self.db_manager.find_documents("orders", {"order_id": order_id})
            return order[0] if order else None
        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {str(e)}")
            return None
    
    def update_order(self, order_id, update_data):
        """Update order data"""
        try:
            # Add updated timestamp
            update_data['updated_date'] = datetime.now().isoformat()
            
            result = self.db_manager.update_document("orders", {"order_id": order_id}, update_data)
            return result
        except Exception as e:
            logger.error(f"Failed to update order {order_id}: {str(e)}")
            return None
    
    def delete_order(self, order_id):
        """Delete order by order ID"""
        try:
            result = self.db_manager.delete_document("orders", {"order_id": order_id})
            return result
        except Exception as e:
            logger.error(f"Failed to delete order {order_id}: {str(e)}")
            return None
    
    # ====== TRANSACTIONS MANAGEMENT ======
    
    def add_transaction(self, transaction_data):
        """Add a new transaction to the database"""
        try:
            # Ensure payment_date is set
            if 'payment_date' not in transaction_data:
                transaction_data['payment_date'] = date.today().strftime("%Y-%m-%d")
            
            # Add created timestamp
            transaction_data['created_date'] = datetime.now().isoformat()
            
            result = self.db_manager.insert_document("transactions", transaction_data)
            return result
        except Exception as e:
            logger.error(f"Failed to add transaction: {str(e)}")
            return None
    
    def get_transactions_by_order(self, order_id):
        """Get all transactions for a specific order"""
        try:
            transactions = self.db_manager.find_documents("transactions", {"order_id": order_id})
            # Sort by payment date
            transactions.sort(key=lambda x: x.get('payment_date', ''), reverse=True)
            return transactions
        except Exception as e:
            logger.error(f"Failed to get transactions for order {order_id}: {str(e)}")
            return []
    
    def get_all_transactions_with_orders(self):
        """Get all transactions with order information - OPTIMIZED"""
        try:
            # Get all transactions and orders in bulk
            transactions = self.db_manager.find_documents("transactions", {})
            all_orders = self.db_manager.find_documents("orders", {})
            
            # Create a lookup dictionary for orders by order_id for O(1) access
            orders_dict = {order.get('order_id'): order for order in all_orders}
            
            # Enrich transactions with order information
            enriched_transactions = []
            for transaction in transactions:
                order_id = transaction.get('order_id')
                if order_id and order_id in orders_dict:
                    order = orders_dict[order_id]
                    # Merge transaction and order data
                    enriched_transaction = transaction.copy()
                    enriched_transaction['customer_name'] = order.get('customer_name', 'N/A')
                    enriched_transaction['order_status'] = order.get('order_status', 'N/A')
                    enriched_transactions.append(enriched_transaction)
                else:
                    # Include transactions without orders but mark them
                    enriched_transaction = transaction.copy()
                    enriched_transaction['customer_name'] = 'Unknown'
                    enriched_transaction['order_status'] = 'N/A'
                    enriched_transactions.append(enriched_transaction)
            
            # Sort by creation timestamp (newest first), fallback to payment_date if created_date not available
            enriched_transactions.sort(key=lambda x: x.get('created_date', x.get('payment_date', '')), reverse=True)
            return enriched_transactions
        except Exception as e:
            logger.error(f"Failed to get transactions with orders: {str(e)}")
            return []
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction by ID"""
        try:
            result = self.db_manager.delete_document("transactions", {"transaction_id": transaction_id})
            if result and result.deleted_count > 0:
                logger.info(f"Transaction {transaction_id} deleted successfully")
                return {"success": True, "message": "Transaction deleted successfully"}
            else:
                logger.warning(f"Transaction {transaction_id} not found for deletion")
                return {"success": False, "message": "Transaction not found"}
        except Exception as e:
            logger.error(f"Failed to delete transaction {transaction_id}: {str(e)}")
            return {"success": False, "message": f"Error deleting transaction: {str(e)}"}
    
    def delete_transactions_by_order(self, order_id):
        """Delete all transactions for a specific order"""
        try:
            result = self.db_manager.delete_many_documents("transactions", {"order_id": order_id})
            return result
        except Exception as e:
            logger.error(f"Failed to delete transactions for order {order_id}: {str(e)}")
            return None
    
    # ====== LEGACY SALES METHODS (for backward compatibility) ======
    
    def add_sale(self, sale_data):
        """Legacy method - redirects to add_order for compatibility"""
        # Convert legacy sale format to order format
        order_data = {
            'order_id': f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'customer_name': sale_data.get('customer', 'Walk-in Customer'),
            'customer_phone': '',
            'customer_address': '',
            'item_name': sale_data.get('item_name', ''),
            'quantity': sale_data.get('quantity', 0),
            'unit_price': sale_data.get('price_per_unit', 0),
            'total_amount': sale_data.get('quantity', 0) * sale_data.get('price_per_unit', 0),
            'advance_payment': sale_data.get('quantity', 0) * sale_data.get('price_per_unit', 0),  # Full payment
            'due_amount': 0,
            'order_status': 'Delivered',
            'payment_method': 'Cash',
            'due_date': sale_data.get('date', date.today().strftime("%Y-%m-%d")),
            'order_date': sale_data.get('date', date.today().strftime("%Y-%m-%d"))
        }
        
        return self.add_order(order_data)
    
    def get_sales(self, query=None):
        """Legacy method - returns orders as sales for compatibility"""
        try:
            if query is None:
                query = {}
            orders = self.db_manager.find_documents("orders", query)
            
            # Convert orders to legacy sales format
            sales = []
            for order in orders:
                sale = {
                    'item_name': order.get('item_name', ''),
                    'quantity': order.get('quantity', 0),
                    'price_per_unit': order.get('unit_price', 0),
                    'customer': order.get('customer_name', ''),
                    'date': order.get('order_date', ''),
                    '_id': order.get('_id')
                }
                sales.append(sale)
            
            return sales
        except Exception as e:
            logger.error(f"Failed to get sales: {str(e)}")
            return []
