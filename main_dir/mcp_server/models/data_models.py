"""
Data models and schemas for MongoDB Hotel Analytics
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for database queries"""
    collection: str = Field(..., description="Collection name to query")
    query: Dict[str, Any] = Field(default_factory=dict, description="MongoDB query filter")
    limit: Optional[int] = Field(None, description="Maximum number of documents to return")
    projection: Optional[Dict[str, int]] = Field(None, description="Fields to include/exclude")


class AggregationRequest(BaseModel):
    """Request model for aggregation pipelines"""
    collection: str = Field(..., description="Collection name to aggregate")
    pipeline: List[Dict[str, Any]] = Field(..., description="MongoDB aggregation pipeline")


class InsertRequest(BaseModel):
    """Request model for document insertion"""
    collection: str = Field(..., description="Collection name")
    document: Dict[str, Any] = Field(..., description="Document to insert")


class UpdateRequest(BaseModel):
    """Request model for document updates"""
    collection: str = Field(..., description="Collection name")
    filter_query: Dict[str, Any] = Field(..., description="Filter to match documents")
    update_data: Dict[str, Any] = Field(..., description="Data to update")


class DeleteRequest(BaseModel):
    """Request model for document deletion"""
    collection: str = Field(..., description="Collection name")
    filter_query: Dict[str, Any] = Field(..., description="Filter to match documents for deletion")


class CollectionInfo(BaseModel):
    """Collection information response"""
    name: str
    count: int
    size_bytes: int
    avg_obj_size: float
    indexes: int
    storage_size: int


class QueryResult(BaseModel):
    """Generic query result response"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    count: Optional[int] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class DatabaseInfo(BaseModel):
    """Database overview information"""
    database_name: str
    collections: List[CollectionInfo]
    total_documents: int
    total_size_bytes: int


class SampleData(BaseModel):
    """Sample documents from a collection"""
    collection: str
    sample_size: int
    documents: List[Dict[str, Any]]
    schema_fields: List[str]