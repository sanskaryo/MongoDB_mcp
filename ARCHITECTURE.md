# Project Structure

This project is now organized into clean, separate components:

## 📁 **Root Directory**
- `main.py` - **Main entry point** - starts both MCP and API servers
- `data/` - Sample data and datasets
- `mongodb_concepts/` - Educational MongoDB examples and concepts
- `requirements.txt` - Python dependencies
- `.env` - Environment variables

## 🔧 **src/mcp_server/** - Model Context Protocol Server
- `server.py` - MCP server entry point
- `mcp_instance.py` - Shared FastMCP instance
- `tools/` - MCP tool implementations (MongoDB operations)
- `models/` - Data models for MCP
- `utils/` - MCP utilities (database connections, etc.)

## 🌐 **src/api_server/** - FastAPI Application Server
- `fastapi_server.py` - FastAPI application entry point
- `agent/` - LangGraph agent implementation
- `helpers/` - Chart generation and data processing utilities
- `ui/` - Frontend UI components (React app)
- `*.log` - Server log files

## 🎯 **Usage**

### Start Everything (Recommended)
```bash
python main.py
```

### Start Individual Components
```bash
# MCP Server only
python src/mcp_server/server.py

# API Server only  
python src/api_server/fastapi_server.py

# MongoDB Concepts (Educational)
python mongodb_concepts/get_collections.py
```

## 🏗️ **Architecture**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   main.py   │───▶│ MCP Server  │    │ API Server  │
│             │    │ (Port 8000) │    │ (Port 8001) │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
                   ┌─────────────────────────────────┐
                   │        MongoDB Atlas            │
                   │     (hotel_management DB)       │
                   └─────────────────────────────────┘
```

## 🔄 **Clean Separation**

- **MCP Server**: Handles Model Context Protocol tools for MongoDB operations
- **API Server**: Provides REST APIs, agent functionality, and web interface  
- **Main Entry**: Orchestrates both servers with proper startup sequence
- **MongoDB Concepts**: Educational examples independent of servers