"""Revenue by date range tool."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class RevenueByDateInput(BaseModel):
    """Strict input schema for get_revenue_by_date_range."""

    model_config = ConfigDict(extra="forbid")

    start_date: str
    end_date: str


@mcp.tool()
def get_revenue_by_date_range(params: RevenueByDateInput) -> Dict[str, Any]:
        """Get total revenue and statistics for a specific date range

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Revenue totals and statistics for the date range
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
                    "_id": None,
                    "total_revenue": {"$sum": "$total_amount"},
                    "total_orders": {"$sum": 1},
                    "avg_order_value": {"$avg": "$total_amount"},
                    "min_order_value": {"$min": "$total_amount"},
                    "max_order_value": {"$max": "$total_amount"}
                }}
            ]
            results = list(db["orders"].aggregate(pipeline))
            if results:
                result = results[0]
                result["start_date"] = start_date
                result["end_date"] = end_date
                del result["_id"]
                return result
            else:
                # Check what dates actually exist in database
                sample = db["orders"].find_one({}, {"created_at": 1})
                sample_date = sample.get('created_at') if sample else 'No orders found'
                return {
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_revenue": 0,
                    "total_orders": 0,
                    "message": f"No orders found in date range. Sample date in DB: {sample_date}",
                    "suggestion": "Try using date range 2024-09-01 to 2024-09-30 based on sample data"
                }
        except Exception as e:
            return {"error": f"Revenue by date range failed: {str(e)}"}