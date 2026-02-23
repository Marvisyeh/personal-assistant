"""Review agent: 晚間回顧、日報、明日草案、KR 推進."""
from pathlib import Path

from langchain.agents import create_agent

from core.common.prompts import load_prompt
from core.common.tools.goals import (
    get_day_plan,
    set_day_plan,
    get_week_plan,
    get_quarter_okr,
    set_quarter_okr,
)

_PROMPTS_DIR = Path(__file__).resolve().parent


def create_review_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "goals_review",
):
    system_prompt = load_prompt(prompt, base_dir=_PROMPTS_DIR)
    return create_agent(
        model=model,
        tools=[
            get_day_plan,
            set_day_plan,
            get_week_plan,
            get_quarter_okr,
            set_quarter_okr,
        ],
        system_prompt=system_prompt,
    )
