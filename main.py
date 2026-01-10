import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



#!/usr/bin/env python3
"""
MongoDB Analytics Agent - Main Entry Point
Clean, production-ready MongoDB analytics system with MCP server and FastAPI backend.
"""

import asyncio
import sys
import subprocess
from pathlib import Path

def start_mcp_server():
    """Start the MCP server in background"""
    print("🔄 Starting MCP Server...")
    return subprocess.Popen([
        sys.executable, "server.py"
    ], cwd=Path(__file__).parent / "src" / "mcp_server")

def start_fastapi_server():
    """Start the FastAPI server in background"""
    print("🔄 Starting FastAPI Server...")
    return subprocess.Popen([
        sys.executable, "fastapi_server.py"
    ], cwd=Path(__file__).parent / "src" / "api_server")

async def main():
    """Main entry point"""
    print("🚀 Starting MongoDB Analytics Agent System")
    
    try:
        # Start MCP server first
        mcp_process = start_mcp_server()
        await asyncio.sleep(5)  # Increased sleep time to 5 seconds
        
        # Start FastAPI server
        api_process = start_fastapi_server()
        await asyncio.sleep(3)  # Increased sleep time
        
        print("✅ System started successfully!")
        print("📊 MCP Server: http://localhost:8000")
        print("🔗 FastAPI Backend: http://localhost:8001")
        print("📖 API Docs: http://localhost:8001/docs")
        print("\nPress Ctrl+C to stop all services...")
        
        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            mcp_process.terminate()
            api_process.terminate()
            print("✅ All services stopped")
            
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())