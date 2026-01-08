"""
Operational metrics tool
"""

from typing import Dict, Any, List
from mcp_server.utils.db_client import mongo_client
from mcp_server.mcp_instance import mcp

@mcp.tool()
def get_payment_methods_breakdown() -> List[Dict[str, Any]]:
        """Get breakdown of orders by payment method.

        Returns:
            List of payment methods with order counts and revenue totals
            
        Analyzes payment_method field in orders collection.
        """
        try:
            db = mongo_client.db
            pipeline = [
                {"$group": {
                    "_id": "$payment_mode",
                    "order_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_amount"},
                    "avg_order_value": {"$avg": "$total_amount"}
                }},
                {"$sort": {"order_count": -1}},
                {"$project": {
                    "payment_method": "$_id",
                    "order_count": 1,
                    "total_revenue": 1,
                    "avg_order_value": {"$round": ["$avg_order_value", 2]},
                    "_id": 0
                }}
            ]
            return list(db["orders"].aggregate(pipeline))
        except Exception as e:
            return [{"error": f"Payment methods breakdown failed: {str(e)}"}]