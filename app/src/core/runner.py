"""MultiAgentRunner: clean public interface for the supervisor multi-agent system."""
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from utils.logger import setup_logger

logger = setup_logger("src.core.agent.multi_agent.runner")


class MultiAgentRunner:
    """High-level interface for the Supervisor multi-agent system.

    Usage:
        runner = MultiAgentRunner()
        response = runner.run("幫我查台北的天氣", session_id="user_123")
        print(response)

    The supervisor automatically routes the query to the correct sub-agent:
        - news_agent    → 新聞查詢、時事分析
        - weather_agent → 天氣查詢
        - math_agent    → 數學計算
        - SELF          → 一般對話、知識問答（supervisor 直接回答）
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        model_provider: str = "openai",
        checkpointer: Any = None,
    ):
        from core.supervisor import build_supervisor_graph

        self._graph = build_supervisor_graph(
            model=model,
            model_provider=model_provider,
            checkpointer=checkpointer,
        )
        logger.info(
            "MultiAgentRunner initialized (model=%s, provider=%s)", model, model_provider
        )

    def run(self, message: str, session_id: str = "default") -> str:
        """Send a message to the supervisor and return the final response.

        Args:
            message: User's input message.
            session_id: Thread ID for session memory (each unique ID = separate session).

        Returns:
            The last AI message content as a string.
        """
        config: RunnableConfig = {"configurable": {"thread_id": session_id}}
        try:
            result = self._graph.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
            )
            # Return the last meaningful AI response
            for msg in reversed(result.get("messages", [])):
                if isinstance(msg, AIMessage) and msg.content:
                    return msg.content
            return "（無回應）"
        except Exception as e:
            logger.error("MultiAgentRunner error (session=%s): %s", session_id, e)
            raise

    def stream(self, message: str, session_id: str = "default"):
        """Stream events from the supervisor graph (for real-time output).

        Yields:
            (node_name, event_data) tuples as the graph executes.
        """
        config: RunnableConfig = {"configurable": {"thread_id": session_id}}
        for event in self._graph.stream(
            {"messages": [{"role": "user", "content": message}]},
            config=config,
            stream_mode="updates",
        ):
            for node_name, data in event.items():
                yield node_name, data


# ---------------------------------------------------------------------------
# Quick manual test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    runner = MultiAgentRunner()

    test_cases = [
        # ("我叫 Marvis", "demo"),
        # ("3 乘以 7 等於多少？再加上 12", "demo"),
        # ("幫我整理今天的國際新聞", "demo"),
        ("今天台北的天氣和重點新聞", "demo"),
        # ("上述結果再加上 12 等於多少？", "demo"),

    ]

    for question, session in test_cases:
        print(f"\n{'='*60}")
        print(f"問題：{question}")
        print(f"{'='*60}")
        answer = runner.run(question, session_id=session)
        print(f"回答：{answer}")
