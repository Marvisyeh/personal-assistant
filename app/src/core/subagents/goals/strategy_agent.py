"""Strategy agent: 年度主題、Outcomes、季度 OKR、限制與風險."""
from langchain.agents import create_agent

from core.prompts import load_prompt
from core.tools.goals import (
    get_year_plan,
    set_year_plan,
    get_quarter_okr,
    set_quarter_okr,
)


def create_strategy_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "goals_strategy",
):
    system_prompt = load_prompt(prompt)
    return create_agent(
        model=model,
        tools=[get_year_plan, set_year_plan, get_quarter_okr, set_quarter_okr],
        system_prompt=system_prompt,
    )
