
import asyncio
import logging
import os
import sys

if sys.platform == "win32":  # Ensure Windows subprocesses inherit selector loop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastmcp import FastMCP

import matplotlib
matplotlib.use('Agg')

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from mcp_server.utils.db_client import mongo_client
from mcp_server.mcp_instance import mcp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all tools (this will register them automatically)
from mcp_server.tools import mongodb_query
from mcp_server.tools import mongodb_aggregate
from mcp_server.tools import mongodb_insert
from mcp_server.tools import mongodb_update
from mcp_server.tools import mongodb_get_collections
from mcp_server.tools import mongodb_describe_collection
from mcp_server.tools import get_revenue_analytics
from mcp_server.tools import get_customer_insights
from mcp_server.tools import get_customer_segments
from mcp_server.tools import get_menu_performance
from mcp_server.tools import get_menu_revenue
from mcp_server.tools import get_operational_metrics
from mcp_server.tools import get_order_status
from mcp_server.tools import get_order_types
from mcp_server.tools import get_revenue_by_date
from mcp_server.tools import search_orders
from mcp_server.tools import quick_stats
from mcp_server.tools import generate_chart
from mcp_server.tools import get_data_range

def setup_server():
    """Setup and configure the MCP server"""
    
    if not mongo_client.connect():
        logger.error("Failed to connect to MongoDB on startup")
        raise ConnectionError("MongoDB connection failed")
    
    logger.info(f"Connected to MongoDB database: {mongo_client.db_name}")
    
    logger.info("All tools registered successfully")
    
    return mcp

def main():
    """Main server entry point"""
    try:
        server_instance = setup_server()
        
        collections = mongo_client.list_collections()
        logger.info(f"Available collections: {collections}")
        
        logger.info("MongoDB Hotel Analytics MCP Server starting on HTTP...")
        logger.info("Server will be available at: http://localhost:8000")
        
        server_instance.run(transport="http", host="127.0.0.1", port=8000)
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        mongo_client.disconnect()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Server error: {e}")
        mongo_client.disconnect()

if __name__ == "__main__":
    main()