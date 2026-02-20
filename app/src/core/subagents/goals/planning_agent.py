"""Planning agent: 週 deliverables、每日 MIT/Top3/time blocks."""
from langchain.agents import create_agent

from core.prompts import load_prompt
from core.tools.goals import (
    get_year_plan,
    get_quarter_okr,
    get_week_plan,
    set_week_plan,
    get_day_plan,
    set_day_plan,
)


def create_planning_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "goals_planning",
):
    system_prompt = load_prompt(prompt)
    return create_agent(
        model=model,
        tools=[
            get_year_plan,
            get_quarter_okr,
            get_week_plan,
            set_week_plan,
            get_day_plan,
            set_day_plan,
        ],
        system_prompt=system_prompt,
    )
