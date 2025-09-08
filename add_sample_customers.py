"""
Script to add sample customers to test the customer management functionality
"""

from data_service import get_hr_service

def add_sample_customers():
    """Add sample customers to the database"""
    hr_service = get_hr_service()
    
    sample_customers = [
        {
            "name": "John Smith",
            "contact_number": "+91 9876543210",
            "gst_number": "29ABCDE1234F1Z5",
            "address": "123 Main Street, Mumbai, Maharashtra 400001"
        },
        {
            "name": "Sarah Johnson",
            "contact_number": "+91 9876543211",
            "gst_number": "29FGHIJ5678K2A9",
            "address": "456 Park Avenue, Delhi, Delhi 110001"
        },
        {
            "name": "Michael Chen",
            "contact_number": "+91 9876543212",
            "gst_number": "",
            "address": "789 Business Plaza, Bangalore, Karnataka 560001"
        },
        {
            "name": "Emily Davis",
            "contact_number": "+91 9876543213",
            "gst_number": "29LMNOP9012Q3R4",
            "address": "321 Tech Park, Hyderabad, Telangana 500001"
        },
        {
            "name": "Robert Wilson",
            "contact_number": "+91 9876543214",
            "gst_number": "",
            "address": ""
        }
    ]
    
    print("Adding sample customers...")
    
    for customer in sample_customers:
        try:
            result = hr_service.add_customer(customer)
            print(f"✅ Added customer: {customer['name']} (ID: {result})")
        except Exception as e:
            print(f"❌ Failed to add customer {customer['name']}: {str(e)}")
    
    print("\nSample customers added successfully!")
    
    # Update due payments for all customers
    hr_service.update_all_customer_due_payments()
    print("✅ Updated due payments for all customers")

if __name__ == "__main__":
    add_sample_customers()
