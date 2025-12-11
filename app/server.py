"""FastMCP server initialization"""

import logging

from fastmcp import FastMCP

from app.core.config import config
from app.routers.tool_router import register_tools

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def create_app() -> FastMCP:
    """Create and configure FastMCP application"""
    logger.info(f"Creating FastMCP server: {config.AGENT_NAME}")

    # Create FastMCP instance
    mcp = FastMCP(config.AGENT_NAME)

    # Register tools
    register_tools(mcp)

    logger.info("FastMCP server created successfully")
    return mcp


# Global MCP instance
mcp = create_app()
