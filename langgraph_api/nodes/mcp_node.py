# langgraph_api/nodes/mcp_node.py
from mcp_server.fastmcp_manager import mcp

async def mcp_node(state):
    """
    MCP Node for LangGraph: gets all workers system stats.
    """
    workers_stats = await mcp.get_all_workers_system_stats()
    
    return {
        "messages": [
            ("ai", f"MCP Workers Status:\n{workers_stats}")
        ]
    }