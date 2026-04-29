"""Standalone MCP server.

When run, this exposes the tools defined in tools.py as a real MCP server
the agent (or any other MCP client like Claude Desktop) can connect to.

For development, you can run the agent in-process and skip this layer.
For demos and the article, having a real MCP server is more impressive
and exercises the actual MCP protocol.

TODO(you): This is the lightest area of the scaffold. Once Phase 1 and 2
of PROJECT_STATUS are done, come back to this and implement the standalone
MCP server. The MCP Python SDK docs are at:
https://modelcontextprotocol.io/docs/sdks/python

For now, the agent imports tools directly from tools.py.
"""
from __future__ import annotations


def main() -> None:
    """Run the MCP server. TODO(you): implement."""
    raise NotImplementedError(
        "Standalone MCP server is Phase 5. "
        "For now, the agent imports tools directly from src.mcp_server.tools."
    )


if __name__ == "__main__":
    main()
