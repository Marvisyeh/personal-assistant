"""
Long-term memory: interface and in-memory implementation.
跨 session 的知識、事實、使用者偏好；可替換為 vector store / DB。
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryEntry:
    """Single long-term memory entry."""
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class LongTermMemory:
    """Interface for long-term memory: add, search, optional summary."""

    def add(self, session_id: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Store a memory entry for the session."""
        raise NotImplementedError

    def search(self, session_id: str, query: str, k: int = 5) -> list[MemoryEntry]:
        """Return up to k relevant entries for the session and query."""
        raise NotImplementedError

    def get_summary(self, session_id: str) -> str | None:
        """Return a summary for the session, if available."""
        raise NotImplementedError


class InMemoryLongTermMemory(LongTermMemory):
    """Simple in-memory long-term memory (list per session, no embedding)."""

    def __init__(self) -> None:
        self._store: dict[str, list[MemoryEntry]] = {}

    def add(self, session_id: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        if session_id not in self._store:
            self._store[session_id] = []
        self._store[session_id].append(MemoryEntry(content=content, metadata=metadata or {}))

    def search(self, session_id: str, query: str, k: int = 5) -> list[MemoryEntry]:
        entries = self._store.get(session_id, [])
        # Naive: return last k entries (no embedding similarity yet)
        return entries[-k:] if k else []

    def get_summary(self, session_id: str) -> str | None:
        entries = self._store.get(session_id, [])
        if not entries:
            return None
        return "\n".join(e.content for e in entries[-10:])


_default_long_term: LongTermMemory | None = None


def get_long_term_memory() -> LongTermMemory:
    """Return the default long-term memory implementation."""
    global _default_long_term
    if _default_long_term is None:
        _default_long_term = InMemoryLongTermMemory()
    return _default_long_term
