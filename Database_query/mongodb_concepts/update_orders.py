# Update Documents - Modify existing data

import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
mongodb_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/hotel_management')
client = pymongo.MongoClient(mongodb_uri)
db = client['hotel_management']

orders = db.orders

# Show current order status before updates
print("=== BEFORE UPDATES ===")
sample_orders = list(orders.find().limit(5))
for order in sample_orders:
    print(f"  {order.get('_id')}: {order.get('order_status')} - ${order.get('total_amount')}")

print("\n=== PERFORMING UPDATES ===")

# 1. UPDATE ONE ORDER - Change specific order status to completed
# update_one(filter, update) - Updates the FIRST document that matches the filter
print("1. Updating one order to completed...")
result = orders.update_one(
    {"_id": "order_00002"},  # filter: Find order with this exact _id
    {"$set": {               # $set: Replace/add these fields with new values
        "order_status": "completed", 
        "updated_at": datetime.now().isoformat()
    }}
)
print(f"   → Updated {result.modified_count} order (1 = success, 0 = not found)")

# 2. UPDATE MULTIPLE ORDERS - Change all cancelled orders to refunded
# update_many(filter, update) - Updates ALL documents that match the filter
print("\n2. Updating all cancelled orders to refunded...")
result = orders.update_many(
    {"order_status": "cancelled"},  # filter: Find ALL orders with status "cancelled"
    {"$set": {                      # $set: Set new values for these fields
        "order_status": "refunded",
        "refund_processed_at": datetime.now().isoformat()
    }}
)
print(f"   → Updated {result.modified_count} cancelled orders to refunded")

# 3. INCREMENT VALUES - Add tip to order total
# $inc: Increment (add to) numeric fields
print("\n3. Adding $5 tip to a specific order...")
result = orders.update_one(
    {"_id": "order_00001"},         # filter: Find this specific order
    {"$inc": {"total_amount": 5.0}} # $inc: Add 5.0 to the current total_amount
)
print(f"   → Added tip to {result.modified_count} order")

# 4. PUSH TO ARRAY - Add special instruction to order
# $push: Add new item to an array field
print("\n4. Adding special instruction to an order...")
result = orders.update_one(
    {"_id": "order_00003"},
    {"$push": {                     # $push: Add item to array (creates array if doesn't exist)
        "special_notes": f"Updated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    }}
)
print(f"   → Added note to {result.modified_count} order")

# 5. CONDITIONAL UPDATE - Update only if condition is met
# Use $where or multiple conditions for complex logic
print("\n5. Update high-value orders (>$1500) with VIP status...")
result = orders.update_many(
    {
        "total_amount": {"$gt": 1500},   # filter: Only orders > $1500
        "order_status": "completed"      # AND status is completed
    },
    {"$set": {"vip_order": True}}        # $set: Mark as VIP order
)
print(f"   → Marked {result.modified_count} high-value orders as VIP")

print("\n=== AFTER UPDATES ===")
# Show the updated orders
updated_orders = list(orders.find({"_id": {"$in": ["order_00001", "order_00002", "order_00003"]}}).limit(3))
for order in updated_orders:
    vip_status = " (VIP)" if order.get('vip_order') else ""
    notes = f" - Notes: {order.get('special_notes', [])}" if order.get('special_notes') else ""
    print(f"  {order.get('_id')}: {order.get('order_status')} - ${order.get('total_amount')}{vip_status}{notes}")

print("\n=== UPDATE OPERATIONS SUMMARY ===")
print("• update_one() - Updates first matching document")
print("• update_many() - Updates all matching documents") 
print("• $set - Replaces field values")
print("• $inc - Increments numeric values")
print("• $push - Adds items to arrays")
print("• Filters determine WHICH documents to update")
print("• Update operators determine HOW to modify them")