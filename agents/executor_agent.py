#   agents/executor_agent.py
#   Agent responsible for executing code and managing file operations

# ----- Imports -----
from .base_agent import create_user_proxy
from tools.code_execution import execute_python_code
from tools.file_tools import write_file

# ----- Main -----
class ExecutorAgent :
    # A proxy agent that can execute code and use file tools
    
    def __init__(self, name: str = "executor") :
        self.agent = create_user_proxy(
            name=name,
            human_input_mode="NEVER",
            code_execution_config={"work_dir": "coding", "use_docker": False}
        )
        # Register tools with this agent
        self._register_tools()
    
    def _register_tools(self) :
        # This would normally use autogen's register_function,
        # but registration is handled in the workflow where both caller and executor are known.
        pass
    
    def get_agent(self) :
        return self.agent