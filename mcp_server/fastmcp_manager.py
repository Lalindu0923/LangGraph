# langgraph_api/mcp_server/fastmcp_manager.py
"""FastMCP Manager for LangGraph: manages MCP (Model Context Protocol) tools and workers."""

import json
import asyncio
from typing import Dict, Any


class MCPManager:
    """Manages MCP (Model Context Protocol) server interactions and worker stats."""
    
    def __init__(self):
        self.workers = {}
        self.is_connected = False
    
    async def get_all_workers_system_stats(self) -> str:
        """
        Retrieves system statistics from all connected MCP workers.
        
        Returns:
            Formatted string with worker stats or connection message.
        """
        if not self.is_connected:
            return "MCP Server not connected. Please initialize the MCP connection first."
        
        try:
            stats = {
                "connected_workers": len(self.workers),
                "workers": self.workers
            }
            return json.dumps(stats, indent=2)
        except Exception as e:
            return f"Error retrieving worker stats: {str(e)}"
    
    async def connect(self) -> bool:
        """Connect to MCP server. Returns True on success."""
        try:
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to MCP: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MCP server. Returns True on success."""
        self.is_connected = False
        self.workers = {}
        return True
    
    async def add_worker(self, worker_id: str, worker_info: Dict[str, Any]) -> bool:
        """Add a worker to the MCP manager."""
        self.workers[worker_id] = worker_info
        return True


# Global MCP manager instance
mcp = MCPManager()
