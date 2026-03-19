#   workflows/coding_workflow.py
#   Simple coding workflow

# ----- Imports -----
from agents.coding_agent import CodingAgent
from agents.executor_agent import ExecutorAgent
from config.settings import TERMINATION_KEYWORD

# ----- Helper Functions -----
def run_coding_workflow(task: str) :
    # Execute a coding task with a coder and executor
    coder = CodingAgent().get_agent()
    executor = ExecutorAgent().get_agent()
    
    executor.is_termination_msg = lambda x: x.get("content", "").rstrip().endswith(TERMINATION_KEYWORD)
    
    executor.initiate_chat(coder, message=task)