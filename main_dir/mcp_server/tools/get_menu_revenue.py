"""Menu items by revenue tool."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class TopMenuRevenueInput(BaseModel):
    """Strict input schema for get_top_menu_items_by_revenue."""

    model_config = ConfigDict(extra="forbid")

    limit: int = 10


@mcp.tool()
def get_top_menu_items_by_revenue(params: TopMenuRevenueInput) -> List[Dict[str, Any]]:
        """Get menu items generating highest revenue

        Args:
            limit: Number of top items to return (default: 10)
            
        Returns:
            List of menu items with revenue and order details
        """
        try:
            limit = params.limit
            db = mongo_client.db
            pipeline = [
                {"$unwind": "$items"},
                {"$group": {
                    "_id": "$items.name",
                    "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                    "total_orders": {"$sum": "$items.quantity"},
                    "avg_price": {"$avg": "$items.price"}
                }},
                {"$sort": {"total_revenue": -1}},
                {"$limit": limit}
            ]
            return list(db["orders"].aggregate(pipeline))
        except Exception as e:
            return [{"error": f"Menu revenue analysis failed: {str(e)}"}]