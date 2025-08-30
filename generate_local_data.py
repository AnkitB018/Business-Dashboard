#!/usr/bin/env python3
"""
Local Sample Data Generator for Business Dashboard
Creates sample data in Excel/CSV format for testing without database
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalSampleDataGenerator:
    def __init__(self):
        self.output_dir = "sample_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Sample data pools (same as before)
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
        """Generate employee data"""
        logger.info(f"Generating {count} employee records...")
        
        employees = []
        for i in range(count):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            
            employee = {
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
            employees.append(employee)
        
        df = pd.DataFrame(employees)
        df.to_excel(f"{self.output_dir}/employees.xlsx", index=False)
        df.to_csv(f"{self.output_dir}/employees.csv", index=False)
        logger.info(f"Created employees.xlsx and employees.csv with {count} records")
        return df
    
    def generate_attendance(self, employees_df, count=50):
        """Generate attendance data"""
        logger.info(f"Generating {count} attendance records...")
        
        if employees_df.empty:
            logger.warning("No employees data provided")
            return pd.DataFrame()
        
        employee_ids = employees_df['employee_id'].tolist()
        employee_names = employees_df['name'].tolist()
        
        statuses = ["Present", "Absent", "Late", "Remote Work"]
        attendance = []
        
        for i in range(count):
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
            
            record = {
                "employee_id": employee_id,
                "employee_name": employee_name,
                "date": self.random_date(
                    datetime(2024, 1, 1), 
                    datetime(2024, 12, 31)
                ).strftime('%Y-%m-%d'),
                "time_in": time_in,
                "time_out": time_out,
                "status": status,
                "hours": hours
            }
            attendance.append(record)
        
        df = pd.DataFrame(attendance)
        df.to_excel(f"{self.output_dir}/attendance.xlsx", index=False)
        df.to_csv(f"{self.output_dir}/attendance.csv", index=False)
        logger.info(f"Created attendance.xlsx and attendance.csv with {count} records")
        return df
    
    def generate_stock(self, count=45):
        """Generate stock data"""
        logger.info(f"Generating {count} stock records...")
        
        stock = []
        for i in range(count):
            category = random.choice(self.stock_categories)
            item_name = random.choice(self.item_names[category])
            quantity = random.randint(5, 500)
            price = round(random.uniform(10.0, 2000.0), 2)
            
            item = {
                "item_name": f"{item_name} - {random.choice(['Pro', 'Standard', 'Premium', 'Basic', 'Advanced'])}",
                "category": category,
                "current_quantity": quantity,
                "unit_price": price,
                "supplier": random.choice(self.suppliers),
                "total_value": round(quantity * price, 2),
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            stock.append(item)
        
        df = pd.DataFrame(stock)
        df.to_excel(f"{self.output_dir}/stock.xlsx", index=False)
        df.to_csv(f"{self.output_dir}/stock.csv", index=False)
        logger.info(f"Created stock.xlsx and stock.csv with {count} records")
        return df
    
    def generate_sales(self, stock_df, count=50):
        """Generate sales data"""
        logger.info(f"Generating {count} sales records...")
        
        if stock_df.empty:
            logger.warning("No stock data provided")
            return pd.DataFrame()
        
        stock_items = stock_df['item_name'].tolist()
        sales = []
        
        for i in range(count):
            item_name = random.choice(stock_items)
            quantity = random.randint(1, 20)
            unit_price = round(random.uniform(15.0, 2500.0), 2)
            
            sale = {
                "item_name": item_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": round(quantity * unit_price, 2),
                "customer_name": random.choice(self.customers),
                "date": self.random_date(
                    datetime(2024, 1, 1), 
                    datetime(2024, 12, 31)
                ).strftime('%Y-%m-%d')
            }
            sales.append(sale)
        
        df = pd.DataFrame(sales)
        df.to_excel(f"{self.output_dir}/sales.xlsx", index=False)
        df.to_csv(f"{self.output_dir}/sales.csv", index=False)
        logger.info(f"Created sales.xlsx and sales.csv with {count} records")
        return df
    
    def generate_purchases(self, count=45):
        """Generate purchase data"""
        logger.info(f"Generating {count} purchase records...")
        
        purchases = []
        for i in range(count):
            category = random.choice(self.stock_categories)
            item_name = random.choice(self.item_names[category])
            quantity = random.randint(10, 200)
            unit_price = round(random.uniform(8.0, 1800.0), 2)
            
            purchase = {
                "item_name": f"{item_name} - {random.choice(['Model A', 'Model B', 'Version 2024', 'Pro Edition', 'Standard'])}",
                "category": category,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": round(quantity * unit_price, 2),
                "supplier": random.choice(self.suppliers),
                "date": self.random_date(
                    datetime(2024, 1, 1), 
                    datetime(2024, 12, 31)
                ).strftime('%Y-%m-%d')
            }
            purchases.append(purchase)
        
        df = pd.DataFrame(purchases)
        df.to_excel(f"{self.output_dir}/purchases.xlsx", index=False)
        df.to_csv(f"{self.output_dir}/purchases.csv", index=False)
        logger.info(f"Created purchases.xlsx and purchases.csv with {count} records")
        return df
    
    def random_date(self, start_date, end_date):
        """Generate a random date between start_date and end_date"""
        time_between = end_date - start_date
        days_between = time_between.days
        random_number_of_days = random.randrange(days_between)
        return start_date + timedelta(days=random_number_of_days)
    
    def generate_all_data(self):
        """Generate all sample data"""
        logger.info("🚀 Starting local sample data generation...")
        
        try:
            # Generate data in order
            employees_df = self.generate_employees(50)
            stock_df = self.generate_stock(45)
            attendance_df = self.generate_attendance(employees_df, 50)
            sales_df = self.generate_sales(stock_df, 50)
            purchases_df = self.generate_purchases(45)
            
            # Create a combined workbook
            with pd.ExcelWriter(f"{self.output_dir}/business_data_complete.xlsx") as writer:
                employees_df.to_excel(writer, sheet_name='Employees', index=False)
                attendance_df.to_excel(writer, sheet_name='Attendance', index=False)
                stock_df.to_excel(writer, sheet_name='Stock', index=False)
                sales_df.to_excel(writer, sheet_name='Sales', index=False)
                purchases_df.to_excel(writer, sheet_name='Purchases', index=False)
            
            logger.info("✅ All sample data generated successfully!")
            logger.info("📊 Data Summary:")
            logger.info(f"   📝 Employees: {len(employees_df)}")
            logger.info(f"   📅 Attendance Records: {len(attendance_df)}")
            logger.info(f"   📦 Stock Items: {len(stock_df)}")
            logger.info(f"   💰 Sales Records: {len(sales_df)}")
            logger.info(f"   🛒 Purchase Records: {len(purchases_df)}")
            logger.info(f"📁 Files created in '{self.output_dir}' directory")
            
            return {
                'employees': employees_df,
                'attendance': attendance_df,
                'stock': stock_df,
                'sales': sales_df,
                'purchases': purchases_df
            }
            
        except Exception as e:
            logger.error(f"❌ Error during data generation: {e}")
            return None

def main():
    """Main function to run the local sample data generator"""
    print("🏢 Business Dashboard - Local Sample Data Generator")
    print("=" * 55)
    print("This will create Excel and CSV files with sample data")
    print("that you can use to test the Business Dashboard.")
    
    try:
        generator = LocalSampleDataGenerator()
        
        print("\nGenerating comprehensive sample data...")
        data = generator.generate_all_data()
        
        if data:
            print("\n✨ Sample data generation completed!")
            print("🎯 Files created:")
            print("   📄 business_data_complete.xlsx (All data in one file)")
            print("   📄 Individual Excel files for each module")
            print("   📄 Individual CSV files for each module")
            print("\n💡 You can now:")
            print("   1. Import this data into your database")
            print("   2. Use the files directly for testing")
            print("   3. Copy the existing business_data.xlsx if needed")
            
            # Ask if user wants to replace the existing business_data.xlsx
            replace = input("\n🔄 Replace existing business_data.xlsx with new sample data? (y/n): ").lower().strip()
            if replace == 'y':
                import shutil
                source = "sample_data/business_data_complete.xlsx"
                target = "business_data.xlsx"
                if os.path.exists(source):
                    shutil.copy2(source, target)
                    print(f"✅ Replaced {target} with new sample data")
                else:
                    print("❌ Source file not found")
        
    except Exception as e:
        logger.error(f"❌ Failed to generate sample data: {e}")
        print("\nPlease make sure:")
        print("1. You have write permissions in the current directory")
        print("2. Required packages (pandas, openpyxl) are installed")

if __name__ == "__main__":
    main()
