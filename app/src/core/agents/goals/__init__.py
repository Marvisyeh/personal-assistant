"""Goals assistant: 年度→季度→週→日→回顧，單一入口由 router 判斷調用哪個 agent."""
import re
from datetime import datetime

from langchain.tools import tool

from core.agents.goals._router import route_goals_intent
from core.agents.goals.subagents.strategy_agent import create_strategy_agent
from core.agents.goals.subagents.planning_agent import create_planning_agent
from core.agents.goals.subagents.execution_agent import create_execution_agent
from core.agents.goals.subagents.review_agent import create_review_agent
from core.common.tools.goals import set_year_plan

from utils.logger import setup_logger

logger = setup_logger("src.core.agents.goals")


def _strategy_actually_called_set_year_plan(result: dict) -> bool:
    """Check if strategy agent's run included a set_year_plan tool call."""
    for msg in result.get("messages", []):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                if (isinstance(tc, dict) and tc.get("name") == "set_year_plan") or (
                    getattr(tc, "name", None) == "set_year_plan"
                ):
                    return True
    return False


def _looks_like_goals_content(query: str) -> bool:
    """Heuristic: user might be stating annual goals or asking to record."""
    keywords = ("目標", "今年", "年度", "記錄", "考取", "申請", "習慣", "想", "要", "提升", "達成")
    return any(kw in query for kw in keywords) and len(query.strip()) > 4


def _extract_outcomes_from_query(query: str) -> tuple[str, list[str]]:
    """Extract year_theme (one line) and outcomes (list) from user message. Fallback for when agent didn't call set_year_plan."""
    query = query.strip()
    # Split by common list delimiters
    parts = re.split(r"[、，,;；\n]", query)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return query[:80] if len(query) > 80 else (query or "使用者年度目標"), []
    # First part often is the theme or intro (e.g. "今年的目標是提升專業技能")
    year_theme = parts[0][:100] if parts else "使用者年度目標"
    # Rest are outcomes; if only one part, use it as single outcome
    if len(parts) == 1:
        outcomes = [parts[0]] if len(parts[0]) > 2 else []
    else:
        # Skip very short intro like "記錄一下"
        outcomes = [p for p in parts if len(p) > 2]
    if not outcomes and query:
        outcomes = [query[:120]]
    return year_theme, outcomes[:10]


def _strategy_fallback_save(query: str) -> None:
    """If strategy agent didn't call set_year_plan, write from parsed query so storage is not empty."""
    year_theme, outcomes = _extract_outcomes_from_query(query)
    # 只有解析出至少一項 outcome 或足夠長的 theme 才寫入，避免「記錄一下」覆蓋成空
    if not outcomes and len(year_theme) < 15:
        return
    try:
        set_year_plan.invoke({
            "year_theme": year_theme,
            "outcomes": outcomes,
            "year": datetime.now().year,
        })
        logger.info("goals fallback: set_year_plan called with %d outcomes", len(outcomes))
    except Exception as e:
        logger.warning("goals fallback set_year_plan failed: %s", e)


def _dispatch_goals(query: str, model: str = "anthropic:claude-haiku-4-5-20251001") -> str:
    """Route to strategy / planning / execution / review and return that agent's response."""
    target = route_goals_intent(query, model=model)
    logger.info("goals router -> %s", target)
    if target == "strategy":
        agent = create_strategy_agent(model=model)
    elif target == "planning":
        agent = create_planning_agent(model=model)
    elif target == "execution":
        agent = create_execution_agent(model=model)
    else:
        agent = create_review_agent(model=model)
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    # 保底：若為 strategy 且 agent 沒有呼叫 set_year_plan，就從 query 解析並代為寫入
    if target == "strategy" and not _strategy_actually_called_set_year_plan(result):
        if _looks_like_goals_content(query):
            _strategy_fallback_save(query)
    content = result["messages"][-1].content
    if isinstance(content, list):
        content = "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        ).strip()
    return content or "無法取得目標規劃結果"


@tool(
    "goals",
    description="目標與規劃助理：年度/季度 OKR、本週與每日排程、臨時重排、晚間回顧。使用者說排程、回顧、重排、訂 OKR 等時可呼叫。",
)
def call_goals_agent(
    query: str,
    model: str = "anthropic:claude-haiku-4-5-20251001",
) -> str:
    """Single entry: router 判斷意圖後調用對應的 strategy / planning / execution / review agent."""
    return _dispatch_goals(query, model=model)


__all__ = ["call_goals_agent"]
