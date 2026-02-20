"""Router: classify user intent into strategy | planning | execution | review."""
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

from core.prompts import load_prompt

ROUTER_PROMPT = load_prompt("goals_router")
VALID_TARGETS = frozenset({"strategy", "planning", "execution", "review"})


def route_goals_intent(query: str, model: str = "anthropic:claude-haiku-4-5-20251001") -> str:
    """Return one of: strategy, planning, execution, review."""
    llm = init_chat_model(model=model)
    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=query),
    ]
    response = llm.invoke(messages)
    text = (response.content or "").strip().lower()
    # Take first word or first line
    word = text.split()[0] if text else ""
    if word in VALID_TARGETS:
        return word
    # Fallback: planning
    return "planning"

if __name__ == "__main__":
    print(route_goals_intent("訂年度目標"))
    # print(route_goals_intent("幫我排本週計劃"))
    # print(route_goals_intent("做晚間回顧"))
    # print(route_goals_intent("臨時多兩小時會議幫我重排"))