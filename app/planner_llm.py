# planner_llm.py - LangChain LLM Task Planner

from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import ShellTool
import os

# Optional: Load from .env
from dotenv import load_dotenv
load_dotenv()

# ========== Config ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ========== Define Tools ==========
# Allow shell execution simulation (or use restricted commands only)
shell_tool = ShellTool()

tools = [
    Tool(
        name="Shell Executor",
        func=shell_tool.run,
        description="Executes shell commands for deployment or installation."
    )
]

# ========== LLM Agent ==========
llm = ChatOpenAI(
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

agent_executor = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# ========== Task Handler ==========
def handle_natural_task(task_nl: str) -> str:
    """
    Convert natural language task into structured shell command
    and execute via tools.
    """
    try:
        result = agent_executor.run(task_nl)
        return result
    except Exception as e:
        return f"[Error] Failed to process task: {str(e)}"

# ========== Test Run ==========
if __name__ == "__main__":
    test_input = "Install nginx and start the service on Ubuntu"
    output = handle_natural_task(test_input)
    print("\n=== Agent Output ===")
    print(output)
