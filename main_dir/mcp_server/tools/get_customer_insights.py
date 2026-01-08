"""Customer insights tool."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class TopCustomersInput(BaseModel):
    """Strict input schema for get_top_customers_by_spending."""

    model_config = ConfigDict(extra="forbid")

    limit: int = 10


@mcp.tool()
def get_top_customers_by_spending(params: TopCustomersInput) -> List[Dict[str, Any]]:
        """Get top customers ranked by total spending.

        Args:
            limit: Number of top customers to return (default: 10)
            
        Returns:
            List of customers with spending details and customer information
            
        Provides customer rankings based on total_spent field.
        
        WORKFLOW:
            For custom customer analysis, first use:
            1. mongodb_get_collections() - to see available collections
            2. mongodb_describe_collection() - to understand field names and structure
        """
        try:
            limit = params.limit
            db = mongo_client.db
            pipeline = [
                {"$sort": {"total_spent": -1}},
                {"$limit": limit},
                {"$project": {
                    "customer_id": 1,
                    "name": 1,
                    "segment": 1,
                    "total_spent": 1,
                    "loyalty_points": 1,
                    "email": 1
                }}
            ]
            return list(db["customers"].aggregate(pipeline))
        except Exception as e:
            return [{"error": f"Customer insights failed: {str(e)}"}]