#   tools/code_execution.py
#   Utilities for safely executing code (if needed)

# ----- Imports -----
import subprocess
import tempfile
import os
from config.settings import WORK_DIR

# ----- Helper Functions -----
def execute_python_code(code: str) -> str :
    # Execute Python code in a temporary file and return stdout
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f :
        f.write(code)
        temp_file = f.name
    try :
        result = subprocess.run(['python', temp_file], capture_output=True, text=True, timeout=10)
        output = result.stdout + result.stderr
    except Exception as e :
        output = str(e)
    finally :
        os.unlink(temp_file)
    return output

def execute_command(command: str) -> str :
    # Run a shell command inside the workspace directory and return output
    try :
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORK_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return output if output else "(no output)"
    except subprocess.TimeoutExpired :
        return "Command timed out after 30 seconds."
    except Exception as e :
        return f"Error executing command: {str(e)}"