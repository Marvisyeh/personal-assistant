from pathlib import Path

from langchain.agents import create_agent
from langchain.tools import tool

from core.common.prompts import load_prompt
from core.common.tools.calculator import add, subtract, multiply, divide

_PROMPTS_DIR = Path(__file__).resolve().parent

MATH_AGENT_SYSTEM_PROMPT = load_prompt("math", base_dir=_PROMPTS_DIR)

math_agent = create_agent(
    model="anthropic:claude-haiku-4-5-20251001",
    tools=[add, subtract, multiply, divide],
    system_prompt=MATH_AGENT_SYSTEM_PROMPT,
)


@tool("math", description="Call the math agent to calculate the result")
def call_math_agent(query: str):
    result = math_agent.invoke({"messages": [{"role": "user", "content": query}]})
    content = result["messages"][-1].content
    if isinstance(content, list):
        content = "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        ).strip()
    return content or "無法計算結果"
