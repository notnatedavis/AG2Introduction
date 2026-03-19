#   agents/manager_agent.py

# ----- Imports -----
from autogen import GroupChatManager
from config.llm_config import get_llm_config

# ----- Main -----
class ManagerAgent :
    # orchestrates the team conversation
    
    def __init__(self, name: str = "manager") :
        llm_config = get_llm_config()
        self.agent = GroupChatManager(
            name=name,
            llm_config=llm_config,
            system_message=(
                "You are a project manager. Your team consists of Coder, Tester, Documenter, "
                "Reviewer, and ToolExecutor. The user is also part of the team. "
                "Your goal is to efficiently complete the user's request. "
                "Break it down, decide who should speak next, and ensure collaboration. "
                "When the task is fully done, reply with 'TERMINATE'."
            )
        )
    
    def get_agent(self) :
        return self.agent