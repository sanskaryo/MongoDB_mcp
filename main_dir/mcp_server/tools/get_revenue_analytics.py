"""Revenue analytics tool."""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class DailyRevenueInput(BaseModel):
    """Strict input schema for get_daily_revenue."""

    model_config = ConfigDict(extra="forbid")

    start_date: str
    end_date: str


@mcp.tool()
def get_daily_revenue(params: DailyRevenueInput) -> List[Dict[str, Any]]:
        """Get daily revenue breakdown for a specific date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of daily revenue records with totals and order counts
            
        Date Format: "2024-01-15"
        
        WORKFLOW:
            For custom revenue analysis, first use:
            1. mongodb_get_collections() - to see available collections
            2. mongodb_describe_collection() - to understand field names and structure
        """
        try:
            start_date = params.start_date
            end_date = params.end_date

            db = mongo_client.db
            # Parse dates and convert to match database format
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            
            pipeline = [
                {"$match": {
                    "created_at": {
                        "$gte": start_dt.strftime("%Y-%m-%dT00:00:00Z"),
                        "$lte": end_dt.strftime("%Y-%m-%dT23:59:59Z")
                    }
                }},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": {"$dateFromString": {"dateString": "$created_at"}}}},
                    "total_revenue": {"$sum": "$total_amount"},
                    "order_count": {"$sum": 1},
                    "avg_order_value": {"$avg": "$total_amount"}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            results = list(db["orders"].aggregate(pipeline))
            
            if not results:
                # If no results, check what dates actually exist
                sample = db["orders"].find_one({}, {"created_at": 1})
                if sample:
                    return {"error": f"No orders found between {start_date} and {end_date}. Sample date in DB: {sample.get('created_at', 'No date found')}"}
                else:
                    return {"error": "No orders found in database"}
            
            return results
        except Exception as e:
            return {"error": f"Revenue analytics failed: {str(e)}"}