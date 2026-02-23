"""Planning agent: 週 deliverables、每日 MIT/Top3/time blocks."""
from pathlib import Path

from langchain.agents import create_agent

from core.common.prompts import load_prompt
from core.common.tools.goals import (
    get_year_plan,
    get_quarter_okr,
    get_week_plan,
    set_week_plan,
    get_day_plan,
    set_day_plan,
)

_PROMPTS_DIR = Path(__file__).resolve().parent


def create_planning_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "goals_planning",
):
    system_prompt = load_prompt(prompt, base_dir=_PROMPTS_DIR)
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
