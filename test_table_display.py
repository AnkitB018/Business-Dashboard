#!/usr/bin/env python3
"""
Simple test to verify customer table functionality
"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_service import HRDataService

def test_customer_table():
    """Test customer table display"""
    
    # Create a simple window
    root = ctk.CTk()
    root.title("Customer Table Test")
    root.geometry("800x600")
    
    # Create a frame
    frame = ctk.CTkFrame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Create title
    title = ctk.CTkLabel(frame, text="Customer Table Test", font=ctk.CTkFont(size=16, weight="bold"))
    title.pack(pady=10)
    
    # Create table frame
    table_frame = ctk.CTkFrame(frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create treeview
    columns = ("Name", "Contact", "GST Number", "Address", "Due Payment")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
    
    # Configure columns
    column_configs = {
        "Name": 150,
        "Contact": 120,
        "GST Number": 150,
        "Address": 200,
        "Due Payment": 100
    }
    
    for col, width in column_configs.items():
        tree.heading(col, text=col)
        tree.column(col, width=width, minwidth=80)
    
    # Pack the tree
    tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Load customer data
    try:
        service = HRDataService()
        customers_df = service.get_customers()
        
        print(f"Loaded {len(customers_df)} customers")
        
        if not customers_df.empty:
            for _, customer in customers_df.iterrows():
                name = customer.get('name', '')
                contact = customer.get('contact_number', '')
                gst = customer.get('gst_number', '')
                address = customer.get('address', '')[:30] + "..." if len(str(customer.get('address', ''))) > 30 else customer.get('address', '')
                due_payment = f"₹{customer.get('due_payment', 0):.2f}"
                
                tree.insert("", "end", values=(name, contact, gst, address, due_payment))
                print(f"Added: {name} | {contact} | {due_payment}")
        else:
            print("No customers found!")
            
    except Exception as e:
        print(f"Error loading customers: {e}")
        # Add some sample data for testing
        tree.insert("", "end", values=("Test Customer", "1234567890", "GST123", "Test Address", "₹100.00"))
        
    # Add status label
    status = ctk.CTkLabel(frame, text=f"Loaded {len(customers_df) if 'customers_df' in locals() and not customers_df.empty else 0} customers")
    status.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_customer_table()
