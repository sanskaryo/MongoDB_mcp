
import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB; align defaults with demo dataset
mongodb_uri = os.getenv('MONGODB_URI') or os.getenv('MONGO_URI') or 'mongodb://localhost:27017/restaurant_management'
database_name = os.getenv('MONGODB_DATABASE') or os.getenv('DB_NAME') or 'restaurant_management'
client = pymongo.MongoClient(mongodb_uri)
db = client[database_name]

orders = db.orders

print("=== MONGODB AGGREGATION PIPELINE EXPLAINED ===")
print("Think of aggregation like a factory assembly line:")
print("Data goes through multiple stages, each stage transforms it")
print("Pipeline = [Stage1, Stage2, Stage3, ...]\n")

# ===== EXAMPLE 1: Simple Grouping =====
print("1. SIMPLE GROUPING - Revenue by Order Status")
print("   Goal: Group orders by status, calculate total revenue & count")
print()

# PIPELINE EXPLANATION:
# This pipeline has 1 stage: $group
pipeline = [
    {
        "$group": {                          # STAGE 1: Group documents together
            "_id": "$order_status",          # GROUP BY: order_status field ($ means "get field value")
            "total_revenue": {"$sum": "$total_amount"},  # SUM: Add up all total_amount values in each group
            "order_count": {"$sum": 1}       # COUNT: Add 1 for each document in the group
        }
    }
]

print("   Pipeline Step-by-Step:")
print("   Stage 1 ($group):")
print("     • GROUP BY: $order_status (completed, cancelled, etc.)")
print("     • CALCULATE: total_revenue = sum of all total_amount")  
print("     • COUNT: order_count = count of documents in each group")
print()

print("   Results:")
for result in orders.aggregate(pipeline):
    status = result['_id']
    revenue = result['total_revenue']
    count = result['order_count']
    print(f"     {status}: ${revenue:.2f} ({count} orders)")

# ===== EXAMPLE 2: Multi-Stage Pipeline =====
print("\n" + "="*50)
print("2. MULTI-STAGE PIPELINE - Top Customers by Spending")
print("   Goal: Find top 5 customers who spent the most money")
print()

# PIPELINE EXPLANATION:  
# This pipeline has 3 stages: $lookup → $group → $sort → $limit
pipeline = [
    {
        "$lookup": {                         # STAGE 1: JOIN with customers collection
            "from": "customers",             # JOIN WITH: customers collection
            "localField": "customer_id",     # MATCH: orders.customer_id
            "foreignField": "_id",           # WITH: customers._id  
            "as": "customer_info"            # RESULT NAME: customer_info array
        }
    },
    {
        "$unwind": "$customer_info"          # STAGE 2: Flatten the customer_info array
    },
    {
        "$group": {                          # STAGE 3: Group by customer
            "_id": "$customer_info.name",    # GROUP BY: customer name
            "customer_id": {"$first": "$customer_id"},
            "total_spent": {"$sum": "$total_amount"}  # SUM: total amount spent by each customer
        }
    },
    {
        "$sort": {"total_spent": -1}        # STAGE 4: Sort by total_spent descending (-1 = high to low)
    },
    {
        "$limit": 5                         # STAGE 5: Take only first 5 results (top 5)
    }
]

print("   Pipeline Step-by-Step:")
print("   Stage 1 ($lookup): JOIN orders with customers collection")
print("   Stage 2 ($unwind): Flatten customer_info array") 
print("   Stage 3 ($group): Group by customer name, sum their spending")
print("   Stage 4 ($sort): Sort by total_spent (highest first)")
print("   Stage 5 ($limit): Take only top 5 customers")
print()

print("   Results:")
for result in orders.aggregate(pipeline):
    name = result['_id']
    customer_id = result['customer_id']
    spent = result['total_spent']
    print(f"     {name} ({customer_id}): ${spent:.2f}")

# ===== EXAMPLE 3: Advanced Pipeline with Filtering =====
print("\n" + "="*50)
print("3. ADVANCED PIPELINE - Monthly Revenue Analysis")
print("   Goal: Get revenue by month, but only for completed orders")
print()

pipeline = [
    {
        "$match": {"order_status": "completed"}  # STAGE 1: FILTER - only completed orders
    },
    {
        "$addFields": {                          # STAGE 2: ADD NEW FIELD
            "month": {"$substr": ["$created_at", 0, 7]}  # Extract YYYY-MM from date string
        }
    },
    {
        "$group": {                              # STAGE 3: GROUP BY month
            "_id": "$month",                     # GROUP BY: the month we just created
            "monthly_revenue": {"$sum": "$total_amount"},
            "orders_count": {"$sum": 1}
        }
    },
    {
        "$sort": {"_id": 1}                     # STAGE 4: Sort by month (1 = ascending, oldest first)
    }
]

print("   Pipeline Step-by-Step:")
print("   Stage 1 ($match): FILTER to only completed orders")
print("   Stage 2 ($addFields): CREATE month field from created_at date")
print("   Stage 3 ($group): GROUP BY month, sum revenue")
print("   Stage 4 ($sort): Sort by month chronologically")
print()

print("   Results:")
for result in orders.aggregate(pipeline):
    month = result['_id']
    revenue = result['monthly_revenue']
    count = result['orders_count']
    print(f"     {month}: ${revenue:.2f} ({count} orders)")

print("\n" + "="*50)
print("KEY AGGREGATION CONCEPTS:")
print("• PIPELINE = Array of stages [stage1, stage2, stage3...]")
print("• Each stage transforms data and passes it to the next stage")
print("• $ = Field reference (get value from document field)")
print("• $group = Combine documents together")
print("• $match = Filter documents (like WHERE in SQL)")
print("• $sort = Order results (1=ascending, -1=descending)")
print("• $limit = Take only N results") 
print("• $lookup = JOIN with another collection")
print("• $sum = Add up values")
print("• $avg = Calculate average")
print("• $count = Count documents")
print("• $addFields = Create new calculated fields")