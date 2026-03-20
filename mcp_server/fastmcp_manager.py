"""Simple battery status provider using psutil."""

import psutil
from langchain_core.tools import tool


class MCPManager:
    """Provides laptop battery data for the MCP node."""

    async def get_all_workers_system_stats(self) -> str:
        """Return battery percentage and charging state."""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return "Battery information is not available on this device."

            plugged = "Plugged in" if battery.power_plugged else "On battery"
            return f"Battery: {battery.percent:.0f}% ({plugged})"
        except Exception as exc:
            return f"Error reading battery information: {exc}"


# Global manager instance used by langgraph_api.nodes.mcp_node
mcp = MCPManager()


# Battery tool that LLM can call
@tool
def get_battery_status() -> str:
    """Get the laptop battery percentage and charging status."""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return "Battery information is not available on this device."
        plugged = "Plugged in" if battery.power_plugged else "On battery"
        return f"Battery: {battery.percent:.0f}% ({plugged})"
    except Exception as exc:
        return f"Error reading battery information: {exc}"
