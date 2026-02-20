"""Agent middleware: e.g. trim messages to fit context window."""
from typing import Any

from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime

from utils.logger import setup_logger

logger = setup_logger("src.core.agent.middleware")


@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the first message and last few to fit context window."""
    messages = state["messages"]
    # logger.info("before trim messages: %s", messages)

    if len(messages) <= 3:
        return None

    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages,
        ]
    }
