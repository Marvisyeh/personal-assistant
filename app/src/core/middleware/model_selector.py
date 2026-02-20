from langchain.agents.middleware import (
  wrap_model_call, 
  ModelRequest, 
  ModelResponse
)
from langchain.chat_models import init_chat_model

from utils.logger import setup_logger

logger = setup_logger("src.core.models.model_selector")

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Choose model based on conversation complexity."""
    message_count = len(request.state["messages"])

    if message_count > 10:
        # Use an advanced model for longer conversations
        model = init_chat_model(model="gpt-4o", model_provider="openai")
    else:
        model = init_chat_model(model="gpt-4o-mini", model_provider="openai")

    return handler(request.override(model=model))