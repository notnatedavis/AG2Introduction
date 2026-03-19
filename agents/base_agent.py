#   agents/base_agent.py
#   Shared base classes or helper functions for agent creation

# ----- Imports -----
import autogen
from autogen import AssistantAgent, UserProxyAgent
from config.llm_config import get_llm_config

# ----- Helper Functions -----
def create_assistant_agent(name: str, system_message: str, **kwargs) -> AssistantAgent :
    # factory to create an AssistantAgent with default LLM config
    llm_config = get_llm_config()
    return AssistantAgent(
        name=name,
        llm_config=llm_config,
        system_message=system_message,
        **kwargs
    )

def create_user_proxy(name: str = "user_proxy", 
                      human_input_mode: str = "NEVER",
                      max_consecutive_auto_reply: int = 10,
                      code_execution_config: dict = None,
                      **kwargs) -> UserProxyAgent:
    # factory to create a UserProxyAgent with sensible defaults
    if code_execution_config is None :
        code_execution_config = {"work_dir": "workspace", "use_docker": False}
    return UserProxyAgent(
        name=name,
        human_input_mode=human_input_mode,
        max_consecutive_auto_reply=max_consecutive_auto_reply,
        code_execution_config=code_execution_config,
        **kwargs
    )