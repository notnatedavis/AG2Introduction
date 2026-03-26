#   agents/tester_agent.py

# ----- Imports -----
from .base_agent import create_assistant_agent

# ----- Main -----
class TesterAgent :
    def __init__(self, name: str = "tester") :
        system_message = (
            "You are a QA engineer. First, understand the testing framework by reading config files and existing tests.\n"
            "Propose test code, ask for user permission, then write with `write_file`. After writing, you may run tests using `execute_command` and analyse output.\n"
            "Report failures and coordinate with the Coder if needed.\n"
            "After testing, output 'TESTS_PASSED' if all tests pass, or 'TESTS_FAILED' if any test fails.\n"
            "Reply 'TERMINATE' when all tests pass or the task is complete."
        )
        self.agent = create_assistant_agent(name, system_message)
    
    def get_agent(self) :
        return self.agent