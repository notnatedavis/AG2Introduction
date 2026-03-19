#   workflows/webpage_workflow.py
#   Complete workflow for generating a webpage

# ----- Imports -----
import autogen
from autogen import register_function
from agents.webpage_agent import WebpageAgent
from agents.executor_agent import ExecutorAgent
from tools.file_tools import write_html_file
from config.settings import TERMINATION_KEYWORD

# ----- Helper Functions -----
def run_webpage_workflow(task: str = None) :
    # Execute the webpage generation workflow
    # Create agents
    designer = WebpageAgent().get_agent()
    executor = ExecutorAgent().get_agent()
    
    # Register the tool with both agents
    register_function(
        write_html_file,
        caller=designer,
        executor=executor,
        name="write_html_file",
        description="Write HTML content to a file and open it in the browser. Input should be a string containing the full HTML code."
    )
    
    # Define task
    if task is None:
        task = "Create a beautiful personal portfolio webpage for a fictional web developer named 'Alex'. Include a header, about section, and project cards with hover effects. Use modern CSS (flexbox/grid)."
    
    # Set termination condition
    executor.is_termination_msg = lambda x: x.get("content", "").rstrip().endswith(TERMINATION_KEYWORD)
    
    # Initiate conversation
    executor.initiate_chat(designer, message=task)