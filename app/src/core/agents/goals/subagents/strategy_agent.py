"""Strategy agent: 年度主題、Outcomes、季度 OKR、限制與風險."""
from pathlib import Path

from langchain.agents import create_agent

from core.common.prompts import load_prompt
from core.common.tools.goals import (
    get_year_plan,
    set_year_plan,
    get_quarter_okr,
    set_quarter_okr,
)

_PROMPTS_DIR = Path(__file__).resolve().parent


def create_strategy_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "goals_strategy",
):
    system_prompt = load_prompt(prompt, base_dir=_PROMPTS_DIR)
    return create_agent(
        model=model,
        tools=[get_year_plan, set_year_plan, get_quarter_okr, set_quarter_okr],
        system_prompt=system_prompt,
    )
