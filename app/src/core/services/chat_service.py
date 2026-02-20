from core.agent import Agent
from core.memory.short_term import get_checkpointer
from utils.logger import setup_logger

logger = setup_logger("src.core.services.chat_service")

class ChatService:
    def __init__(self):
        pass

    async def process_message(self, message: str, model: str, model_provider: str, session_id: str):
        try:
            checkpointer = get_checkpointer()
            agent = Agent(model=model, model_provider=model_provider, checkpointer=checkpointer)
            response = agent.run(message, session_id=session_id)
            logger.info(f"Chat response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise e
