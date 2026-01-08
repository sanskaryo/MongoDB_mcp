"""MongoDB collection description tool for schema analysis."""

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict

from mcp_server.mcp_instance import mcp
from mcp_server.utils.db_client import mongo_client


class MongoDBDescribeInput(BaseModel):
    """Strict input schema for mongodb_describe_collection."""

    model_config = ConfigDict(extra="forbid")

    collection: str
    sample_size: int = 5


@mcp.tool()
def mongodb_describe_collection(params: MongoDBDescribeInput) -> Dict[str, Any]:
    """Analyze collection schema and discover actual field names and types.

    Args:
        collection: Collection name to analyze (orders, customers, menu_items, etc.)
        sample_size: Number of sample documents to return (default: 5)
        
    Returns:
        Dict with field names, types, sample values, and example documents
        
    CRITICAL: Always use this tool first to discover exact field names before querying.
    This prevents field name errors and ensures accurate queries.
    """
    try:
        collection = params.collection
        sample_size = params.sample_size

        if not collection or not isinstance(collection, str):
            return {"success": False, "error": "Collection name must be a non-empty string"}
            
        if not isinstance(sample_size, int) or sample_size <= 0:
            return {"success": False, "error": "Sample size must be a positive integer"}
        
        db = mongo_client.db
        # Get sample documents
        cursor = db[collection].find().limit(sample_size)
        samples = []
        for doc in cursor:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            samples.append(doc)
        
        # Get collection stats
        count = db[collection].count_documents({})
        
        # Extract field names and types from samples
        fields = {}
        for doc in samples:
            for key, value in doc.items():
                field_type = type(value).__name__
                if key not in fields:
                    fields[key] = {"type": field_type, "count": 1}
                else:
                    fields[key]["count"] += 1
                    if fields[key]["type"] != field_type:
                        fields[key]["type"] = "mixed"
        
        return {
            "success": True,
            "collection": collection,
            "document_count": count,
            "sample_size": len(samples),
            "fields": fields,
            "sample_documents": samples
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to describe collection: {str(e)}"
        }