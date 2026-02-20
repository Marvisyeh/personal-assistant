"""Execution coach agent: 臨時重排、取捨、更新今日計劃."""
from langchain.agents import create_agent

from core.prompts import load_prompt
from core.tools.goals import (
    get_day_plan,
    set_day_plan,
    get_week_plan,
    set_week_plan,
)


def create_execution_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "goals_execution",
):
    system_prompt = load_prompt(prompt)
    return create_agent(
        model=model,
        tools=[get_day_plan, set_day_plan, get_week_plan, set_week_plan],
        system_prompt=system_prompt,
    )
