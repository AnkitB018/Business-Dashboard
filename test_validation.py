#!/usr/bin/env python3
"""
Test script to verify employee data validation functionality
"""

import re

def validate_employee_id(emp_id):
    """Validate employee ID format: 3 letters + 3 digits (e.g., EMP001, HR001)"""
    if not emp_id or len(emp_id.strip()) == 0:
        return False
    
    # Pattern: 3 letters followed by 3 digits
    pattern = r'^[A-Z]{2,4}\d{3,4}$'
    return bool(re.match(pattern, emp_id.strip().upper()))

def validate_email(email):
    """Validate email format with common domains"""
    if not email or len(email.strip()) == 0:
        return False
    
    email = email.strip().lower()
    
    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Check for valid domain extensions
    valid_domains = ['.com', '.org', '.net', '.edu', '.gov', '.in', '.co.in', '.ac.in', '.co.uk']
    return any(email.endswith(domain) for domain in valid_domains)

def validate_phone(phone):
    """Validate phone number: 10 digits or with country code"""
    if not phone or len(phone.strip()) == 0:
        return False
    
    # Remove all non-digit characters except +
    phone_clean = re.sub(r'[^\d+]', '', phone.strip())
    
    # Case 1: 10 digits (Indian mobile)
    if len(phone_clean) == 10 and phone_clean.isdigit():
        # Should start with 6, 7, 8, or 9
        return phone_clean[0] in ['6', '7', '8', '9']
    
    # Case 2: With country code +91
    if phone_clean.startswith('+91') and len(phone_clean) == 13:
        mobile_part = phone_clean[3:]
        return mobile_part.isdigit() and mobile_part[0] in ['6', '7', '8', '9']
    
    # Case 3: Without + but with 91
    if phone_clean.startswith('91') and len(phone_clean) == 12:
        mobile_part = phone_clean[2:]
        return mobile_part.isdigit() and mobile_part[0] in ['6', '7', '8', '9']
    
    return False

def test_validation():
    """Test the validation functions"""
    print("🧪 Testing Employee Data Validation\n")
    
    # Test Employee ID validation
    print("📝 Employee ID Validation:")
    emp_ids = ["EMP001", "HR001", "IT123", "ABC1234", "emp001", "123ABC", "E1", "EMPX", ""]
    for emp_id in emp_ids:
        result = validate_employee_id(emp_id)
        status = "✅ VALID" if result else "❌ INVALID"
        print(f"  {emp_id:<10} → {status}")
    
    print("\n📧 Email Validation:")
    emails = [
        "user@company.com", 
        "test@gmail.com", 
        "employee@company.org",
        "user@company.co.in",
        "invalid.email",
        "user@company.xyz",
        "user@.com",
        ""
    ]
    for email in emails:
        result = validate_email(email)
        status = "✅ VALID" if result else "❌ INVALID"
        print(f"  {email:<20} → {status}")
    
    print("\n📱 Phone Validation:")
    phones = [
        "9876543210",
        "+91 9876543210", 
        "91 9876543210",
        "919876543210",
        "1234567890",
        "98765",
        "+1 9876543210",
        ""
    ]
    for phone in phones:
        result = validate_phone(phone)
        status = "✅ VALID" if result else "❌ INVALID"
        print(f"  {phone:<15} → {status}")

if __name__ == "__main__":
    test_validation()
