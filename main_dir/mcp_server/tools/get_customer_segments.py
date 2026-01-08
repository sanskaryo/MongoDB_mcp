"""
Customer segments analytics tool
"""

from typing import Dict, Any, List
from mcp_server.utils.db_client import mongo_client
from mcp_server.mcp_instance import mcp

@mcp.tool()
def get_customer_segments() -> List[Dict[str, Any]]:
        """Analyze customer segments with spending statistics.

        Returns:
            List of customer segments with counts and spending metrics
            
        Groups customers by segment field and calculates aggregated spending statistics.
        """
        try:
            db = mongo_client.db
            pipeline = [
                {"$group": {
                    "_id": "$segment",
                    "customer_count": {"$sum": 1},
                    "total_spending": {"$sum": "$total_spent"},
                    "avg_spending": {"$avg": "$total_spent"},
                    "max_spending": {"$max": "$total_spent"},
                    "min_spending": {"$min": "$total_spent"},
                    "avg_loyalty_points": {"$avg": "$loyalty_points"}
                }},
                {"$sort": {"total_spending": -1}}
            ]
            return list(db["customers"].aggregate(pipeline))
        except Exception as e:
            return [{"error": f"Customer segments analysis failed: {str(e)}"}]