"""
Data models for MongoDB Hotel Analytics MCP Server
"""

from .data_models import (
    QueryRequest, AggregationRequest, InsertRequest, UpdateRequest, DeleteRequest,
    CollectionInfo, QueryResult, DatabaseInfo, SampleData
)

__all__ = [
    'QueryRequest', 'AggregationRequest', 'InsertRequest', 'UpdateRequest', 'DeleteRequest',
    'CollectionInfo', 'QueryResult', 'DatabaseInfo', 'SampleData'
]