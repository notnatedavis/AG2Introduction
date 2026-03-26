#   tools/tool_security.py
#   Security wrappers for dangerous tools

# ----- Imports -----

import time
from typing import Any, Callable, Dict, List, Optional, Set

# constants
# list of read‑only shell commands (safe to execute without approval)
READ_ONLY_COMMANDS: Set[str] = {
    "ls", "cat", "head", "tail", "grep", "find", "echo", "pwd", "which",
    "file", "stat", "du", "df", "ps", "top", "htop", "whoami", "id",
    "date", "cal", "env", "printenv"
}

# ----- Helper Functions -----

def is_read_only_command(command: str) -> bool :
    # Check if a shell command is considered read‑only (safe)
    cmd_parts = command.strip().split()
    if not cmd_parts :
        return False
    base_cmd = cmd_parts[0]
    return base_cmd in READ_ONLY_COMMANDS

# ----- Main -----


def require_approval(
    tool_func: Callable,
    tool_name: str,
    user_input_queue: Optional[Any] = None,
    message_queue: Optional[Any] = None,
    read_only_by_default: bool = True
) -> Callable :
    # Wrap a dangerous tool to require human approval before execution.

    # args :
    #     tool_func: The original tool function
    #     tool_name: Name of the tool (used in prompts)
    #     user_input_queue: Queue to receive user input (approval/rejection).
    #     message_queue: Queue to send notifications to the frontend.
    #     read_only_by_default: If True, execute_command will be approved only if command is read‑only; otherwise approval is mandatory

    # Returns:
    #     Wrapped function that asks for approval

    def wrapper(*args, **kwargs) :
        # For execute_command, we can do a read‑only check
        if tool_name == "execute_command" and read_only_by_default :
            # get the command string (assumed to be first argument)
            command = args[0] if args else kwargs.get('command', '')
            if is_read_only_command(command) :
                # Safe command – execute immediately
                return tool_func(*args, **kwargs)

        # for all other dangerous tools, always ask for approval
        if user_input_queue is None :
            # No approval mechanism available – raise error (or fallback)
            raise RuntimeError(f"Tool '{tool_name}' requires approval but no user_input_queue provided.")

        # prepare approval prompt
        prompt = f"⚠️ Tool '{tool_name}' wants to execute:\n"
        if args :
            prompt += f"Arguments: {args}\n"
        if kwargs :
            prompt += f"Keyword arguments: {kwargs}\n"
        prompt += "Approve? (y/n): "

        # Notify frontend that input is needed
        if message_queue :
            msg = {
                'sender': 'system',
                'content': f'[Approval needed] {prompt}',
                'timestamp': time.time()
            }
            message_queue.put(msg)

        # Wait for user response (blocking)
        try :
            response = user_input_queue.get()
        except Exception :
            # If queue closed, assume denial
            raise RuntimeError(f"Tool '{tool_name}' approval timed out or queue closed.")

        if response.lower().strip() in ('y', 'yes', 'approve', '1'):
            # Approved – execute original tool
            return tool_func(*args, **kwargs)
        else :
            # Denied – raise exception or return denial message
            raise PermissionError(f"User denied execution of tool '{tool_name}'.")

    # Preserve original function attributes
    wrapper.__name__ = tool_func.__name__
    wrapper.__doc__ = tool_func.__doc__
    return wrapper