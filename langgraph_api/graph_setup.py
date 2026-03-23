# langgraph_api/graph_setup.py

from typing import Annotated
from pathlib import Path
import sys
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# MCP NODE
# Support both package-style imports and direct file loading by LangGraph.
try:
    from .nodes.mcp_node import mcp_node
except Exception:
    current_dir = Path(__file__).resolve().parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from nodes.mcp_node import mcp_node
from mcp_server.fastmcp_manager import get_battery_status

# Load env
load_dotenv()

# ==============================
# 1. STATE (Memory)
# ==============================
class State(TypedDict):
    messages: Annotated[list, add_messages]

# ==============================
# 2. TOOLS
# ==============================
@tool
def add(a: float, b: float) -> float:
    """Adds two numbers together."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divides number 'a' by number 'b'."""
    if b == 0:
        return "Error: Division by zero is not allowed."
    return a / b

def subtract(a: float, b: float) -> float:
    """Subtracts number 'b' from number 'a'."""
    return a - b

tools = [add, multiply, divide, subtract]

# ==============================
# 3. LLM
# ==============================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

llm_with_tools = llm.bind_tools(tools)

# ==============================
# 4. ROUTER
# ==============================
def router(state: State):
    latest_message = state["messages"][-1].content.lower()

    if "hi" in latest_message or "hello" in latest_message:
        return "hi"

    if "battery" in latest_message or "charge" in latest_message:
        return "mcp"

    return "chatbot"

# ==============================
# 5. NODES
# ==============================
def chatbot_node(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools=tools)

def hi_node(state: State):
    return {
        "messages": [
            ("ai", "Hello! How can I assist you today? ====❤️")
        ]
    }

# ==============================
# 6. BUILD GRAPH
# ==============================
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", tool_node)
graph_builder.add_node("Hi_Node", hi_node)
graph_builder.add_node("MCP_Node", mcp_node)

# START → Router
graph_builder.add_conditional_edges(
    START,
    router,
    {
        "hi": "Hi_Node",
        "mcp": "MCP_Node",
        "chatbot": "chatbot"
    }
)

# chatbot → tools OR end
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)

# Back edges
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("Hi_Node", END)
graph_builder.add_edge("MCP_Node", END )

# Compile graph
graph = graph_builder.compile()
