"""
LangGraph Agent that connects to MongoDB MCP Server
Uses Groq for LLM and integrates with our MCP tools
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class MongoDBAnalyticsAgent:
    """LangGraph agent that uses MongoDB MCP tools via Groq"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None, mcp_server_url: str = "http://localhost:8000/mcp"):
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.mcp_server_url = mcp_server_url
        
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it in environment or pass as parameter")
        
        # Set API key in environment for ChatAnthropic
        os.environ["ANTHROPIC_API_KEY"] = self.anthropic_api_key
        
        # Initialize Anthropic model for tool calling
        self.model = ChatAnthropic(
            model_name="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 model
            temperature=0,
            max_tokens_to_sample=2000,
            timeout=60,
            stop=[]
        )
        
        self.client = None
        self.tools = None
        self.agent = None
    
    async def initialize(self):
        """Initialize MCP client and load tools"""
        try:
            print("🔄 Initializing MCP client...")
            # Setup MCP client to connect to our MongoDB server
            self.client = MultiServerMCPClient(
                {
                    "mongodb": {
                        "url": self.mcp_server_url,
                        "transport": "streamable_http",
                    }
                }
            )
            
            print("🔄 Getting available tools...")
            # Get available tools from MCP server
            self.tools = await self.client.get_tools()
            print(f"✅ Connected to MCP server. Found {len(self.tools)} tools:")
            for tool in self.tools:
                print(f"   📧 {tool.name}: {tool.description}")
            
            print("🔄 Creating agent...")
            # Create agent with explicit tool calling instructions
            system_prompt = """You are a MongoDB analytics assistant for hotel management data. You have access to specialized tools for comprehensive data analysis.

DATABASE COLLECTIONS:
- orders: Customer orders with items, dates, amounts, types  
- customers: Customer profiles with segments, spending, loyalty points
- menu_items: Restaurant menu with prices and categories
- delivery_details: Delivery logistics and tracking
- users: System users and staff information
- audit_logs: System activity and audit trails

IMPORTANT DATA HANDLING RULES:
1. ALWAYS check data availability first using get_data_date_range() when users ask about date-based queries or trends
2. Use the actual date ranges returned by get_data_date_range() for subsequent queries
3. If user asks about "last month" or relative dates, first check what data is available, then calculate appropriate dates
4. When calling tools, use proper JSON format for parameters. Always include required parameters.
5. ONLY generate charts when user explicitly asks for charts, graphs, or visualizations
6. For simple questions about counts, totals, or data analysis, provide text responses without charts

Examples of correct workflow:
1. User asks: "How many delivery orders last month?"
   - First call: get_data_date_range("orders") 
   - Then use mongodb_query or search_orders_by_criteria to count delivery orders
   - Provide a simple text answer with the count

2. User asks: "Generate a chart of revenue trends over time"
   - First call: get_data_date_range("orders")
   - Then use generate_chart_from_data for visualization

Examples of correct tool calls:
- get_data_date_range: Use collection name as string
- mongodb_query: Use collection name as string, query as JSON object
- get_revenue_by_date_range: Use dates in "YYYY-MM-DD" format based on actual data availability
- get_collection_summary: Use collection name as string

Use the available tools to answer questions about the hotel data. When asked about revenue, use revenue analytics tools. For customer questions, use customer insight tools. For simple data questions, provide direct answers without visualization unless explicitly requested. ALWAYS check data availability before making date-based queries."""

            self.agent = create_agent(
                model=self.model,
                tools=self.tools,
                system_prompt=system_prompt
            )
            
            print("✅ Agent created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def preprocess_query(self, query: str) -> str:
        """
        Enhance user queries with context and specific tool suggestions
        """
        if not query or not isinstance(query, str):
            return "Please provide a valid question about the hotel data."
            
        query = query.strip()
        if len(query) < 3:
            return "Please provide a more detailed question."
            
        query_lower = query.lower()
        suggestions = []
        
        # Revenue and financial queries
        revenue_keywords = ['revenue', 'sales', 'money', 'earning', 'profit', 'income', 'total', 'amount', 'financial']
        if any(word in query_lower for word in revenue_keywords):
            suggestions.append("💰 Revenue Analysis: Use get_daily_revenue(), get_revenue_by_date_range(), or get_top_menu_items_by_revenue()")
        
        # Customer analysis queries  
        customer_keywords = ['customer', 'client', 'buyer', 'user', 'segment', 'spending', 'loyalty', 'top customer']
        if any(word in query_lower for word in customer_keywords):
            suggestions.append("👥 Customer Insights: Use get_top_customers_by_spending() or get_customer_segments()")
            
        # Menu and product queries
        menu_keywords = ['menu', 'dish', 'food', 'item', 'popular', 'selling', 'product', 'bestseller', 'most ordered']
        if any(word in query_lower for word in menu_keywords):
            suggestions.append("🍽️ Menu Analysis: Use get_top_menu_items_by_orders() or get_top_menu_items_by_revenue()")
            
        # Operations and order queries
        ops_keywords = ['order', 'status', 'type', 'payment', 'delivery', 'operation', 'breakdown', 'distribution']
        if any(word in query_lower for word in ops_keywords):
            suggestions.append("⚙️ Operations: Use get_orders_by_status(), get_orders_by_type(), or get_payment_methods_breakdown()")
            
        # Data exploration queries
        explore_keywords = ['collections', 'available', 'database', 'schema', 'structure', 'describe', 'show me']
        if any(word in query_lower for word in explore_keywords):
            suggestions.append("🔍 Data Exploration: Use mongodb_get_collections() or mongodb_describe_collection()")
        
        # Date and time queries
        date_keywords = ['date', 'time', 'range', 'period', 'daily', 'monthly', 'week', 'month', 'year', 'september', 'october']
        if any(word in query_lower for word in date_keywords):
            suggestions.append("📅 Date Analysis: First check get_data_date_range() for available dates")
            
        # Chart and visualization queries
        chart_keywords = ['chart', 'graph', 'plot', 'visualization', 'pie', 'bar', 'line', 'generate', 'create']
        if any(word in query_lower for word in chart_keywords):
            suggestions.append("📊 Visualization: Use generate_chart_from_data() with appropriate data source")
            
        # Search and filter queries
        search_keywords = ['find', 'search', 'filter', 'where', 'lookup', 'query']
        if any(word in query_lower for word in search_keywords):
            suggestions.append("🔎 Search & Filter: Use search_orders_by_criteria() or mongodb_query()")
        
        # Add context if suggestions found
        if suggestions:
            enhanced_query = f"{query}\n\n🎯 Relevant Tools:\n" + "\n".join(f"• {s}" for s in suggestions)
            enhanced_query += "\n\n📋 Tip: Always check available data dates before querying specific time periods."
        else:
            # Generic enhancement for unclear queries
            enhanced_query = f"{query}\n\n💡 Available Analysis:\n"
            enhanced_query += "• Revenue & Financial Data\n• Customer Insights & Segments\n• Menu Performance\n• Order Analytics\n• Payment Methods\n• Data Exploration\n\n"
            enhanced_query += "🔧 Start with mongodb_get_collections() to explore available data."
        
        return enhanced_query

    async def query(self, user_input: str) -> Dict[str, Any]:
        """Process user query using the agent with preprocessing and error handling"""
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        try:
            # Preprocess query to add helpful context
            enhanced_query = self.preprocess_query(user_input)
            
            print(f"🔄 Processing query: {user_input}")
            if len(enhanced_query) > len(user_input):
                print("💡 Added tool suggestions to help with query")
            
            # Run the agent with better error handling
            try:
                result = await self.agent.ainvoke({
                    "messages": [HumanMessage(content=enhanced_query)]
                })
            except Exception as agent_error:
                # Handle agent-level errors (e.g., model API issues)
                error_msg = str(agent_error)
                if "tool_use_failed" in error_msg:
                    suggestion = "Tool call format issue. Try rephrasing your query more simply."
                elif "model" in error_msg.lower():
                    suggestion = "Model API issue. Check your GROQ_API_KEY and try again."
                else:
                    suggestion = "Try a simpler query or check system status."
                
                return {
                    "success": False,
                    "error": error_msg,
                    "suggestion": suggestion,
                    "response": f"I encountered an error: {error_msg}. {suggestion}",
                    "tool_calls": 0,
                    "message_count": 0,
                    "tools_used": []
                }
            
            # Validate result structure
            if not result or "messages" not in result or not result["messages"]:
                return {
                    "success": False,
                    "error": "Invalid agent response structure",
                    "suggestion": "Try restarting the system",
                    "response": "I encountered a system error. Please try again.",
                    "tool_calls": 0,
                    "message_count": 0,
                    "tools_used": []
                }
            
            # Extract the final response safely
            final_message = result["messages"][-1]
            if not hasattr(final_message, 'content') or not final_message.content:
                return {
                    "success": False,
                    "error": "Empty response from agent",
                    "suggestion": "Try rephrasing your query",
                    "response": "I couldn't generate a response. Please rephrase your question.",
                    "tool_calls": 0,
                    "message_count": len(result["messages"]),
                    "tools_used": []
                }
            
            # Count tool calls more accurately
            tool_calls = 0
            for message in result["messages"]:
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_calls += len(message.tool_calls)
            
            return {
                "success": True,
                "response": final_message.content,
                "message_count": len(result["messages"]),
                "tool_calls": tool_calls,
                "original_query": user_input,
                "enhanced_query": enhanced_query,
                "tools_used": [msg.tool_calls[0]['name'] for msg in result["messages"] 
                              if hasattr(msg, 'tool_calls') and msg.tool_calls] if tool_calls > 0 else []
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Query processing error: {error_msg}")
            
            # Provide more helpful error messages
            if "token" in error_msg.lower():
                suggestion = "Try using smaller limits or more specific queries to avoid token limits."
            elif "connection" in error_msg.lower():
                suggestion = "Check if the MCP server is running on localhost:8000."
            elif "tool" in error_msg.lower():
                suggestion = "The tool call format may be incorrect. Check parameter names and types."
            else:
                suggestion = "Try simplifying your query or using specific collection names."
            
            return {
                "success": False,
                "error": error_msg,
                "suggestion": suggestion,
                "response": f"I encountered an error: {error_msg}. {suggestion}"
            }
    
    async def cleanup(self):
        """Clean up resources"""
        if self.client:
            # MultiServerMCPClient cleanup - set to None for garbage collection
            try:
                self.client = None
            except Exception as e:
                print(f"Warning: MCP client cleanup error: {e}")

# Demo function
async def main():
    """Demo the MongoDB Analytics Agent"""
    print("🤖 Starting MongoDB Analytics Agent Demo")
    print("=" * 50)
    
    # Initialize agent
    agent = MongoDBAnalyticsAgent()
    
    if not await agent.initialize():
        print("❌ Failed to initialize agent")
        return
    
    # Test diverse user scenarios with direct questions
    test_queries = [
        # Data overview
        "Show me all available collections in the database",
        
        # Revenue analysis
        "What was the total revenue from September 15-30, 2024?",
        
        # Customer insights
        "List the top 5 customers by total spending",
        
        # Order analysis
        "How many orders were completed vs cancelled?",
        
        # Menu performance
        "Which 3 menu items generate the most revenue?",
        
        # Payment analysis
        "Show breakdown of payment methods used",
        
        # Date range check
        "What date range of data is available in the orders collection?",
        
        # Chart generation
        "Generate a pie chart of order types distribution"
    ]
    
    print("\n🧪 Testing queries...")
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        result = await agent.query(query)
        
        if result["success"]:
            print(f"✅ Response: {result['response']}")
            print(f"📊 Used {result['tool_calls']} tool calls, {result['message_count']} messages")
        else:
            print(f"❌ Error: {result['error']}")
    
    # Cleanup
    await agent.cleanup()
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    asyncio.run(main())