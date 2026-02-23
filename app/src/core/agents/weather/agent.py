from pathlib import Path

from langchain.agents import create_agent
from langchain.tools import tool

from core.common.prompts import load_prompt
from core.common.tools.weather import get_weather
from utils.logger import setup_logger

_PROMPTS_DIR = Path(__file__).resolve().parent
logger = setup_logger("src.core.agents.weather")

def create_weather_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "prompt_short",
):
    WEATHER_AGENT_SYSTEM_PROMPT = load_prompt(prompt, base_dir=_PROMPTS_DIR)
    weather_agent = create_agent(
        model=model,
        tools=[get_weather],
        system_prompt=WEATHER_AGENT_SYSTEM_PROMPT,
    )
    return weather_agent


@tool("weather", description="Call the weather agent to get the latest weather")
def call_weather_agent(query: str, model: str = "anthropic:claude-haiku-4-5-20251001", prompt: str = "prompt_short"):
    weather_agent = create_weather_agent(model=model, prompt=prompt)
    result = weather_agent.invoke({"messages": [{"role": "user", "content": query}]})
    logger.debug(result)
    content = result["messages"][-1].content
    if isinstance(content, list):
        content = "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        ).strip()
    return content or "無法取得天氣資訊"


if __name__ == "__main__":
    weather_agent = create_weather_agent()
    result = weather_agent.invoke(
        {"messages": [{"role": "user", "content": "今日台北天氣如何？"}]}
    )
    print(result["messages"][-1].content)
