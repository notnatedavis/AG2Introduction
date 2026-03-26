#   agents/reviewer_agent.py

# ----- Imports -----
from .base_agent import create_assistant_agent

# ----- Main -----
class ReviewerAgent :
    def __init__(self, name: str = "reviewer") :
        system_message = (
            "You are a code reviewer. Analyse code quality, suggest improvements, and point out potential bugs.\n"
            "You do NOT write files. Use `read_file` and `grep` to examine code.\n"
            "Provide constructive feedback in the chat.\n"
            "After review, output 'REVIEW_APPROVED' if the code is approved, or 'REVIEW_REJECTED' if changes are needed.\n"
            "Reply 'TERMINATE' when your review is complete."
        )
        self.agent = create_assistant_agent(name, system_message)
    
    def get_agent(self) :
        return self.agent