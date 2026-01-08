import os
from typing import Annotated, TypedDict, List
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List, "The messages in the conversation"]

# Initialize the LLM
llm = ChatAnthropic(model="claude-3-5-haiku-20241022")

# We will bind tools later in the FastAPI app when we connect to the MCP server
def create_agent(tools):
    llm_with_tools = llm.bind_tools(tools)
    
    def call_model(state: AgentState):
        messages = state['messages']
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Define the graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    workflow.set_entry_point("agent")
    
    def should_continue(state: AgentState):
        messages = state['messages']
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
    
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
