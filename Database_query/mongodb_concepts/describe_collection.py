# Describe Collection - Analyze collection structure

import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
mongodb_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/hotel_management')
client = pymongo.MongoClient(mongodb_uri)
db = client['hotel_management']

# Get orders collection
orders = db.orders

# Get sample document
sample = orders.find_one()
if sample:
    print("Sample document fields:")
    for field in sample.keys():
        print(f"  - {field}: {type(sample[field]).__name__}")
    
    # Count documents
    count = orders.count_documents({})
    print(f"\nTotal documents: {count}")
else:
    print("Collection is empty")