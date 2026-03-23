import psutil
from langchain_core.tools import tool


class MCPManager:
    """Backward-compatible manager used by MCP node code paths."""

    async def get_all_workers_system_stats(self) -> str:
        """Return battery information in the previous MCP stats contract."""
        return get_battery_status.invoke({})


# Keep global `mcp` for compatibility with existing imports.
mcp = MCPManager()

# Tool exposed to LangGraph/LangChain.
@tool
def get_battery_status() -> str:
    """Get the laptop battery percentage and charging status."""
    try:
        battery = psutil.sensors_battery()

        if battery is None:
            return "Battery info not available."

        plugged = "Plugged in" if battery.power_plugged else "On battery"

        return f"🔋 Battery: {battery.percent}% ({plugged})"

    except Exception as e:
        return f"Error: {str(e)}"