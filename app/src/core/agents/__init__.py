"""Multi-agent supervisor system using LangGraph StateGraph."""
from core.agents.financial import call_finance_agent
from core.agents.math_agent import call_math_agent
from core.agents.news.news_agent import call_news_agent
from core.agents.weather.agent import call_weather_agent
from core.agents.goals import call_goals_agent


__all__ = [
    "call_finance_agent",
    "call_news_agent",
    "call_weather_agent",
    "call_math_agent",
    "call_goals_agent",
]