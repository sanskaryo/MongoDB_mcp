# Search Orders - Advanced filtering

import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
mongodb_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/hotel_management')
client = pymongo.MongoClient(mongodb_uri)
db = client['hotel_management']

orders = db.orders

# Search by order ID (partial match)
print("Orders with 'order_000' in ID:")
# $regex: "order_000" - Find any _id field that CONTAINS the text "order_000" anywhere in it
# $options: "i" - Make the search case-insensitive (ignores upper/lowercase)
for order in orders.find({"_id": {"$regex": "order_000", "$options": "i"}}).limit(3):
    print(f"  {order.get('_id')}: Customer {order.get('customer_id')} - ${order.get('total_amount')}")

# Search by date range (orders from 2024)
print("\nOrders from 2024:")
# $regex: "^2024" - The ^ symbol means "starts with", so find dates that START with "2024"
# This will match: "2024-01-01", "2024-12-25", etc. but NOT "2023-2024" or "in 2024"
for order in orders.find({"created_at": {"$regex": "^2024"}}).limit(3):
    print(f"  {order.get('_id')}: {order.get('created_at')} - ${order.get('total_amount')}")

# Search in items array (orders containing specific food)
print("\nOrders containing 'Rice' items:")
# "items.name" - Search inside the items array, specifically in the "name" field of each item
# $regex: "Rice" - Find any item name that CONTAINS the word "Rice"
# $options: "i" - Case-insensitive, so matches "rice", "Rice", "RICE", etc.
for order in orders.find({"items.name": {"$regex": "Rice", "$options": "i"}}).limit(3):
    items_with_rice = [item['name'] for item in order.get('items', []) if 'rice' in item['name'].lower()]
    print(f"  {order.get('_id')}: {items_with_rice} - ${order.get('total_amount')}")

# Multiple conditions with regex
print("\nCompleted orders over $1000 from September 2024:")
# This combines 3 conditions - ALL must be true:
# 1. "order_status": "completed" - Exact match for status field
# 2. "total_amount": {"$gt": 1000} - $gt means "greater than" 1000
# 3. "created_at": {"$regex": "^2024-09"} - Date starts with "2024-09" (September 2024)
for order in orders.find({
    "order_status": "completed",        # Exact string match
    "total_amount": {"$gt": 1000},      # Number greater than 1000
    "created_at": {"$regex": "^2024-09"} # String starts with "2024-09"
}).limit(3):
    print(f"  {order.get('_id')}: ${order.get('total_amount')} on {order.get('created_at')}")

# Advanced regex patterns
print("\nOrders with UPI payment:")
# $regex: "upi" - Find any payment_mode that CONTAINS "upi"
# $options: "i" - Case-insensitive, so matches "UPI", "upi", "Upi", etc.
for order in orders.find({"payment_mode": {"$regex": "upi", "$options": "i"}}).limit(3):
    print(f"  {order.get('_id')}: {order.get('payment_mode')} - ${order.get('total_amount')}")