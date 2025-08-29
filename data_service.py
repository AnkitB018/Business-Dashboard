import pandas as pd
from database import get_db_manager
from datetime import datetime, date
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

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
                "Stock": self._migrate_stock,
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
    
    def _migrate_stock(self, df: pd.DataFrame) -> bool:
        """Migrate stock data"""
        try:
            for _, row in df.iterrows():
                stock_doc = {
                    "item_name": str(row.get("Item Name", "")),
                    "category": str(row.get("Category", "")),
                    "current_quantity": float(row.get("Current Quantity", 0)) if pd.notna(row.get("Current Quantity")) else 0,
                    "unit_cost_average": float(row.get("Unit Cost on Average", 0)) if pd.notna(row.get("Unit Cost on Average")) else 0,
                    "minimum_stock": 10  # Default minimum stock
                }
                
                # Check if item already exists
                existing = self.db_manager.find_documents(
                    "stock", 
                    {"item_name": stock_doc["item_name"]}
                )
                
                if not existing:
                    self.db_manager.insert_document("stock", stock_doc)
                else:
                    # Update existing stock
                    self.db_manager.update_document(
                        "stock",
                        {"item_name": stock_doc["item_name"]},
                        stock_doc
                    )
            
            return True
        except Exception as e:
            logger.error(f"Error migrating stock: {e}")
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
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    # Employee operations
    def get_employees(self, filter_dict: Dict = None) -> pd.DataFrame:
        """Get employees as DataFrame"""
        return self.db_manager.get_collection_as_dataframe("employees", filter_dict)
    
    def add_employee(self, employee_data: Dict) -> str:
        """Add new employee"""
        # Ensure employee_id is unique
        existing = self.db_manager.find_documents("employees", {"employee_id": employee_data["employee_id"]})
        if existing:
            raise ValueError(f"Employee ID {employee_data['employee_id']} already exists")
        
        return self.db_manager.insert_document("employees", employee_data)
    
    def update_employee(self, employee_id: str, update_data: Dict) -> int:
        """Update employee data"""
        return self.db_manager.update_document("employees", {"employee_id": employee_id}, update_data)
    
    def delete_employee(self, employee_id: str) -> int:
        """Delete employee"""
        return self.db_manager.delete_documents("employees", {"employee_id": employee_id})
    
    # Attendance operations
    def get_attendance(self, filter_dict: Dict = None) -> pd.DataFrame:
        """Get attendance as DataFrame"""
        return self.db_manager.get_collection_as_dataframe("attendance", filter_dict)
    
    def add_attendance(self, attendance_data: Dict) -> str:
        """Add attendance record"""
        # Check for duplicate entries
        existing = self.db_manager.find_documents(
            "attendance", 
            {
                "employee_id": attendance_data["employee_id"],
                "date": attendance_data["date"]
            }
        )
        if existing:
            raise ValueError("Attendance record already exists for this employee and date")
        
        return self.db_manager.insert_document("attendance", attendance_data)
    
    def delete_attendance(self, filter_dict: Dict) -> int:
        """Delete attendance records"""
        return self.db_manager.delete_documents("attendance", filter_dict)
    
    # Stock operations
    def get_stock(self, filter_dict: Dict = None) -> pd.DataFrame:
        """Get stock as DataFrame"""
        return self.db_manager.get_collection_as_dataframe("stock", filter_dict)
    
    def update_stock(self, item_name: str, update_data: Dict) -> int:
        """Update stock data"""
        return self.db_manager.update_document("stock", {"item_name": item_name}, update_data)
    
    def add_stock_item(self, stock_data: Dict) -> str:
        """Add new stock item"""
        return self.db_manager.insert_document("stock", stock_data)
    
    def delete_stock_item(self, item_name: str) -> int:
        """Delete stock item"""
        return self.db_manager.delete_documents("stock", {"item_name": item_name})
    
    # Purchase operations
    def get_purchases(self, filter_dict: Dict = None) -> pd.DataFrame:
        """Get purchases as DataFrame"""
        return self.db_manager.get_collection_as_dataframe("purchases", filter_dict)
    
    def add_purchase(self, purchase_data: Dict) -> str:
        """Add purchase and update stock"""
        # Add purchase record
        purchase_id = self.db_manager.insert_document("purchases", purchase_data)
        
        # Update stock
        self._update_stock_after_purchase(purchase_data)
        
        return purchase_id
    
    def _update_stock_after_purchase(self, purchase_data: Dict):
        """Update stock quantities after purchase"""
        item_name = purchase_data["item_name"]
        quantity = purchase_data["quantity"]
        unit_price = purchase_data["unit_price"]
        
        # Check if item exists in stock
        existing_stock = self.db_manager.find_documents("stock", {"item_name": item_name})
        
        if existing_stock:
            # Update existing stock
            current_stock = existing_stock[0]
            old_qty = current_stock["current_quantity"]
            old_cost = current_stock["unit_cost_average"]
            
            new_qty = old_qty + quantity
            new_cost = ((old_qty * old_cost) + (quantity * unit_price)) / new_qty
            
            self.db_manager.update_document(
                "stock",
                {"item_name": item_name},
                {
                    "current_quantity": new_qty,
                    "unit_cost_average": round(new_cost, 2)
                }
            )
        else:
            # Add new stock item
            new_stock = {
                "item_name": item_name,
                "category": purchase_data.get("category", ""),
                "current_quantity": quantity,
                "unit_cost_average": unit_price,
                "minimum_stock": 10
            }
            self.db_manager.insert_document("stock", new_stock)
    
    # Sales operations
    def get_sales(self, filter_dict: Dict = None) -> pd.DataFrame:
        """Get sales as DataFrame"""
        return self.db_manager.get_collection_as_dataframe("sales", filter_dict)
    
    def add_sale(self, sales_data: Dict) -> str:
        """Add sale and update stock"""
        # Check stock availability
        item_name = sales_data["item_name"]
        quantity = sales_data["quantity"]
        
        stock_items = self.db_manager.find_documents("stock", {"item_name": item_name})
        if not stock_items:
            raise ValueError(f"Item '{item_name}' not found in stock")
        
        current_stock = stock_items[0]["current_quantity"]
        if quantity > current_stock:
            raise ValueError(f"Insufficient stock. Available: {current_stock}")
        
        # Add sales record
        sales_id = self.db_manager.insert_document("sales", sales_data)
        
        # Update stock
        new_quantity = current_stock - quantity
        self.db_manager.update_document(
            "stock",
            {"item_name": item_name},
            {"current_quantity": new_quantity}
        )
        
        return sales_id
    
    def delete_sale(self, filter_dict: Dict) -> int:
        """Delete sales record"""
        return self.db_manager.delete_documents("sales", filter_dict)


# Singleton instance
hr_service = None

def get_hr_service() -> HRDataService:
    """Get singleton instance of HR service"""
    global hr_service
    if hr_service is None:
        hr_service = HRDataService()
    return hr_service
