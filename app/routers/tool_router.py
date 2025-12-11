"""MCP tool router"""

import logging

from fastmcp import FastMCP

from app.core.agents.simple_agent import agent

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP) -> None:
    """Register MCP tools to the server"""

    @mcp.tool()
    async def ask_question(query: str) -> str:
        """Ask a question to the AI agent

        Args:
            query: The question to ask

        Returns:
            AI agent's response
        """
        logger.info(f"Received query: {query}")
        response = await agent.invoke(query)
        logger.info(f"Generated response: {response[:100]}...")
        return response

    @mcp.tool()
    async def get_greeting(name: str = "User") -> str:
        """Get a personalized greeting

        Args:
            name: Name to greet (default: User)

        Returns:
            Greeting message
        """
        return f"Hello, {name}! How can I help you today?"
