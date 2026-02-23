from pathlib import Path

from langchain.agents import create_agent
from langchain.tools import tool

from core.common.prompts import load_prompt
from core.common.tools.news import get_latest_news
from utils.logger import setup_logger

_PROMPTS_DIR = Path(__file__).resolve().parent
logger = setup_logger("src.core.agents.news")

def create_news_agent(
        model: str = "anthropic:claude-haiku-4-5-20251001",
        prompt: str = "news_short",
    ):
    NEWS_AGENT_SYSTEM_PROMPT = load_prompt(prompt, base_dir=_PROMPTS_DIR)
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
    content = result["messages"][-1].content
    if isinstance(content, list):
        content = "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        ).strip()
    return content or "無法取得新聞資訊"


if __name__ == "__main__":
    news_agent = create_news_agent()
    result = news_agent.invoke({"messages": [{"role": "user", "content": "今日國內外新聞"}]})
    print(result["messages"][-1].content)
