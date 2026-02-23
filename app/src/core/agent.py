"""Agent class: run messages with session-scoped state via checkpointer."""
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from core.builder import build_agent
from utils.logger import setup_logger

logger = setup_logger("src.core.agent.agent")


class Agent:
    """
    通用 Agent 包裝：
    - 維持 session-scoped state（經由 checkpointer）
    - 封裝 LangGraph agent 介面成簡單的 `run(message, session_id)`

    專用型的 domain agent（例如新聞、任務管理）請放在獨立模組裡，
    透過這個通用 `Agent` 類別與不同的 system_prompt / tools 組合出來。
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        model_provider: str = "openai",
        tools: list[Any] | None = None,
        checkpointer: Any = None,
        system_prompt: str | None = None,
    ):
        self.tools = list(tools) if tools else []
        self._checkpointer = checkpointer
        self._model = model
        self._model_provider = model_provider
        self._system_prompt = system_prompt
        self.agent = build_agent(
            model=model,
            model_provider=model_provider,
            tools=self.tools,
            checkpointer=checkpointer,
            system_prompt=system_prompt
            if system_prompt is not None
            else "You are a helpful assistant. Be concise and accurate. respond in traditional chinese.",
        )

    def add_tool(self, tool: Any) -> None:
        self.tools.append(tool)
        self.agent = build_agent(
            model=self._model,
            model_provider=self._model_provider,
            tools=self.tools,
            checkpointer=self._checkpointer,
            system_prompt=self._system_prompt,
        )

    def add_tools(self, tools: list[Any]) -> None:
        self.tools.extend(tools)
        self.agent = build_agent(
            model=self._model,
            model_provider=self._model_provider,
            tools=self.tools,
            checkpointer=self._checkpointer,
            system_prompt=self._system_prompt,
        )

    def run(self, message: str, session_id: str = "default") -> str:
        config: RunnableConfig = {"configurable": {"thread_id": session_id}}
        try:
            response = self.agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
            )
            if isinstance(response, dict) and "messages" in response:
                messages = response["messages"]
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage) and getattr(msg, "content", None):
                        return msg.content
            return response
        except Exception as e:
            logger.error("Error processing message for session %s: %s", session_id, e)
            raise


if __name__ == "__main__":
    from core.memory.long_term import InMemoryLongTermMemory
    from core.memory.short_term import get_checkpointer
    from core.agents import call_news_agent, call_weather_agent, call_math_agent
    from core.agents.goals import call_goals_agent
    from core.agents.financial import call_finance_agent

    checkpointer = get_checkpointer()
    agent = Agent(
        model="claude-haiku-4-5-20251001",
        model_provider="anthropic",
        checkpointer=checkpointer,
    )
    long_term_memory = InMemoryLongTermMemory()
    agent.add_tools(
        [
            long_term_memory.search,
            long_term_memory.add,
            call_finance_agent,
            call_news_agent,
            call_weather_agent,
            call_math_agent,
            call_goals_agent,
        ]
    )
    # result = agent.run("My name is Marvis", session_id="demo")
    # print(result)
    # details.append(result)
    # result = agent.run("What is my name?", session_id="demo")
    # print(result)
    # details.append(result)
    # result = agent.run("What is 2 + 2?", session_id="demo")
    # print(result)
    # details.append(result)
    # result = agent.run("今日台北天氣如何？", session_id="demo")
    # print(result)
    # result = agent.run("今天有什麼重要國際新聞？", session_id="demo")
    # print(result)
    # result = agent.run("今日台北天氣和國際重點新聞", session_id="demo")
    # print(result)

    while True:
        query = input("Enter your query: ")
        if query == "exit":
            break
        result = agent.run(query, session_id="demo")
        print(result)