"""Menu performance tool."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class TopMenuItemsInput(BaseModel):
    """Strict input schema for get_top_menu_items_by_orders."""

    model_config = ConfigDict(extra="forbid")

    limit: int = 10


@mcp.tool()
def get_top_menu_items_by_orders(params: TopMenuItemsInput) -> List[Dict[str, Any]]:
        """Get most frequently ordered menu items

        Args:
            limit: Number of top items to return (default: 10)
            
        Returns:
            List of menu items with order frequency and revenue
        """
        try:
            limit = params.limit
            db = mongo_client.db
            pipeline = [
                {"$unwind": "$items"},
                {"$group": {
                    "_id": "$items.name",
                    "total_orders": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}},
                    "avg_price": {"$avg": "$items.price"}
                }},
                {"$sort": {"total_orders": -1}},
                {"$limit": limit}
            ]
            return list(db["orders"].aggregate(pipeline))
        except Exception as e:
            return [{"error": f"Menu performance analysis failed: {str(e)}"}]