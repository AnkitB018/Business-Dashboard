#!/usr/bin/env python3
"""
Sample Data Generator for Business Dashboard
Generates comprehensive test data for all modules
"""

import random
from datetime import datetime, timedelta, date
from data_service import get_hr_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SampleDataGenerator:
    def __init__(self):
        self.hr_service = get_hr_service()
        if not self.hr_service:
            raise Exception("Failed to connect to database")
        
        # Sample data pools
        self.first_names = [
            "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa",
            "William", "Jennifer", "James", "Mary", "Christopher", "Patricia", "Daniel",
            "Linda", "Matthew", "Elizabeth", "Anthony", "Barbara", "Mark", "Susan",
            "Donald", "Jessica", "Steven", "Helen", "Paul", "Nancy", "Andrew", "Karen",
            "Joshua", "Betty", "Kenneth", "Dorothy", "Kevin", "Sandra", "Brian", "Donna",
            "George", "Carol", "Edward", "Ruth", "Ronald", "Sharon", "Timothy", "Michelle",
            "Jason", "Laura", "Jeffrey", "Sarah"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
            "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
            "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
            "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
            "Mitchell", "Carter", "Roberts"
        ]
        
        self.departments = [
            "Human Resources", "Finance", "Engineering", "Marketing", "Sales",
            "Operations", "IT Support", "Legal", "Research & Development", "Customer Service"
        ]
        
        self.positions = [
            "Manager", "Senior Developer", "Junior Developer", "Analyst", "Coordinator",
            "Specialist", "Executive", "Assistant", "Lead", "Director", "Consultant",
            "Administrator", "Representative", "Engineer", "Designer"
        ]
        
        self.stock_categories = [
            "Electronics", "Office Supplies", "Furniture", "Software", "Hardware",
            "Books", "Stationery", "Equipment", "Tools", "Materials"
        ]
        
        self.item_names = {
            "Electronics": ["Laptop", "Desktop PC", "Monitor", "Keyboard", "Mouse", "Tablet", "Smartphone", "Printer", "Scanner", "Router"],
            "Office Supplies": ["Paper", "Pens", "Pencils", "Staplers", "Paper Clips", "Folders", "Binders", "Markers", "Erasers", "Scissors"],
            "Furniture": ["Office Chair", "Desk", "Filing Cabinet", "Bookshelf", "Conference Table", "Reception Desk", "Storage Unit", "Partition", "Whiteboard", "Cork Board"],
            "Software": ["Microsoft Office", "Adobe Creative Suite", "Antivirus", "Project Management Tool", "CRM Software", "Accounting Software", "Design Software", "Database Software", "Communication Tool", "Analytics Tool"],
            "Hardware": ["Hard Drive", "RAM", "Graphics Card", "Motherboard", "Power Supply", "CPU", "Network Card", "Sound Card", "Cables", "Adapters"],
            "Books": ["Programming Guide", "Business Strategy", "Marketing Handbook", "Finance Manual", "HR Policies", "Technical Documentation", "Training Materials", "Reference Book", "Industry Report", "Best Practices"],
            "Stationery": ["Notebooks", "Post-it Notes", "Highlighters", "Rubber Bands", "Push Pins", "Tape", "Glue", "Calculator", "Ruler", "Correction Fluid"],
            "Equipment": ["Projector", "Camera", "Microphone", "Speakers", "Headphones", "Webcam", "Conference Phone", "Laminator", "Shredder", "Binding Machine"],
            "Tools": ["Screwdriver Set", "Wire Strippers", "Multimeter", "Soldering Iron", "Drill", "Hammer", "Pliers", "Level", "Measuring Tape", "Utility Knife"],
            "Materials": ["Cable Ties", "Screws", "Bolts", "Washers", "Wire", "Solder", "Cleaning Supplies", "Labels", "Packaging", "Protective Gear"]
        }
        
        self.suppliers = [
            "TechCorp Solutions", "Office Plus Ltd", "Global Supplies Inc", "Prime Electronics",
            "Business Essentials Co", "Digital World Ltd", "Corporate Supplies", "Tech Innovations",
            "Office Depot Pro", "Industrial Supplies Ltd", "Smart Solutions Inc", "Modern Office Co",
            "Technology Partners", "Supply Chain Masters", "Equipment Specialists", "Quality Suppliers Ltd"
        ]
        
        self.customers = [
            "ABC Corporation", "XYZ Industries", "Global Tech Inc", "Business Solutions Ltd",
            "Enterprise Systems", "Innovation Labs", "Corporate Services", "Digital Dynamics",
            "Future Technologies", "Smart Business Co", "Advanced Solutions", "Prime Enterprises",
            "Tech Innovators Ltd", "Modern Systems Inc", "Quality Services Co", "Professional Corp"
        ]
    
    def generate_employees(self, count=50):
        """Generate sample employee data"""
        logger.info(f"Generating {count} employee records...")
        
        for i in range(count):
            try:
                first_name = random.choice(self.first_names)
                last_name = random.choice(self.last_names)
                
                employee_data = {
                    "employee_id": f"EMP{1000 + i:03d}",
                    "name": f"{first_name} {last_name}",
                    "email": f"{first_name.lower()}.{last_name.lower()}@company.com",
                    "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                    "department": random.choice(self.departments),
                    "position": random.choice(self.positions),
                    "salary": round(random.uniform(30000, 120000), 2),
                    "joining_date": self.random_date(
                        datetime(2020, 1, 1), 
                        datetime(2024, 12, 31)
                    ).strftime('%Y-%m-%d')
                }
                
                result = self.hr_service.add_employee(employee_data)
                if result:
                    logger.info(f"Added employee: {employee_data['name']}")
                
            except Exception as e:
                logger.error(f"Error adding employee {i}: {e}")
        
        logger.info("Employee data generation completed")
    
    def generate_attendance(self, count=50):
        """Generate sample attendance data"""
        logger.info(f"Generating {count} attendance records...")
        
        # Get existing employees
        employees_df = self.hr_service.get_employees()
        if employees_df.empty:
            logger.warning("No employees found. Please generate employee data first.")
            return
        
        employee_ids = employees_df['employee_id'].tolist()
        employee_names = employees_df['name'].tolist()
        
        statuses = ["Present", "Absent", "Late", "Remote Work"]
        
        for i in range(count):
            try:
                emp_index = random.randint(0, len(employee_ids) - 1)
                employee_id = employee_ids[emp_index]
                employee_name = employee_names[emp_index]
                status = random.choice(statuses)
                
                # Generate realistic time data based on status
                if status == "Present":
                    time_in = f"{random.randint(8, 9)}:{random.randint(0, 59):02d}"
                    time_out = f"{random.randint(17, 18)}:{random.randint(0, 59):02d}"
                    hours = round(random.uniform(8.0, 9.5), 1)
                elif status == "Late":
                    time_in = f"{random.randint(9, 11)}:{random.randint(0, 59):02d}"
                    time_out = f"{random.randint(17, 19)}:{random.randint(0, 59):02d}"
                    hours = round(random.uniform(6.0, 8.5), 1)
                elif status == "Remote Work":
                    time_in = f"{random.randint(8, 10)}:{random.randint(0, 59):02d}"
                    time_out = f"{random.randint(16, 18)}:{random.randint(0, 59):02d}"
                    hours = round(random.uniform(7.5, 9.0), 1)
                else:  # Absent
                    time_in = ""
                    time_out = ""
                    hours = 0.0
                
                attendance_data = {
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "date": self.random_date(
                        datetime(2024, 1, 1), 
                        datetime(2024, 12, 31)
                    ),
                    "time_in": time_in,
                    "time_out": time_out,
                    "status": status,
                    "hours": hours
                }
                
                result = self.hr_service.add_attendance(attendance_data)
                if result:
                    logger.info(f"Added attendance for {employee_name} on {attendance_data['date']}")
                
            except Exception as e:
                logger.error(f"Error adding attendance {i}: {e}")
        
        logger.info("Attendance data generation completed")
    
    def generate_stock(self, count=45):
        """Generate sample stock data"""
        logger.info(f"Generating {count} stock records...")
        
        for i in range(count):
            try:
                category = random.choice(self.stock_categories)
                item_name = random.choice(self.item_names[category])
                quantity = random.randint(5, 500)
                price = round(random.uniform(10.0, 2000.0), 2)
                
                stock_data = {
                    "item_name": f"{item_name} - {random.choice(['Pro', 'Standard', 'Premium', 'Basic', 'Advanced'])}",
                    "category": category,
                    "current_quantity": quantity,
                    "unit_price": price,
                    "supplier": random.choice(self.suppliers),
                    "total_value": round(quantity * price, 2),
                    "last_updated": datetime.now()
                }
                
                result = self.hr_service.add_stock_item(stock_data)
                if result:
                    logger.info(f"Added stock item: {stock_data['item_name']}")
                
            except Exception as e:
                logger.error(f"Error adding stock item {i}: {e}")
        
        logger.info("Stock data generation completed")
    
    def generate_sales(self, count=50):
        """Generate sample sales data"""
        logger.info(f"Generating {count} sales records...")
        
        # Get existing stock items
        stock_df = self.hr_service.get_stock()
        if stock_df.empty:
            logger.warning("No stock items found. Please generate stock data first.")
            return
        
        stock_items = stock_df['item_name'].tolist()
        
        for i in range(count):
            try:
                item_name = random.choice(stock_items)
                quantity = random.randint(1, 20)
                unit_price = round(random.uniform(15.0, 2500.0), 2)
                
                sales_data = {
                    "item_name": item_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": round(quantity * unit_price, 2),
                    "customer_name": random.choice(self.customers),
                    "date": self.random_date(
                        datetime(2024, 1, 1), 
                        datetime(2024, 12, 31)
                    )
                }
                
                result = self.hr_service.add_sale(sales_data)
                if result:
                    logger.info(f"Added sale: {quantity}x {item_name}")
                
            except Exception as e:
                logger.error(f"Error adding sale {i}: {e}")
        
        logger.info("Sales data generation completed")
    
    def generate_purchases(self, count=45):
        """Generate sample purchase data"""
        logger.info(f"Generating {count} purchase records...")
        
        for i in range(count):
            try:
                category = random.choice(self.stock_categories)
                item_name = random.choice(self.item_names[category])
                quantity = random.randint(10, 200)
                unit_price = round(random.uniform(8.0, 1800.0), 2)
                
                purchase_data = {
                    "item_name": f"{item_name} - {random.choice(['Model A', 'Model B', 'Version 2024', 'Pro Edition', 'Standard'])}",
                    "category": category,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": round(quantity * unit_price, 2),
                    "supplier": random.choice(self.suppliers),
                    "date": self.random_date(
                        datetime(2024, 1, 1), 
                        datetime(2024, 12, 31)
                    )
                }
                
                result = self.hr_service.add_purchase(purchase_data)
                if result:
                    logger.info(f"Added purchase: {quantity}x {purchase_data['item_name']}")
                
            except Exception as e:
                logger.error(f"Error adding purchase {i}: {e}")
        
        logger.info("Purchase data generation completed")
    
    def random_date(self, start_date, end_date):
        """Generate a random date between start_date and end_date"""
        time_between = end_date - start_date
        days_between = time_between.days
        random_number_of_days = random.randrange(days_between)
        return start_date + timedelta(days=random_number_of_days)
    
    def generate_all_data(self):
        """Generate all sample data"""
        logger.info("🚀 Starting comprehensive sample data generation...")
        
        try:
            # Generate data in order (employees first for attendance dependency)
            self.generate_employees(50)
            self.generate_stock(45)
            self.generate_attendance(50)
            self.generate_sales(50)
            self.generate_purchases(45)
            
            logger.info("✅ All sample data generated successfully!")
            logger.info("📊 Data Summary:")
            
            # Get counts
            employees_count = len(self.hr_service.get_employees())
            attendance_count = len(self.hr_service.get_attendance())
            stock_count = len(self.hr_service.get_stock())
            sales_count = len(self.hr_service.get_sales())
            purchases_count = len(self.hr_service.get_purchases())
            
            logger.info(f"   📝 Employees: {employees_count}")
            logger.info(f"   📅 Attendance Records: {attendance_count}")
            logger.info(f"   📦 Stock Items: {stock_count}")
            logger.info(f"   💰 Sales Records: {sales_count}")
            logger.info(f"   🛒 Purchase Records: {purchases_count}")
            
        except Exception as e:
            logger.error(f"❌ Error during data generation: {e}")
            logger.error("Make sure MongoDB is running and accessible")
    
    def clear_all_data(self):
        """Clear all existing data (use with caution!)"""
        logger.warning("🗑️ Clearing all existing data...")
        
        try:
            # Note: This would need proper implementation in database.py
            # For now, just inform the user
            logger.info("To clear all data, you would need to:")
            logger.info("1. Connect to your MongoDB instance")
            logger.info("2. Drop the collections: employees, attendance, stock, sales, purchases")
            logger.info("3. Or use MongoDB Compass/CLI to clear the data")
            
        except Exception as e:
            logger.error(f"❌ Error during data clearing: {e}")

def main():
    """Main function to run the sample data generator"""
    print("🏢 Business Dashboard - Sample Data Generator")
    print("=" * 50)
    
    try:
        generator = SampleDataGenerator()
        
        print("\nChoose an option:")
        print("1. Generate all sample data (recommended)")
        print("2. Generate only employee data")
        print("3. Generate only attendance data")
        print("4. Generate only stock data")
        print("5. Generate only sales data")
        print("6. Generate only purchase data")
        print("7. Clear all data (⚠️ WARNING)")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            generator.generate_all_data()
        elif choice == "2":
            generator.generate_employees(50)
        elif choice == "3":
            generator.generate_attendance(50)
        elif choice == "4":
            generator.generate_stock(45)
        elif choice == "5":
            generator.generate_sales(50)
        elif choice == "6":
            generator.generate_purchases(45)
        elif choice == "7":
            confirm = input("⚠️ This will delete ALL data. Type 'YES' to confirm: ")
            if confirm == "YES":
                generator.clear_all_data()
            else:
                print("Operation cancelled.")
        else:
            print("Invalid choice. Please run the script again.")
        
        print("\n✨ Sample data generator completed!")
        print("🎯 You can now test the Business Dashboard with realistic data.")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize sample data generator: {e}")
        print("\nPlease make sure:")
        print("1. MongoDB is running and accessible")
        print("2. Database connection is properly configured")
        print("3. All required dependencies are installed")

if __name__ == "__main__":
    main()
