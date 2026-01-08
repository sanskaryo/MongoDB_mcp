"""Data range detection tool for MCP server."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class DataRangeInput(BaseModel):
    """Strict input schema for get_data_date_range."""

    model_config = ConfigDict(extra="forbid")

    collection: str = "orders"


@mcp.tool()
def get_data_date_range(params: DataRangeInput) -> Dict[str, Any]:
        """Get the actual date range of data available in the database
        
        Args:
            collection: Collection name to check (default: orders)
            
        Returns:
            Dictionary with min_date, max_date, total_records, and sample_dates
        """
        try:
            collection = params.collection
            db = mongo_client.db
            # Get min and max dates from the collection
            pipeline = [
                {"$group": {
                    "_id": None,
                    "min_date": {"$min": "$created_at"},
                    "max_date": {"$max": "$created_at"},
                    "total_records": {"$sum": 1}
                }}
            ]
            
            result = list(db[collection].aggregate(pipeline))
            
            if not result:
                return {
                    "error": f"No data found in {collection} collection",
                    "min_date": None,
                    "max_date": None,
                    "total_records": 0,
                    "sample_dates": []
                }
            
            data = result[0]
            
            # Get some sample dates to show distribution
            sample_pipeline = [
                {"$sample": {"size": 10}},
                {"$project": {"created_at": 1, "_id": 0}},
                {"$sort": {"created_at": 1}}
            ]
            
            samples = list(db[collection].aggregate(sample_pipeline))
            sample_dates = [doc["created_at"] for doc in samples if "created_at" in doc]
            
            # Parse dates to extract useful information
            min_date = data["min_date"]
            max_date = data["max_date"]
            
            # Convert to readable format if they're strings
            if isinstance(min_date, str):
                min_dt = datetime.fromisoformat(min_date.replace('Z', '+00:00'))
                min_date_str = min_dt.strftime("%Y-%m-%d")
            else:
                min_date_str = min_date.strftime("%Y-%m-%d") if min_date else None
                
            if isinstance(max_date, str):
                max_dt = datetime.fromisoformat(max_date.replace('Z', '+00:00'))
                max_date_str = max_dt.strftime("%Y-%m-%d")
            else:
                max_date_str = max_date.strftime("%Y-%m-%d") if max_date else None
            
            return {
                "collection": collection,
                "min_date": min_date_str,
                "max_date": max_date_str,
                "min_date_full": str(min_date),
                "max_date_full": str(max_date),
                "total_records": data["total_records"],
                "sample_dates": [str(date) for date in sample_dates[:5]],
                "summary": f"Data available from {min_date_str} to {max_date_str} ({data['total_records']} records)"
            }
            
        except Exception as e:
            return {
                "error": f"Error checking date range: {str(e)}",
                "collection": collection,
                "min_date": None,
                "max_date": None,
                "total_records": 0,
                "sample_dates": []
            }