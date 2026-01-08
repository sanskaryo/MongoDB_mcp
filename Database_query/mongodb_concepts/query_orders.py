# Query Documents - Find and filter data

import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
mongodb_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/hotel_management')
client = pymongo.MongoClient(mongodb_uri)
db = client['hotel_management']

orders = db.orders

# Check what fields exist in the orders
sample_order = orders.find_one()
print("Available fields in orders:")
if sample_order:
    for key in sample_order.keys():
        print(f"  - {key}: {sample_order[key]}")
    print()

# Find all orders (using correct field names)
print("All orders:")
for order in orders.find().limit(3):
    order_id = order.get('_id')
    customer_id = order.get('customer_id') 
    total_amount = order.get('total_amount')
    status = order.get('order_status', 'unknown')
    print(f"  {order_id}: Customer {customer_id} - ${total_amount} ({status})")

# Find by status (using correct field name)
print("\nCompleted orders:")
for order in orders.find({"order_status": "completed"}).limit(3):
    order_id = order.get('_id')
    customer_id = order.get('customer_id')
    total_amount = order.get('total_amount')
    print(f"  {order_id}: Customer {customer_id} - ${total_amount}")

# Find by amount range
print("\nOrders over $50:")
for order in orders.find({"total_amount": {"$gt": 50}}).limit(3):
    order_id = order.get('_id') 
    customer_id = order.get('customer_id')
    total_amount = order.get('total_amount')
    print(f"  {order_id}: Customer {customer_id} - ${total_amount}")