"""
Order types analysis tool
"""

from typing import Dict, Any, List
from mcp_server.utils.db_client import mongo_client
from mcp_server.mcp_instance import mcp

@mcp.tool()
def get_orders_by_type() -> List[Dict[str, Any]]:
        """Get breakdown of orders by type (dine-in, delivery, etc.)

        Returns:
            List of order types with counts, revenue and averages
        """
        try:
            db = mongo_client.db
            pipeline = [
                {"$group": {
                    "_id": "$order_type",
                    "order_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_amount"},
                    "avg_order_value": {"$avg": "$total_amount"},
                    "min_order_value": {"$min": "$total_amount"},
                    "max_order_value": {"$max": "$total_amount"}
                }},
                {"$sort": {"total_revenue": -1}},
                {"$project": {
                    "order_type": "$_id",
                    "order_count": 1,
                    "total_revenue": 1,
                    "avg_order_value": {"$round": ["$avg_order_value", 2]},
                    "min_order_value": 1,
                    "max_order_value": 1,
                    "_id": 0
                }}
            ]
            return list(db["orders"].aggregate(pipeline))
        except Exception as e:
            return [{"error": f"Order types breakdown failed: {str(e)}"}]