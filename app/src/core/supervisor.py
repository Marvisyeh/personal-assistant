"""Supervisor graph: routes user queries to the appropriate sub-agent.

Architecture:
    User Input
        ↓
    Supervisor (LLM decides which agent handles the query)
        ├── news_agent    → 新聞查詢、時事分析、新聞摘要
        ├── weather_agent → 天氣查詢
        ├── math_agent    → 數學計算（加減乘除）
        └── SELF          → 一般對話、知識問答（supervisor 直接回答）
        ↓
    Response to User

Flow:
    START → supervisor → [sub-agent] → supervisor → END (when FINISH)
    START → supervisor → SELF (supervisor answers directly) → END
"""
from typing import Any, Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel

from utils.logger import setup_logger

logger = setup_logger("src.core.agent.multi_agent.supervisor")

# ---------------------------------------------------------------------------
# Agent registry – names must match the node names in the graph
# ---------------------------------------------------------------------------
AgentName = Literal["news_agent", "weather_agent", "math_agent", "SELF", "FINISH"]

AGENT_DESCRIPTIONS = {
    "news_agent": "新聞查詢、時事分析、新聞摘要、媒體報導",
    "weather_agent": "天氣查詢、氣象資訊、氣溫、降雨機率",
    "math_agent": "數學計算：加法、減法、乘法、除法",
}

SUPERVISOR_SYSTEM_PROMPT = """你是一個智能調度員（Supervisor），負責將使用者的問題分配給最合適的處理方式。

可用的專業子 Agent：
{agent_descriptions}

規則：
1. 根據使用者最新的訊息，選擇「一個」最合適的選項。
2. 只要涉及上列專業領域（天氣、新聞、數學），必須選擇對應的子 Agent，不可用 SELF 代答。
3. 若使用者同時問多個領域（例如「今天台北的天氣和重點新聞」），先選其中一個子 Agent 處理；子 Agent 回覆後你會再被呼叫，屆時再選另一個子 Agent 處理剩餘部分，直到都處理完再回傳 FINISH。
4. 僅在「不涉及天氣、新聞、數學」的一般對話、知識問答、概念解釋時，才回傳 SELF。
5. 當所有相關子 Agent 都已回覆、或無需再派單時，回傳 FINISH。

只能回傳以下之一的值：{agent_names}""".format(
    agent_descriptions="\n".join(
        f"- {name}：{desc}" for name, desc in AGENT_DESCRIPTIONS.items()
    ),
    agent_names=", ".join(list(AGENT_DESCRIPTIONS.keys()) + ["SELF", "FINISH"]),
)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
class SupervisorState(MessagesState):
    """Extends MessagesState with a routing decision field."""
    next: str


# ---------------------------------------------------------------------------
# Routing decision schema (for structured output)
# ---------------------------------------------------------------------------
class RouteDecision(BaseModel):
    """Supervisor's routing decision."""
    next: AgentName


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------
def build_supervisor_graph(
    model: str = "gpt-4o-mini",
    model_provider: str = "openai",
    checkpointer: Any = None,
):
    """Build and compile the supervisor multi-agent StateGraph.

    Args:
        model: LLM model name for both supervisor and sub-agents.
        model_provider: LLM provider (e.g. "openai", "anthropic").
        checkpointer: LangGraph checkpointer for session memory.
                      Defaults to InMemorySaver if not provided.

    Returns:
        A compiled LangGraph StateGraph ready to invoke.
    """
    from core.subagents.math_agent import math_agent
    from core.subagents.news_agent import create_news_agent
    from core.subagents.weather_agent import create_weather_agent

    # ------------------------------------------------------------------
    # 1. Sub-agents: compiled graphs that accept {"messages": ...} (full context)
    # ------------------------------------------------------------------
    sub_agents = {
        "news_agent": create_news_agent(),
        "weather_agent": create_weather_agent(),
        "math_agent": math_agent,
    }

    # ------------------------------------------------------------------
    # 2. Supervisor node (LLM router with structured output)
    #    When decision is SELF, the supervisor answers directly without
    #    delegating to a sub-agent, acting as a general-purpose assistant.
    # ------------------------------------------------------------------
    router_llm = init_chat_model(
        model=model, model_provider=model_provider
    ).with_structured_output(RouteDecision)

    general_llm = init_chat_model(model=model, model_provider=model_provider)

    def supervisor_node(state: SupervisorState) -> dict:
        """Route to a sub-agent, or answer directly when SELF is chosen."""
        messages = [{"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT}] + state[
            "messages"
        ]
        decision: RouteDecision = router_llm.invoke(messages)
        logger.info("Supervisor routed to: %s", decision.next)

        if decision.next == "SELF":
            response = general_llm.invoke(state["messages"])
            return {
                "messages": [AIMessage(content=response.content, name="supervisor")],
                "next": "FINISH",
            }

        # If FINISH, check if we need to consolidate multiple sub-agent responses
        if decision.next == "FINISH":
            # Count sub-agent responses in the conversation
            sub_agent_names = set(AGENT_DESCRIPTIONS.keys())
            sub_agent_responses = [
                msg for msg in state["messages"]
                if isinstance(msg, AIMessage) and hasattr(msg, "name") and msg.name in sub_agent_names
            ]
            
            # Find the original user query (first HumanMessage)
            user_query = ""
            for msg in state["messages"]:
                if isinstance(msg, HumanMessage):
                    user_query = msg.content if hasattr(msg, "content") else str(msg)
                    break
            
            # If multiple sub-agents responded, consolidate them into one response
            if len(sub_agent_responses) >= 2:
                consolidation_prompt = f"""使用者問了：{user_query}

以下是各個專業子 Agent 的回覆：
{chr(10).join(f'- {msg.name}: {msg.content}' for msg in sub_agent_responses)}

請將以上回覆整理成一段完整、流暢的回答，直接回覆給使用者。不要重複「以下是...」這種說明，直接給出整合後的內容。"""
                consolidated = general_llm.invoke([
                    {"role": "user", "content": consolidation_prompt}
                ])
                return {
                    "messages": [AIMessage(content=consolidated.content, name="supervisor")],
                    "next": "FINISH",
                }
            # If only one or no sub-agent response, let the last response be the final answer
            return {"next": "FINISH"}

        return {"next": decision.next}

    # ------------------------------------------------------------------
    # 3. Sub-agent nodes
    # ------------------------------------------------------------------
    def make_agent_node(agent_graph, agent_name: str):
        """Wrap a sub-agent graph into a StateGraph node function."""

        def node(state: SupervisorState) -> dict:
            # Only pass the messages, not the supervisor's routing state
            # Only pass the messages, not the supervisor's routing state
            # Only pass the messages, not the supervisor's routing state
            result = agent_graph.invoke({"messages": state["messages"]})
            last_msg = result["messages"][-1]
            # Tag the message with the agent's name for traceability
            # Tag the message with the agent's name for traceability
            response = AIMessage(
                content=last_msg.content,
                name=agent_name,
            )
            logger.info("%s responded: %.80s...", agent_name, last_msg.content)
            return {"messages": [response]}

        node.__name__ = agent_name
        return node

    # ------------------------------------------------------------------
    # 4. Assemble the StateGraph
    # ------------------------------------------------------------------
    builder = StateGraph(SupervisorState)

    # Add supervisor node
    builder.add_node("supervisor", supervisor_node)

    # Add sub-agent nodes
    for name, agent in sub_agents.items():
        builder.add_node(name, make_agent_node(agent, name))

    # Entry point → supervisor
    builder.add_edge(START, "supervisor")

    # Supervisor conditionally routes to a sub-agent or END
    def route_after_supervisor(state: SupervisorState) -> str:
        next_node = state.get("next", "FINISH")
        return END if next_node == "FINISH" else next_node

    builder.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {**{name: name for name in sub_agents}, END: END},  # SELF is handled inside supervisor_node, so no edge needed
    )

    # Every sub-agent returns to supervisor after completing its task
    for name in sub_agents:
        builder.add_edge(name, "supervisor")

    # ------------------------------------------------------------------
    # 5. Compile with checkpointer
    # ------------------------------------------------------------------
    cp = checkpointer if checkpointer is not None else InMemorySaver()
    return builder.compile(checkpointer=cp)
