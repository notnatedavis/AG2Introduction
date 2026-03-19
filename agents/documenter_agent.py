#   agents/documenter_agent.py

# ----- Imports -----
from .base_agent import create_assistant_agent

# ----- Main -----
class DocumenterAgent :
    def __init__(self, name: str = "documenter") :
        system_message = (
            "You are a technical writer. Update README, inline docs, and API documentation as needed.\n"
            "Use `read_file` to understand current docs, propose changes, ask for permission, then `write_file`.\n"
            "Ensure documentation is clear and up‑to‑date.\n"
            "Reply 'TERMINATE' when documentation tasks are done."
        )
        self.agent = create_assistant_agent(name, system_message)
    
    def get_agent(self) :
        return self.agent