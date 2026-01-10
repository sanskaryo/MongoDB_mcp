"""
Utility modules for MongoDB Hotel Analytics MCP Server
"""

from .db_client import mongo_client, MongoDBClient

__all__ = ['mongo_client', 'MongoDBClient']