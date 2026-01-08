"""MongoDB aggregation tool for complex data analysis."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class MongoDBAggregateInput(BaseModel):
    """Strict input schema for mongodb_aggregate."""

    model_config = ConfigDict(extra="forbid")

    collection: str
    pipeline: List[Dict[str, Any]]


@mcp.tool()
def mongodb_aggregate(params: MongoDBAggregateInput) -> Dict[str, Any]:
        """Execute MongoDB aggregation pipeline for advanced data analysis.

        Args:
            collection: Collection name (orders, customers, menu_items, users, audit_logs, delivery_details)
            pipeline: List of aggregation stage dictionaries
            
        Returns:
            Dict with success status and aggregated results
            
        Core Patterns:
            Group by field: [{"$group": {"_id": "$field", "count": {"$sum": 1}}}]
            Sort results: [{"$sort": {"field": -1}}]
            Filter first: [{"$match": {"field": "value"}}, {"$group": {...}}]
            Calculate totals: [{"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
            
        Common Stages:
            $match: Filter documents
            $group: Group and calculate  
            $sort: Order results (1=asc, -1=desc)
            $limit: Limit results
            $unwind: Split arrays
            
        WORKFLOW:
            1. ALWAYS use mongodb_get_collections() first to see available collections
            2. ALWAYS use mongodb_describe_collection() to discover field names and structure
            3. Then build aggregation pipeline using actual field names from schema
            
        Revenue Example: [{"$group": {"_id": "$order_date", "revenue": {"$sum": "$total_amount"}}}]
        """
        try:
            collection = params.collection
            pipeline = params.pipeline

            if not collection or not isinstance(collection, str):
                return {"success": False, "error": "Collection name must be a non-empty string"}
                
            if not isinstance(pipeline, list) or not pipeline:
                return {"success": False, "error": "Pipeline must be a non-empty list of stages"}
                
            for i, stage in enumerate(pipeline):
                if not isinstance(stage, dict):
                    return {"success": False, "error": f"Pipeline stage {i} must be a dictionary"}
            
            db = mongo_client.db
            cursor = db[collection].aggregate(pipeline)
            results = []
            for doc in cursor:
                # Convert ObjectId to string if present
                if '_id' in doc and hasattr(doc['_id'], '__str__'):
                    doc['_id'] = str(doc['_id'])
                results.append(doc)
                
            return {
                "success": True,
                "data": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Aggregation operation failed: {str(e)}"
            }