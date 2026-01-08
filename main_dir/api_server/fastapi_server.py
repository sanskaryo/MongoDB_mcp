import asyncio
import json
import os
import sys
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

if sys.platform == "win32":  # Ensure subprocesses inherit selector loop
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.langgraph_agent import MongoDBAnalyticsAgent

# Global agent instance
agent: Optional[MongoDBAnalyticsAgent] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent
    try:
        # Startup
        agent = MongoDBAnalyticsAgent()
        if await agent.initialize():
            print(" MongoDB Analytics Agent initialized successfully")
        else:
            print(" Failed to initialize MongoDB Analytics Agent")
            raise Exception("Agent initialization failed")
        yield
    except Exception as e:
        print(f" Startup error: {e}")
        raise e
    finally:
        # Shutdown
        if agent:
            await agent.cleanup()
            print(" Agent cleanup completed")

app = FastAPI(
    title="MongoDB Analytics Agent API",
    description="REST API for MongoDB hotel analytics with chart generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static files for charts
charts_dir = os.path.join(os.getcwd(), "charts")
os.makedirs(charts_dir, exist_ok=True)
app.mount("/charts", StaticFiles(directory=charts_dir), name="charts")

# Mount UI static files if they exist
ui_dir = os.path.join(os.path.dirname(__file__), "ui", "build")
if os.path.exists(ui_dir):
    app.mount("/ui", StaticFiles(directory=ui_dir, html=True), name="ui")

class QueryRequest(BaseModel):
    query: str
    generate_chart: bool = False
    chart_type: Optional[str] = None  # auto, bar, line, pie, horizontal_bar, scatter
    chart_title: Optional[str] = None
    save_chart: bool = True
    chart_size: Optional[tuple] = None  # (width, height)

class QueryResponse(BaseModel):
    success: bool
    response: str
    tool_calls: int
    message_count: int
    tools_used: List[str] = []
    chart_path: Optional[str] = None
    chart_title: Optional[str] = None
    chart_type: Optional[str] = None
    error: Optional[str] = None
    suggestion: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MongoDB Analytics Agent API",
        "version": "1.0.0", 
        "description": "REST API for MongoDB hotel analytics with chart generation",
        "mcp_server": "http://localhost:8000/mcp",
        "endpoints": {
            "/query": "POST - Send analytics queries to the agent",
            "/tools": "GET - List available MCP tools", 
            "/health": "GET - Health check",
            "/charts/{filename}": "GET - Retrieve generated charts",
            "/charts": "GET - List available charts",
            "/clear-charts": "DELETE - Clear all generated charts",
            "/docs": "GET - API documentation"
        },
        "chart_types": ["auto", "bar", "line", "pie", "horizontal_bar", "scatter"],
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global agent
    if agent and agent.agent:
        return {"status": "healthy", "agent_initialized": True}
    return {"status": "unhealthy", "agent_initialized": False}

@app.get("/tools")
async def get_tools():
    """Get list of available tools"""
    global agent
    if not agent or not agent.tools:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    tools_info = []
    for tool in agent.tools:
        # Safely handle tool schema access
        parameters = []
        if hasattr(tool, 'input_schema'):
            schema = tool.input_schema
            if isinstance(schema, dict) and 'properties' in schema:
                parameters = list(schema['properties'].keys())
            elif hasattr(schema, 'model_fields'):
                parameters = list(schema.model_fields.keys())
        
        tools_info.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": parameters
        })
    
    return {"tools": tools_info, "total_count": len(tools_info)}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process analytics query with optional chart generation"""
    global agent
    
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Process the query
        result = await agent.query(request.query)

        # Handle structured response (list of content blocks)
        response_content = result["response"]
        if isinstance(response_content, list):
            # Extract text from content blocks
            response_parts = []
            for block in response_content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        response_parts.append(block.get("text", ""))
                    elif "text" in block:  # Fallback
                        response_parts.append(block["text"])
            result["response"] = "\n".join(response_parts)
        
        # Check if a chart was generated by the agent
        chart_path = None
        chart_title = None
        chart_type = None
        
        # Look for chart information in the response or tools used
        if result.get("success") and "generate_chart_from_data" in result.get("tools_used", []):
            # Check for newest chart file
            charts_dir = "./charts"
            if os.path.exists(charts_dir):
                chart_files = [f for f in os.listdir(charts_dir) if f.endswith('.png')]
                if chart_files:
                    # Get the most recently created chart
                    chart_files.sort(key=lambda x: os.path.getctime(os.path.join(charts_dir, x)), reverse=True)
                    newest_chart = chart_files[0]
                    chart_path = f"/charts/{newest_chart}"
                    chart_title = "Generated Chart"
                    chart_type = "image"
        
        # Also check if the agent explicitly requested chart generation
        if request.generate_chart and result["success"]:
            chart_info = await generate_chart_from_result(
                result, 
                request.query,
                request.chart_type or "auto"
            )
            if chart_info.get("path"):
                chart_path = chart_info.get("path")
                chart_title = chart_info.get("title", "Generated Chart") 
                chart_type = chart_info.get("type", "image")
        
        return QueryResponse(
            success=result["success"],
            response=result["response"],
            tool_calls=result.get("tool_calls", 0),
            message_count=result.get("message_count", 0),
            tools_used=result.get("tools_used", []),
            chart_path=chart_path,
            chart_title=chart_title,
            chart_type=chart_type,
            error=result.get("error"),
            suggestion=result.get("suggestion")
        )
        
    except Exception as e:
        print(f"❌ Error in process_query: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/charts/{filename}")
async def get_chart(filename: str):
    """Serve generated chart files"""
    chart_path = f"./charts/{filename}"
    if os.path.exists(chart_path):
        return FileResponse(
            path=chart_path,
            media_type="image/png",
            filename=filename
        )
    else:
        raise HTTPException(status_code=404, detail="Chart not found")

@app.get("/charts")
async def list_charts():
    """List all available chart files"""
    charts_dir = "./charts"
    if not os.path.exists(charts_dir):
        return {"charts": [], "count": 0}
    
    chart_files = []
    for filename in os.listdir(charts_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.svg')):
            file_path = os.path.join(charts_dir, filename)
            file_stats = os.stat(file_path)
            chart_files.append({
                "filename": filename,
                "path": f"/charts/{filename}",
                "size": file_stats.st_size,
                "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
            })
    
    # Sort by creation date, newest first
    chart_files.sort(key=lambda x: x["created"], reverse=True)
    
    return {
        "charts": chart_files,
        "count": len(chart_files),
        "charts_directory": charts_dir
    }

@app.delete("/clear-charts")
async def clear_charts():
    """Clear all generated chart files"""
    charts_dir = "./charts"
    if not os.path.exists(charts_dir):
        return {"message": "No charts directory found", "deleted": 0}
    
    deleted_count = 0
    for filename in os.listdir(charts_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.svg')):
            file_path = os.path.join(charts_dir, filename)
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
    
    return {
        "message": f"Cleared {deleted_count} chart files",
        "deleted": deleted_count
    }

async def generate_chart_from_result(result: Dict[str, Any], query: str, chart_type: Optional[str] = None) -> Dict[str, Any]:
    """Generate chart based on query result and context"""
    try:
        # Import chart generation module
        from helpers.chart_generator import ChartGenerator
        
        chart_gen = ChartGenerator()
        
        # Determine appropriate chart type if not specified
        if not chart_type or chart_type == "auto":
            chart_type = chart_gen.suggest_chart_type(query, result.get("tools_used", []))
        
        # Generate chart
        chart_result = await chart_gen.generate_chart(
            query=query,
            result_data=result,
            chart_type=chart_type,
            tools_used=result.get("tools_used", [])
        )
        
        if chart_result and "path" in chart_result:
            filename = os.path.basename(chart_result["path"])
            return {
                "path": f"/charts/{filename}",
                "title": chart_result.get("title", f"Chart for: {query[:50]}..."),
                "filename": filename,
                "type": chart_type
            }
    except ImportError:
        print("Warning: ChartGenerator not available")
    except Exception as e:
        print(f"Error generating chart: {e}")
    
    return {}

if __name__ == "__main__":
    import uvicorn
    
    # Create charts directory if it doesn't exist
    os.makedirs("./charts", exist_ok=True)
    
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0", 
        port=8001,
        reload=True
    )