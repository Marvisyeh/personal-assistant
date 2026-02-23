"""Investment planning agent: 投資計劃，包含資產配置、標的、風險屬性（與所得分配的投資金相依）."""
from pathlib import Path

from langchain.agents import create_agent

from core.common.prompts import load_prompt
from core.common.tools.calculator import add, subtract, multiply, divide
from core.common.tools.budget import (
    get_investment_plan,
    get_monthly_expenses,
    set_investment_plan,
    set_monthly_expense,
)

_PROMPTS_DIR = Path(__file__).resolve().parent

INVESTMENT_TOOLS = [
    get_monthly_expenses,
    set_monthly_expense,
    get_investment_plan,
    set_investment_plan,
    add,
    subtract,
    multiply,
    divide,
]


def create_investment_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "finance_investment",
):
    system_prompt = load_prompt(prompt, base_dir=_PROMPTS_DIR)
    return create_agent(
        model=model,
        tools=INVESTMENT_TOOLS,
        system_prompt=system_prompt,
    )
