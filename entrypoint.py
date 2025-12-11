"""Application entrypoint"""

from app.core.config import get_config
from app.server import mcp


def main():
    """Run the FastMCP server"""
    config = get_config()

    print(f"Starting {config.AGENT_NAME} on {config.HOST}:{config.PORT}")

    mcp.run(
        host=config.HOST,
        port=config.PORT,
        transport="stdio",  # Use stdio transport for MCP
    )


if __name__ == "__main__":
    main()
