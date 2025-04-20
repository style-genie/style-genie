# fashion_agent/server.py
# This file will contain the code for the MCP server.

import agent
from mcp.server.fastmcp import Context, FastMCP

# Create a named server
mcp = agent.fashion_agent

if __name__ == "__main__":
    agent.fashion_agent.run()
