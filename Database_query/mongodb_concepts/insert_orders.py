# Insert Documents - Add new data

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

# Insert one order
new_order = {
    "_id": f"order_{int(datetime.now().timestamp())}",
    "customer_id": "cust_test_001",
    "total_amount": 25.99,
    "order_status": "pending",
    "order_type": "dine_in",
    "created_at": datetime.now().isoformat(),
    "items": [{"item_id": "item_test", "name": "Test Item", "qty": 1, "price": 25.99}]
}

result = orders.insert_one(new_order)
print(f"Inserted order with ID: {result.inserted_id}")

# Insert multiple orders
multiple_orders = [
    {
        "_id": "order_bulk_1", 
        "customer_id": "cust_test_002", 
        "total_amount": 35.50, 
        "order_status": "pending",
        "order_type": "takeout",
        "created_at": datetime.now().isoformat(),
        "items": [{"item_id": "item_001", "name": "Burger", "qty": 1, "price": 35.50}]
    },
    {
        "_id": "order_bulk_2", 
        "customer_id": "cust_test_003", 
        "total_amount": 42.00, 
        "order_status": "completed",
        "order_type": "dine_in", 
        "created_at": datetime.now().isoformat(),
        "items": [{"item_id": "item_002", "name": "Pizza", "qty": 1, "price": 42.00}]
    }
]

result = orders.insert_many(multiple_orders)
print(f"Inserted {len(result.inserted_ids)} orders")