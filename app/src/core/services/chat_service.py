from core.models.agent import Agent
from utils.logger import setup_logger

logger = setup_logger("src.core.services.chat_service")

class ChatService:
    def __init__(self):
        pass

    async def process_message(self, message: str, model: str, model_provider: str, session_id: str):
        try:
            agent = Agent(model=model, model_provider=model_provider)
            response = agent.run(message)
            logger.info(f"Chat response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise e
