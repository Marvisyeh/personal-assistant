"""Extraction agent: 從使用者訊息萃取財務數字並寫入儲存，不做分析或建議."""
from pathlib import Path

from langchain.agents import create_agent

from core.common.prompts import load_prompt
from core.common.tools.calculator import add
from core.common.tools.budget import (
    get_monthly_expenses,
    set_budget,
    set_monthly_expense,
)

_PROMPTS_DIR = Path(__file__).resolve().parent

EXTRACTION_TOOLS = [
    get_monthly_expenses,
    set_budget,
    set_monthly_expense,
    add,
]


def create_extraction_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "finance_extraction",
):
    system_prompt = load_prompt(prompt, base_dir=_PROMPTS_DIR)
    return create_agent(
        model=model,
        tools=EXTRACTION_TOOLS,
        system_prompt=system_prompt,
    )
