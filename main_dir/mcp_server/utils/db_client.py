"""
MongoDB Database Client
Handles MongoDB connections and basic operations
"""

import os
from typing import Optional, Dict, Any, List, Union
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()


class MongoDBClient:
    """MongoDB client wrapper for hotel analytics"""
    
    def __init__(self):
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self.db_name = os.getenv('MONGODB_DATABASE', os.getenv('DB_NAME', 'hotel_management'))
        
    def connect(self) -> bool:
        """Establish MongoDB connection"""
        try:
            mongo_uri = os.getenv('MONGODB_URI', os.getenv('MONGO_URI'))
            if not mongo_uri:
                raise ValueError("MONGODB_URI not found in environment variables")
            
            self._client = MongoClient(mongo_uri)
            # Test connection
            self._client.admin.command('ping')
            self._db = self._client[self.db_name]
            return True
            
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
    
    @property
    def db(self) -> Database:
        """Get database instance"""
        if self._db is None:
            if not self.connect():
                raise ConnectionError("Failed to connect to MongoDB")
        return self._db
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get collection instance"""
        return self.db[collection_name]
    
    def list_collections(self) -> List[str]:
        """Get list of all collections"""
        return self.db.list_collection_names()
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            stats = self.db.command('collStats', collection_name)
            collection = self.get_collection(collection_name)
            
            return {
                'name': collection_name,
                'count': collection.count_documents({}),
                'size_bytes': stats.get('size', 0),
                'avg_obj_size': stats.get('avgObjSize', 0),
                'indexes': len(list(collection.list_indexes())),
                'storage_size': stats.get('storageSize', 0)
            }
        except Exception as e:
            return {
                'name': collection_name,
                'error': str(e),
                'count': 0
            }
    
    def execute_query(self, collection_name: str, query: Dict[str, Any], 
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Execute a find query"""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query)
            
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except Exception as e:
            raise Exception(f"Query execution failed: {e}")
    
    def execute_aggregation(self, collection_name: str, 
                          pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute an aggregation pipeline"""
        try:
            collection = self.get_collection(collection_name)
            return list(collection.aggregate(pipeline))
        except Exception as e:
            raise Exception(f"Aggregation execution failed: {e}")
    
    def execute_insert(self, collection_name: str, 
                      document: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Execute insert operation - single document or batch"""
        try:
            collection = self.get_collection(collection_name)
            
            if isinstance(document, list):
                # Batch insert
                result = collection.insert_many(document)
                return {
                    "inserted_ids": [str(id) for id in result.inserted_ids],
                    "inserted_count": len(result.inserted_ids)
                }
            else:
                # Single insert
                result = collection.insert_one(document)
                return {
                    "inserted_id": str(result.inserted_id),
                    "inserted_count": 1
                }
        except Exception as e:
            raise Exception(f"Insert operation failed: {e}")
    
    def execute_update(self, collection_name: str, 
                      filter_criteria: Dict[str, Any], 
                      update_data: Dict[str, Any], 
                      upsert: bool = False) -> Dict[str, Any]:
        """Execute update operation with flexible update operators"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_many(filter_criteria, update_data, upsert=upsert)
            
            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }
        except Exception as e:
            raise Exception(f"Update operation failed: {e}")
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """Get list of collections with metadata"""
        try:
            collections = []
            for name in self.list_collections():
                stats = self.get_collection_stats(name)
                collections.append(stats)
            return collections
        except Exception as e:
            raise Exception(f"Failed to get collections: {e}")
    
    def describe_collection(self, collection_name: str, sample_size: int = 5) -> Dict[str, Any]:
        """Get collection schema analysis and sample documents"""
        try:
            collection = self.get_collection(collection_name)
            
            # Get sample documents
            samples = list(collection.find().limit(sample_size))
            
            # Get collection stats
            stats = self.get_collection_stats(collection_name)
            
            # Analyze schema from samples
            schema = {}
            if samples:
                for doc in samples:
                    for key, value in doc.items():
                        if key not in schema:
                            schema[key] = set()
                        schema[key].add(type(value).__name__)
                
                # Convert sets to lists for JSON serialization
                schema = {k: list(v) for k, v in schema.items()}
            
            return {
                "collection": collection_name,
                "stats": stats,
                "schema": schema,
                "sample_documents": samples
            }
        except Exception as e:
            raise Exception(f"Collection describe failed: {e}")


# Global client instance
mongo_client = MongoDBClient()