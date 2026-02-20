from langchain.agents import create_agent
from langchain.tools import tool

from core.tools.calculator import add, subtract, multiply, divide
from core.prompts import load_prompt

MATH_AGENT_SYSTEM_PROMPT = load_prompt("math")

math_agent = create_agent(
    model="anthropic:claude-haiku-4-5-20251001",
    tools=[add, subtract, multiply, divide],
    system_prompt=MATH_AGENT_SYSTEM_PROMPT,
)

@tool("math", description="Call the math agent to calculate the result")
def call_math_agent(query: str):
    result = math_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content