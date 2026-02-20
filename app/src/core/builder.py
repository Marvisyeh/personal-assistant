"""Build LangGraph agent from model, tools, middleware, checkpointer."""
from typing import Any

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from core.middleware import trim_messages


def build_agent(
    model: str = "gpt-4o-mini",
    model_provider: str = "openai",
    tools: list[Any] | None = None,
    middleware: list[Any] | None = None,
    checkpointer: Any = None,
    system_prompt: str = "You are a helpful assistant. Be concise and accurate.",
):
    """Create and return a compiled LangGraph agent."""
    from langgraph.checkpoint.memory import InMemorySaver

    chat_model = init_chat_model(model=model, model_provider=model_provider)
    middleware_list = middleware if middleware is not None else [trim_messages]
    cp = checkpointer if checkpointer is not None else InMemorySaver()
    return create_agent(
        chat_model,
        tools=tools or [],
        middleware=middleware_list,
        checkpointer=cp,
        system_prompt=system_prompt,
    )
