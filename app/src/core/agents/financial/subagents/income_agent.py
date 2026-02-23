"""Income allocation agent: 所得分配，包含月薪、每月支出、存錢規劃、願望清單."""
from pathlib import Path

from langchain.agents import create_agent

from core.common.prompts import load_prompt
from core.common.tools.calculator import add, subtract, multiply, divide
from core.common.tools.budget import (
    add_savings_plan,
    add_wishlist_item,
    delete_savings_plan,
    delete_wishlist_item,
    get_budget,
    get_monthly_expenses,
    get_yearly_travel_budget,
    list_savings_plans,
    list_wishlist,
    set_budget,
    set_monthly_expense,
    set_yearly_travel_budget,
    update_savings_plan,
    update_wishlist_item,
)

_PROMPTS_DIR = Path(__file__).resolve().parent

INCOME_TOOLS = [
    get_budget,
    set_budget,
    get_yearly_travel_budget,
    set_yearly_travel_budget,
    get_monthly_expenses,
    set_monthly_expense,
    list_savings_plans,
    add_savings_plan,
    update_savings_plan,
    delete_savings_plan,
    list_wishlist,
    add_wishlist_item,
    update_wishlist_item,
    delete_wishlist_item,
    add,
    subtract,
    multiply,
    divide,
]


def create_income_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "finance_income",
):
    system_prompt = load_prompt(prompt, base_dir=_PROMPTS_DIR)
    return create_agent(
        model=model,
        tools=INCOME_TOOLS,
        system_prompt=system_prompt,
    )
