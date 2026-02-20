"""Budget agent: 理財顧問助理，協助薪資分配、預算與存錢規劃、想買的東西記錄與討論."""
from langchain.agents import create_agent
from langchain.tools import tool

from core.prompts import load_prompt
from core.tools.calculator import add, subtract, multiply, divide
from core.tools.budget import (
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
from utils.logger import setup_logger

logger = setup_logger("src.core.subagents.budget_agent")

BUDGET_TOOLS = [
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


def create_budget_agent(
    model: str = "anthropic:claude-haiku-4-5-20251001",
    prompt: str = "budget_short",
):
    system_prompt = load_prompt(prompt)
    return create_agent(
        model=model,
        tools=BUDGET_TOOLS,
        system_prompt=system_prompt,
    )


@tool("budget", description="理財顧問：薪資分配、每月預算、存錢規劃、想買的東西記錄與何時可買的討論")
def call_budget_agent(query: str, model: str = "anthropic:claude-haiku-4-5-20251001", prompt: str = "budget_short") -> str:
    """Call the budget agent (for use as a tool from main agent)."""
    agent = create_budget_agent(model=model, prompt=prompt)
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content


if __name__ == "__main__":
    # 月薪 64000, 房貸 15000, 保險費 4000, 電話費 999, 交通費 800, 伙食費 4500, 
    # 軟體訂閱費 2500, 想要固定一筆錢可以穩定投資，想買的東西有點多我們到時候再討論
    
    from langchain_core.messages import AIMessage, HumanMessage

    agent = create_budget_agent()
    messages = []  # 累積對話，讓 agent 有上下文

    while True:
        query = input("請輸入問題：")
        if query == "exit" or query == "quit":
            break
        messages.append(HumanMessage(content=query))
        reply = agent.invoke({"messages": messages})
        new_messages = reply.get("messages", [])
        # 只保留我們送出的 + agent 回覆的最後一則（避免重複累積）
        if new_messages:
            messages = new_messages
        last = messages[-1]
        text = last.content if hasattr(last, "content") else str(last)
        print(text)
