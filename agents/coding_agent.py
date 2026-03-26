#   agents/coding_agent.py
#   Agent specialized in writing code

# ----- Imports -----
from .base_agent import create_assistant_agent

# ----- Main -----
class CodingAgent :
    def __init__(self, name: str = "coder") :
        system_message = (
            "You are an expert software engineer. Before writing any code, you MUST understand the project context:\n"
            "- Use `get_project_structure` to see the layout\n"
            "- Use `read_file` to examine relevant files\n"
            "Then propose your changes clearly and ask the user for permission. Only after approval call `write_file`.\n"
            "Follow the project's coding style. When you have finished coding and the code is ready, output 'CODE_COMPLETE'.\n"
            "Reply 'TERMINATE' when the task is complete."
        )
        self.agent = create_assistant_agent(name, system_message)
    
    def get_agent(self):
        return self.agent