"""MongoDB collections listing tool for database exploration."""

from typing import Dict, Any, List
from mcp_server.utils.db_client import mongo_client
from mcp_server.mcp_instance import mcp

@mcp.tool()
def mongodb_get_collections() -> Dict[str, Any]:
    """List all available collections with basic metadata.

    Returns:
        Dict with collection names, document counts, and basic info
        
    Use this to discover available collections, then use mongodb_describe_collection() 
    to get detailed schema for specific collections before querying.
    """
    try:
        db = mongo_client.db
        collections = []
        for collection_name in db.list_collection_names():
            try:
                count = db[collection_name].count_documents({})
                collections.append({
                    "name": collection_name,
                    "document_count": count
                })
            except Exception as count_error:
                collections.append({
                    "name": collection_name,
                    "document_count": -1,
                    "error": f"Count failed: {str(count_error)}"
                })
                
        return {
            "success": True,
            "collections": collections,
            "total_collections": len(collections)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get collections: {str(e)}"
        }