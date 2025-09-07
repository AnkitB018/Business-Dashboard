#!/usr/bin/env python3
"""
Test script for the new Orders and Transactions system
This will create some sample orders and transactions to demonstrate the functionality
"""

import sys
import os
from datetime import datetime, date
from data_service import DataService

def create_sample_orders():
    """Create sample orders to test the new system"""
    try:
        data_service = DataService()
        
        # Sample orders data
        sample_orders = [
            {
                'order_id': 'ORD202509070001',
                'customer_name': 'John Smith',
                'customer_phone': '+91 9876543210',
                'customer_address': '123 Main Street, Delhi',
                'item_name': 'Laptop Dell Inspiron',
                'quantity': 1,
                'unit_price': 45000.0,
                'total_amount': 45000.0,
                'advance_payment': 15000.0,
                'due_amount': 30000.0,
                'order_status': 'Processing',
                'payment_method': 'UPI',
                'order_date': '2025-09-07',
                'due_date': '2025-09-15',
                'created_date': datetime.now().isoformat()
            },
            {
                'order_id': 'ORD202509070002',
                'customer_name': 'Priya Sharma',
                'customer_phone': '+91 9876543211',
                'customer_address': '456 Park Avenue, Mumbai',
                'item_name': 'iPhone 15 Pro',
                'quantity': 2,
                'unit_price': 79999.0,
                'total_amount': 159998.0,
                'advance_payment': 50000.0,
                'due_amount': 109998.0,
                'order_status': 'Pending',
                'payment_method': 'Card',
                'order_date': '2025-09-07',
                'due_date': '2025-09-10',
                'created_date': datetime.now().isoformat()
            },
            {
                'order_id': 'ORD202509070003',
                'customer_name': 'Rajesh Kumar',
                'customer_phone': '+91 9876543212',
                'customer_address': '789 Business Center, Bangalore',
                'item_name': 'Samsung 55" QLED TV',
                'quantity': 1,
                'unit_price': 89999.0,
                'total_amount': 89999.0,
                'advance_payment': 89999.0,
                'due_amount': 0.0,
                'order_status': 'Paid',
                'payment_method': 'Bank Transfer',
                'order_date': '2025-09-06',
                'due_date': '2025-09-08',
                'created_date': datetime.now().isoformat()
            },
            {
                'order_id': 'ORD202509070004',
                'customer_name': 'Anita Desai',
                'customer_phone': '+91 9876543213',
                'customer_address': '321 Tech Park, Pune',
                'item_name': 'MacBook Air M2',
                'quantity': 1,
                'unit_price': 124999.0,
                'total_amount': 124999.0,
                'advance_payment': 25000.0,
                'due_amount': 99999.0,
                'order_status': 'Ready',
                'payment_method': 'Cash',
                'order_date': '2025-09-05',
                'due_date': '2025-09-12',
                'created_date': datetime.now().isoformat()
            }
        ]
        
        # Add orders to database
        for order in sample_orders:
            result = data_service.add_order(order)
            if result:
                print(f"✅ Created order: {order['order_id']} for {order['customer_name']}")
                
                # Create initial transaction for advance payment
                if order['advance_payment'] > 0:
                    transaction_data = {
                        'transaction_id': f"TXN{order['order_id'][3:]}01",
                        'order_id': order['order_id'],
                        'payment_amount': order['advance_payment'],
                        'payment_date': order['order_date'],
                        'payment_method': order['payment_method'],
                        'transaction_type': 'advance_payment',
                        'notes': 'Initial advance payment',
                        'created_date': datetime.now().isoformat()
                    }
                    
                    trans_result = data_service.add_transaction(transaction_data)
                    if trans_result:
                        print(f"   💳 Added advance payment transaction: ₹{order['advance_payment']:.2f}")
            else:
                print(f"❌ Failed to create order: {order['order_id']}")
        
        # Add some additional payment transactions
        additional_payments = [
            {
                'transaction_id': 'TXN20250907000102',
                'order_id': 'ORD202509070001',
                'payment_amount': 10000.0,
                'payment_date': '2025-09-07',
                'payment_method': 'Cash',
                'transaction_type': 'payment',
                'notes': 'Partial payment towards balance',
                'created_date': datetime.now().isoformat()
            },
            {
                'transaction_id': 'TXN20250907000202',
                'order_id': 'ORD202509070002',
                'payment_amount': 20000.0,
                'payment_date': '2025-09-07',
                'payment_method': 'UPI',
                'transaction_type': 'payment',
                'notes': 'Second installment payment',
                'created_date': datetime.now().isoformat()
            }
        ]
        
        for payment in additional_payments:
            result = data_service.add_transaction(payment)
            if result:
                print(f"   💰 Added payment: ₹{payment['payment_amount']:.2f} for {payment['order_id']}")
                
                # Update order's advance payment and due amount
                order_data = data_service.get_order_by_id(payment['order_id'])
                if order_data:
                    new_advance = order_data.get('advance_payment', 0) + payment['payment_amount']
                    new_due = order_data.get('total_amount', 0) - new_advance
                    
                    update_data = {
                        'advance_payment': new_advance,
                        'due_amount': new_due
                    }
                    
                    if new_due <= 0:
                        update_data['order_status'] = 'Paid'
                    
                    data_service.update_order(payment['order_id'], update_data)
                    print(f"   📊 Updated order balance: Due amount now ₹{new_due:.2f}")
        
        print("\n🎉 Sample orders and transactions created successfully!")
        print("You can now test the new Sales Management System in the application.")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")

if __name__ == "__main__":
    print("🚀 Creating sample orders and transactions for testing...")
    print("=" * 60)
    create_sample_orders()
    print("=" * 60)
    print("✨ Test completed! Open the application and navigate to Sales Management.")
