"""Simple LangGraph agent implementation"""

import logging
from typing import Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.core.config import config

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Agent state definition"""

    messages: list[BaseMessage]
    user_query: str
    final_response: str | None


class SimpleAgent:
    """Simple agent using LangGraph workflow"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            temperature=config.OPENAI_TEMPERATURE,
            api_key=config.OPENAI_API_KEY,
        )
        self.workflow = StateGraph(AgentState)
        self.compiled_workflow: CompiledStateGraph = self._compile()

    async def invoke(self, user_query: str) -> str:
        """Execute agent workflow and return response"""
        initial_state: AgentState = {
            "messages": [],
            "user_query": user_query,
            "final_response": None,
        }

        result: AgentState = await self.compiled_workflow.ainvoke(initial_state)
        return result.get("final_response", "No response generated")

    async def call_llm(self, state: AgentState) -> AgentState:
        """Call LLM with user query"""
        # Prepare messages
        messages = [
            SystemMessage(content="You are a helpful AI assistant."),
            HumanMessage(content=state["user_query"]),
        ]

        # Call LLM
        response: AIMessage = await self.llm.ainvoke(messages)

        # Update state
        state["messages"] = messages + [response]
        state["final_response"] = response.content

        return state

    def should_end(self, state: AgentState) -> Literal["end"]:
        """Always end after one LLM call (simple workflow)"""
        return "end"

    def _compile(self) -> CompiledStateGraph:
        """Compile LangGraph workflow"""
        # Add nodes
        self.workflow.add_node("llm", self.call_llm)

        # Set entry point
        self.workflow.set_entry_point("llm")

        # Add edges
        self.workflow.add_conditional_edges(
            "llm",
            self.should_end,
            {"end": END},
        )

        return self.workflow.compile()


# Global agent instance
agent = SimpleAgent()
