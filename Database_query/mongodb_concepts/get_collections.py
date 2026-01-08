# Get Collections - List all collections in database

import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
mongodb_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/hotel_management')
client = pymongo.MongoClient(mongodb_uri)
db = client['hotel_management']

# List all collections
collections = db.list_collection_names()
print("Collections found:")
for collection in collections:
    print(f"  - {collection}")

print(f"\nTotal: {len(collections)} collections")