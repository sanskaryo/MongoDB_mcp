from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from agent import create_agent
from mcp_server import mcp 
from langchain_core.messages import HumanMessage, AIMessage
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MongoDB Analytics Agent API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get tools from FastMCP
# In a real MCP setup, you'd use an MCP client to connect to the server on port 8000
# For this "from scratch" guide, we'll use the tools defined in mcp_server.py
tools = mcp._tools.values() 
agent_executor = create_agent(list(tools))

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Convert history to LangChain messages
        messages = []
        for msg in request.history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=request.message))
        
        # Run the agent
        result = agent_executor.invoke({"messages": messages})
        
        # Get the last message (the agent's response)
        response_message = result["messages"][-1].content
        
        return {"response": response_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
