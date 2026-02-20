"""Multi-agent supervisor system using LangGraph StateGraph."""
from core.subagents.math_agent import call_math_agent
from core.subagents.news_agent import call_news_agent
from core.subagents.weather_agent import call_weather_agent
from core.subagents.goals import call_goals_agent


__all__ = ["call_news_agent", "call_weather_agent", "call_math_agent", "call_goals_agent"]