"""MongoDB query tool for finding documents in collections."""

from typing import Any, Dict, List, Union
import json

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


@mcp.tool()
def mongodb_query(collection: str, query: Union[Dict[str, Any], str] = "{}", limit: int = 10) -> Dict[str, Any]:
    """Execute a MongoDB query.
    
    Args:
        collection: The name of the collection to query.
        query: The query filter as a dictionary or JSON string. Defaults to empty dict.
        limit: The maximum number of documents to return. Maximum 500.
    """
    try:
        # Parse query if it's a string
        if isinstance(query, str):
            try:
                # Handle case where query might be empty string
                if not query.strip():
                    query = {}
                else:
                    query = json.loads(query)
            except json.JSONDecodeError:
                # If JSON parsing fails, assume it's an invalid format for this tool
                return {"success": False, "error": "Invalid JSON format for query string"}

        # Validation logic must be indented to stay within the main 'try' block
        if not collection or not isinstance(collection, str):
            return {"success": False, "error": "Collection name must be a non-empty string"}
            
        if query is None:
            query = {}
        elif not isinstance(query, dict):
            return {"success": False, "error": "Query must be a dictionary"}
            
        if not isinstance(limit, int) or limit <= 0:
            return {"success": False, "error": "Limit must be a positive integer"}
            
        db = mongo_client.db
        cursor = db[collection].find(query).limit(limit)
        results = []
        for doc in cursor:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            results.append(doc)
            
        return {
            "success": True,
            "data": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Query operation failed: {str(e)}"
        }