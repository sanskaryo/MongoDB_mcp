"""MongoDB update tool for modifying documents in collections."""

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class MongoDBUpdateInput(BaseModel):
    """Strict input schema for mongodb_update."""

    model_config = ConfigDict(extra="forbid")

    collection: str
    filter_criteria: Dict[str, Any] = Field(default_factory=dict)
    update_data: Dict[str, Any] = Field(default_factory=dict)
    upsert: bool = False


@mcp.tool()
def mongodb_update(params: MongoDBUpdateInput) -> Dict[str, Any]:
        """Update documents in a MongoDB collection.

        Args:
            collection: Collection name (orders, customers, menu_items, users, audit_logs, delivery_details)
            filter_criteria: Query dict to find documents to update
            update_data: Update operations dict using MongoDB update operators
            upsert: Create document if not found (default: False)
            
        Returns:
            Dict with success status, modified count, and upserted ID if applicable
            
        IMPORTANT: Before updating, always use:
            1. mongodb_get_collections() - to see available collections
            2. mongodb_describe_collection() - to understand field names and structure
            
        Update Patterns:
            Set fields: {"$set": {"status": "completed", "total": 150}}
            Increment: {"$inc": {"loyalty_points": 10}}
            Add to array: {"$push": {"items": {"name": "Pizza"}}}
            
        Use MongoDB update operators ($set, $inc, $push, $pull, $unset).
        Always structure filter_criteria as a valid MongoDB query dictionary.
        """
        try:
            collection = params.collection
            filter_criteria = params.filter_criteria
            update_data = params.update_data
            upsert = params.upsert

            if not collection or not isinstance(collection, str):
                return {"success": False, "error": "Collection name must be a non-empty string"}
                
            if not isinstance(filter_criteria, dict):
                return {"success": False, "error": "Filter criteria must be a dictionary"}
                
            if not isinstance(update_data, dict) or not update_data:
                return {"success": False, "error": "Update data must be a non-empty dictionary"}
                
            if not isinstance(upsert, bool):
                return {"success": False, "error": "Upsert must be a boolean value"}
            
            db = mongo_client.db
            result = db[collection].update_many(filter_criteria, update_data, upsert=upsert)
            
            return {
                "success": True,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Update operation failed: {str(e)}"
            }