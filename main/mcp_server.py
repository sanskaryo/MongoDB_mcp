from fastmcp import FastMCP
import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime, timedelta

# Initialize FastMCP
mcp = FastMCP("MongoDB Analytics")

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
client = pymongo.MongoClient(MONGO_URI)
db = client["restaurant_analytics"]

@mcp.tool()
def get_daily_revenue(days: int = 7) -> str:
    """Get daily revenue for the last N days."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    pipeline = [
        {"$match": {"timestamp": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "revenue": {"$sum": "$total"}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    results = list(db.orders.aggregate(pipeline))
    if not results:
        return "No revenue data found for the specified period."
    
    df = pd.DataFrame(results)
    df.columns = ["Date", "Revenue"]
    
    return df.to_markdown(index=False)

@mcp.tool()
def get_top_selling_items(limit: int = 5) -> str:
    """Get the top selling menu items."""
    pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.name",
            "total_quantity": {"$sum": "$items.quantity"}
        }},
        {"$sort": {"total_quantity": -1}},
        {"$limit": limit}
    ]
    
    results = list(db.orders.aggregate(pipeline))
    if not results:
        return "No sales data found."
    
    df = pd.DataFrame(results)
    df.columns = ["Item", "Quantity Sold"]
    
    return df.to_markdown(index=False)

@mcp.tool()
def get_inventory_alerts() -> str:
    """Get items that are below reorder level."""
    low_stock = list(db.inventory.find({"$expr": {"$lte": ["$quantity", "$reorder_level"]}}))
    
    if not low_stock:
        return "All inventory levels are healthy."
    
    df = pd.DataFrame(low_stock)
    return df[["item", "quantity", "reorder_level", "unit"]].to_markdown(index=False)

if __name__ == "__main__":
    mcp.run()
