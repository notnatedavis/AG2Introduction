#   agents/coding_agent.py
#   Agent specialized in writing code

# ----- Imports -----
from .base_agent import create_assistant_agent

# ----- Main -----
class CodingAgent :
    # A reusable coding agent that can generate code based on tasks."""
    
    def __init__(self, name: str = "coder"):
        system_message = (
            "You are an expert Python coder. Write clean, efficient code. "
            "When asked to implement something, provide the full code with comments. "
            "Reply 'TERMINATE' when the task is complete."
        )
        self.agent = create_assistant_agent(name, system_message)
    
    def get_agent(self) :
        return self.agent