#   agents/tool_executor_agent.py

# ----- Imports -----
from .base_agent import create_user_proxy

# ----- Main -----
class ToolExecutorAgent :
    # Agent that executes file system and shell commands, but only after user approval
    
    def __init__(self, name: str = "tool_executor") :
        self.agent = create_user_proxy(
            name=name,
            human_input_mode="NEVER",        # we will feed user replies via the workflow
            code_execution_config=False,     # we use function calls instead of direct code exec
            max_consecutive_auto_reply=1     # don't auto-reply to itself
        )
    
    def get_agent(self) :
        return self.agent