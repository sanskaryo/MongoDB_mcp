"""
Order status breakdown tool
"""

from typing import Dict, Any, List
from mcp_server.utils.db_client import mongo_client
from mcp_server.mcp_instance import mcp

@mcp.tool()
def get_orders_by_status() -> List[Dict[str, Any]]:
        """Get breakdown of orders by status

        Returns:
            List of order statuses with counts and revenue totals
        """
        try:
            db = mongo_client.db
            pipeline = [
                {"$group": {
                    "_id": "$order_status",
                    "order_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_amount"},
                    "avg_order_value": {"$avg": "$total_amount"}
                }},
                {"$sort": {"order_count": -1}},
                {"$project": {
                    "status": "$_id",
                    "order_count": 1,
                    "total_revenue": 1,
                    "avg_order_value": {"$round": ["$avg_order_value", 2]},
                    "_id": 0
                }}
            ]
            return list(db["orders"].aggregate(pipeline))
        except Exception as e:
            return [{"error": f"Order status breakdown failed: {str(e)}"}]