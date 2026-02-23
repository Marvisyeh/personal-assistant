"""Router: classify user intent into income | investment."""
from pathlib import Path

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from core.common.prompts import load_prompt

_PROMPTS_DIR = Path(__file__).resolve().parent
ROUTER_PROMPT = load_prompt("finance_router", base_dir=_PROMPTS_DIR)
VALID_TARGETS = frozenset({"income", "investment"})


def route_finance_intent(query: str, model: str = "anthropic:claude-haiku-4-5-20251001") -> str:
    """Return one of: income, investment."""
    llm = init_chat_model(model=model)
    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=query),
    ]
    response = llm.invoke(messages)
    text = (response.content or "").strip().lower()
    word = text.split()[0] if text else ""
    if word in VALID_TARGETS:
        return word
    return "income"


if __name__ == "__main__":
    print(route_finance_intent("我月薪 64000，房貸 15000"))
    print(route_finance_intent("我想買一台新電腦"))
    print(route_finance_intent("我的投資金要怎麼配置股債比例"))
    print(route_finance_intent("幫我設定每月伙食費 4500"))
