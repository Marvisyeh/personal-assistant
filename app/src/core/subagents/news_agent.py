from langchain.agents import create_agent
from langchain.tools import tool

from core.tools.news import get_latest_news
from core.prompts import load_prompt
from utils.logger import setup_logger

logger = setup_logger("src.core.subagents.news_agent")

def create_news_agent(
        model: str = "anthropic:claude-haiku-4-5-20251001",
        prompt: str = "news_short",
    ):
    NEWS_AGENT_SYSTEM_PROMPT = load_prompt(prompt)
    news_agent = create_agent(
        model=model,
        tools=[get_latest_news],
        system_prompt=NEWS_AGENT_SYSTEM_PROMPT,
    )
    return news_agent

@tool("news", description="Call the news agent to get the latest news")
def call_news_agent(query: str, model: str = "anthropic:claude-haiku-4-5-20251001", prompt: str = "news_short"):
    news_agent = create_news_agent(model=model, prompt=prompt)
    result = news_agent.invoke({"messages": [{"role": "user", "content": query}]})
    logger.debug(result)
    return result["messages"][-1].content


if __name__ == "__main__":
    news_agent = create_news_agent()
    result = news_agent.invoke({"messages": [{"role": "user", "content": "今日國內外新聞"}]})
    print(result["messages"][-1].content)
