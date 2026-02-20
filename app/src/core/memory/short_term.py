"""
Short-term memory: session-scoped conversation history and LangGraph checkpointer.
同一 session_id 的對話由 checkpointer 依 thread_id 持久化（同 process 內）。
"""
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

_store: dict[str, "CustomChatMessageHistory"] = {}
_checkpointer: InMemorySaver | None = None


class CustomChatMessageHistory(ChatMessageHistory):
    """Session chat history with support for dict and LangChain message formats."""

    def add_message(self, message):
        if isinstance(message, dict):
            if "text" in message:
                self.messages.append(AIMessage(content=message["text"]))
            elif "content" in message:
                if message.get("role") == "assistant":
                    self.messages.append(AIMessage(content=message["content"]))
                else:
                    self.messages.append(HumanMessage(content=message["content"]))
        else:
            self.messages.append(message)


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Return the chat history for the given session (for display/API)."""
    if session_id not in _store:
        _store[session_id] = CustomChatMessageHistory()
    return _store[session_id]


def get_checkpointer() -> InMemorySaver:
    """Return a shared checkpointer so all agents use the same session state by thread_id."""
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = InMemorySaver()
    return _checkpointer
