from langchain.agents import create_agent
from langchain.tools import tool

from core.tools.weather import get_weather
from core.prompts import load_prompt
from utils.logger import setup_logger

logger = setup_logger("src.core.subagents.weather_agent")

def create_weather_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "weather_short",
):
    WEATHER_AGENT_SYSTEM_PROMPT = load_prompt(prompt)
    weather_agent = create_agent(
        model=model,
        tools=[get_weather],
        system_prompt=WEATHER_AGENT_SYSTEM_PROMPT,
    )
    return weather_agent


@tool("weather", description="Call the weather agent to get the latest weather")
def call_weather_agent(query: str, model: str = "anthropic:claude-haiku-4-5-20251001", prompt: str = "weather_short"):
    weather_agent = create_weather_agent(model=model, prompt=prompt)
    result = weather_agent.invoke({"messages": [{"role": "user", "content": query}]})
    logger.debug(result)
    return result["messages"][-1].content


if __name__ == "__main__":
    weather_agent = create_weather_agent()
    result = weather_agent.invoke(
        {"messages": [{"role": "user", "content": "今日台北天氣如何？"}]}
    )
    print(result["messages"][-1].content)
