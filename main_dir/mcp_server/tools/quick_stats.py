"""Quick statistics tool for MongoDB collections."""

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class CollectionSummaryInput(BaseModel):
    """Strict input schema for get_collection_summary."""

    model_config = ConfigDict(extra="forbid")

    collection: str


@mcp.tool()
def get_collection_summary(params: CollectionSummaryInput) -> Dict[str, Any]:
        """Get summary statistics for any collection.

        Args:
            collection: Collection name (orders, customers, menu_items, users, delivery_details, audit_logs)
            
        Returns:
            Dict with collection-specific summary statistics
            
        Provides different metrics based on collection type:
            orders: total count, revenue totals, average order value
            customers: customer count, segment breakdown, spending averages
            menu_items: item count, price ranges, category distribution
            
        WORKFLOW:
            For custom statistics, first use:
            1. mongodb_get_collections() - to see available collections
            2. mongodb_describe_collection() - to understand field names and structure
        """
        try:
            collection = params.collection
            db = mongo_client.db
            if collection == "orders":
                pipeline = [
                    {"$group": {
                        "_id": None,
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": "$total_amount"},
                        "avg_order_value": {"$avg": "$total_amount"},
                        "min_order_value": {"$min": "$total_amount"},
                        "max_order_value": {"$max": "$total_amount"}
                    }}
                ]
            elif collection == "customers":
                pipeline = [
                    {"$group": {
                        "_id": None,
                        "total_customers": {"$sum": 1},
                        "avg_spent": {"$avg": "$total_spent"},
                        "max_spent": {"$max": "$total_spent"},
                        "min_spent": {"$min": "$total_spent"},
                        "avg_loyalty_points": {"$avg": "$loyalty_points"}
                    }}
                ]
            elif collection == "menu_items":
                pipeline = [
                    {"$group": {
                        "_id": None,
                        "total_items": {"$sum": 1},
                        "avg_price": {"$avg": "$price"},
                        "max_price": {"$max": "$price"},
                        "min_price": {"$min": "$price"}
                    }}
                ]
            else:
                # Generic count for any collection
                count = db[collection].count_documents({})
                return {"collection": collection, "total_documents": count}
            
            results = list(db[collection].aggregate(pipeline))
            if results:
                stats = results[0]
                stats["collection"] = collection
                del stats["_id"]
                return stats
            else:
                return {
                    "collection": collection,
                    "total_documents": 0,
                    "message": "No data found"
                }
            
        except Exception as e:
            return {"error": f"Collection summary failed: {str(e)}"}