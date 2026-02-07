from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage

store = {}

class CustomChatMessageHistory(ChatMessageHistory):
    def add_message(self, message):
        """Override to handle different message formats"""
        if isinstance(message, dict):
            # Handle Claude format
            if 'text' in message:
                self.messages.append(AIMessage(content=message['text']))
            # Handle standard format
            elif 'content' in message:
                if message.get('role') == 'assistant':
                    self.messages.append(AIMessage(content=message['content']))
                else:
                    self.messages.append(HumanMessage(content=message['content']))
        else:
            # Handle LangChain message objects
            self.messages.append(message)

# 未來可以搭配 Redis 和 MongoDB 等資料庫來實作，快取和持久化
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = CustomChatMessageHistory()
    return store[session_id]