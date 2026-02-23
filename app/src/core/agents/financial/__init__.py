"""Financial assistant: 所得分配與投資計劃，單一入口由 router 判斷調用哪個 agent."""
from langchain.tools import tool

from core.agents.financial._router import route_finance_intent
from core.agents.financial.subagents.income_agent import create_income_agent
from core.agents.financial.subagents.investment_agent import create_investment_agent
from core.agents.financial.subagents.extraction_agent import create_extraction_agent

from utils.logger import setup_logger

logger = setup_logger("src.core.agents.financial")

# ──────────────────────────────────────────────
# 工具呼叫偵測
# ──────────────────────────────────────────────

_INCOME_WRITE_TOOLS = frozenset({
    "set_budget", "set_monthly_expense",
    "add_savings_plan", "update_savings_plan", "delete_savings_plan",
    "add_wishlist_item", "update_wishlist_item", "delete_wishlist_item",
    "set_yearly_travel_budget",
})


def _write_tools_called(result: dict, tool_names: frozenset) -> bool:
    """Check if any of the given write tools were called in the agent result."""
    for msg in result.get("messages", []):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                if name in tool_names:
                    return True
    return False


def _extraction_fallback(query: str, model: str) -> None:
    """Run extraction agent to parse and save financial data from query."""
    try:
        agent = create_extraction_agent(model=model)
        agent.invoke({"messages": [{"role": "user", "content": query}]})
        logger.info("extraction agent fallback completed")
    except Exception as e:
        logger.warning("extraction agent fallback failed: %s", e)


# ──────────────────────────────────────────────
# Dispatch
# ──────────────────────────────────────────────

def _dispatch_finance(query: str, model: str = "anthropic:claude-haiku-4-5-20251001") -> str:
    """Route to income | investment and return that agent's response."""
    target = route_finance_intent(query, model=model)
    logger.info("finance router -> %s", target)

    if target == "investment":
        agent = create_investment_agent(model=model)
        result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    else:
        agent = create_income_agent(model=model)
        result = agent.invoke({"messages": [{"role": "user", "content": query}]})
        # 保底：若 income agent 沒有呼叫任何寫入工具，交給 extraction agent 萃取並寫入
        if not _write_tools_called(result, _INCOME_WRITE_TOOLS):
            logger.info("income agent skipped write tools — running extraction agent fallback")
            _extraction_fallback(query, model)

    content = result["messages"][-1].content
    if isinstance(content, list):
        content = "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        ).strip()
    return content or "無法取得財務分析結果"


@tool(
    "finance",
    description="個人財務助理：所得分配（月薪、每月支出、存錢計劃、願望清單）與投資計劃（資產配置、股債比例、ETF 標的、風險屬性）。涉及薪資分配、預算、投資配置、存錢計畫、想買的東西時可呼叫。",
)
def call_finance_agent(
    query: str,
    model: str = "anthropic:claude-haiku-4-5-20251001",
) -> str:
    """Single entry: router 判斷意圖後調用對應的 income（所得分配）或 investment（投資計劃）agent."""
    return _dispatch_finance(query, model=model)


__all__ = ["call_finance_agent"]
