"""MongoDB insert tool for adding documents to collections."""

from typing import Any, Dict, List, Union

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class MongoDBInsertInput(BaseModel):
    """Strict input schema for mongodb_insert."""

    model_config = ConfigDict(extra="forbid")

    collection: str
    document: Union[Dict[str, Any], List[Dict[str, Any]]]


@mcp.tool()
def mongodb_insert(params: MongoDBInsertInput) -> Dict[str, Any]:
        """Insert one or multiple documents into a MongoDB collection.

        Args:
            collection: Collection name (orders, customers, menu_items, users, audit_logs, delivery_details)
            document: Single document dict or list of document dicts to insert
            
        Returns:
            Dict with success status, inserted IDs, and count
            
        Document Format:
            Single: {"field": "value", "number": 123}
            Multiple: [{"field1": "value1"}, {"field2": "value2"}]
            
        Always pass valid document dictionaries with proper field names and types.
        """
        try:
            collection = params.collection
            document = params.document

            db = mongo_client.db
            if isinstance(document, list):
                if not document:
                    return {"error": "Document list cannot be empty"}
                    
                result = db[collection].insert_many(document)
                return {
                    "success": True,
                    "inserted_count": len(result.inserted_ids),
                    "inserted_ids": [str(obj_id) for obj_id in result.inserted_ids]
                }
            else:
                if not document:
                    return {"error": "Document cannot be empty"}
                    
                result = db[collection].insert_one(document)
                return {
                    "success": True,
                    "inserted_count": 1,
                    "inserted_id": str(result.inserted_id)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Insert operation failed: {str(e)}"
            }