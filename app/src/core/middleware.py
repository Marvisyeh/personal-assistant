"""Agent middleware: e.g. trim messages to fit context window."""
from typing import Any

from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langchain_core.messages import HumanMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime

from utils.logger import setup_logger

logger = setup_logger("src.core.agent.middleware")


@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the first message and last few turns to fit context window.

    Always starts the recent slice from a HumanMessage to avoid sending
    orphaned tool_result blocks (which Anthropic API rejects with 400).
    """
    messages = state["messages"]

    if len(messages) <= 3:
        return {"messages": messages}

    first_msg = messages[0]
    rest = messages[1:]

    # Take the last N messages as candidates, then walk forward until we
    # hit a HumanMessage so we never start with an orphaned ToolMessage.
    candidates = rest[-6:]
    safe_start = 0
    for i, msg in enumerate(candidates):
        if isinstance(msg, HumanMessage):
            safe_start = i
            break

    recent_messages = candidates[safe_start:]

    # Edge case: no HumanMessage found in candidates — keep only first_msg
    # to avoid sending an invalid message sequence.
    if not recent_messages or not isinstance(recent_messages[0], HumanMessage):
        recent_messages = []

    new_messages = [first_msg] + recent_messages
    logger.debug("trim_messages: kept %d/%d messages", len(new_messages), len(messages))

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages,
        ]
    }
