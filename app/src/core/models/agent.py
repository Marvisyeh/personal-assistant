from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import (
  ChatPromptTemplate,PromptTemplate, 
  SystemMessagePromptTemplate, HumanMessagePromptTemplate, 
  MessagesPlaceholder
)
from langchain_core.runnables.history import RunnableWithMessageHistory

from core.memory.memory_story import get_session_history
from core.tools.calculator import add, multiply, divide, subtract
from utils.logger import setup_logger

logger = setup_logger("src.core.models.agent")

class Agent:
    def __init__(self, model: str = "gpt-4o-mini", model_provider: str = "openai"):
        self.tools: list = []
        self.model = init_chat_model(model=model, model_provider=model_provider)
        self.chat_history = []

    def add_tool(self, tool):
        self.tools.append(tool)
    
    def add_tools(self, tools: list):
        self.tools.extend(tools)

    def run(self, message: str, session_id: str = "default"):
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate(
                prompt=PromptTemplate(input_variables=[], template='You are a helpful assistant')
            ),
            MessagesPlaceholder(variable_name='chat_history', optional=True),
            HumanMessagePromptTemplate(
                prompt=PromptTemplate(input_variables=['input'], template='{input}')
            ),
            MessagesPlaceholder(variable_name='agent_scratchpad')
        ])

        agent = create_tool_calling_agent(self.model, tools=self.tools, prompt=prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools)
        agent_with_chat_history = RunnableWithMessageHistory(
            agent_executor, 
            get_session_history,
            input_messages_key='input',
            history_messages_key='chat_history'
        )
        try:
          response = agent_with_chat_history.invoke(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
          )
          logger.info(f"Agent response for session {session_id}: {response}")
          # Extract the text content from the response
          if isinstance(response, dict) and 'output' in response:
              output = response['output']
              if isinstance(output, list) and len(output) > 0:
                  text_content = output[0].get('text', '')
                  logger.info(f"Extracted text content for session {session_id}: {text_content}")
                  return text_content
          # If we can't extract text content, return the response as is
          return str(response)
        except Exception as e:
          logger.error(f"Error processing message for session {session_id}: {e}")
          raise e


if __name__ == "__main__":
      # agent = Agent()
      # agent.add_tools([add, multiply, divide, subtract])
      # print(agent.run("Hi! I'm Paula, nice to meet you!"))
      # print(agent.run("What is 2 + 2?"))
      # print(agent.run("What is my name?"))  

    agent = Agent(model="claude-3-5-sonnet-20240620", model_provider="anthropic")
    agent.add_tools([add, multiply, divide, subtract])
    print(agent.run("Hi! I'm Paula, nice to meet you!"))
    print(agent.run("What is 2 + 2?"))
    print(agent.run("What is my name?"))
