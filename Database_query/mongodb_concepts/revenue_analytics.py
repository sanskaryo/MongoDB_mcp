# Revenue Analytics - Business insights

import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
mongodb_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/hotel_management')
client = pymongo.MongoClient(mongodb_uri)
db = client['hotel_management']

orders = db.orders

# Total revenue
pipeline = [
    {"$match": {"status": "completed"}},
    {"$group": {
        "_id": None,
        "total_revenue": {"$sum": "$total_amount"},
        "total_orders": {"$sum": 1},
        "avg_order": {"$avg": "$total_amount"}
    }}
]

result = list(orders.aggregate(pipeline))
if result:
    data = result[0]
    print(f"Total Revenue: ${data['total_revenue']:.2f}")
    print(f"Total Orders: {data['total_orders']}")
    print(f"Average Order: ${data['avg_order']:.2f}")

# Daily revenue (fixed field names)
pipeline = [
    {"$match": {"order_status": "completed"}},
    {"$addFields": {
        "order_date": {"$substr": ["$created_at", 0, 10]}  # Extract YYYY-MM-DD
    }},
    {"$group": {
        "_id": "$order_date",
        "daily_revenue": {"$sum": "$total_amount"}
    }},
    {"$sort": {"_id": -1}},
    {"$limit": 7}
]

print("\nLast 7 days revenue:")
for day in orders.aggregate(pipeline):
    print(f"  {day['_id']}: ${day['daily_revenue']:.2f}")