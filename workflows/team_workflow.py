# workflows/team_workflow.py

# ----- Imports -----
import time
import autogen
from autogen import register_function, GroupChat
from agents.coding_agent import CodingAgent
from agents.tester_agent import TesterAgent
from agents.documenter_agent import DocumenterAgent
from agents.reviewer_agent import ReviewerAgent
from agents.tool_executor_agent import ToolExecutorAgent
from agents.manager_agent import ManagerAgent
from tools.file_tools import list_files, read_file, write_file, search_files, grep, get_project_structure
from tools.code_execution import execute_command

# ----- Main -----
def run_team_workflow(task: str, message_queue=None, user_input_queue=None):
    """
    Run the team workflow.

    - message_queue: queue for sending messages to the frontend (if any)
    - user_input_queue: queue for receiving user input from the frontend
    """
    # Instantiate agents
    coder = CodingAgent().get_agent()
    tester = TesterAgent().get_agent()
    documenter = DocumenterAgent().get_agent()
    reviewer = ReviewerAgent().get_agent()
    executor = ToolExecutorAgent().get_agent()
    manager = ManagerAgent().get_agent()

    # Define a custom input function that reads from the user_input_queue
    def get_human_input(prompt):
        if user_input_queue:
            # Optionally send a notification to the frontend that input is needed
            if message_queue:
                msg = {
                    'sender': 'system',
                    'content': f'[Waiting for your input] {prompt}',
                    'timestamp': time.time()
                }
                message_queue.put(msg)
            # Block until user replies
            return user_input_queue.get()
        else:
            # Fallback to console input (for testing without frontend)
            return input(prompt)

    # Create a dedicated user proxy agent that will interact with the human
    user_proxy = autogen.UserProxyAgent(
        name="user",
        human_input_mode="ALWAYS",
        code_execution_config=False,
        get_human_input=get_human_input
    )

    # List of all agents (including user_proxy) that we need to wrap for message capture
    all_agents = [coder, tester, documenter, reviewer, executor, manager, user_proxy]

    # Register all tools with the executor (caller = any agent, executor = executor)
    for tool in [list_files, read_file, write_file, search_files, grep, get_project_structure, execute_command]:
        register_function(
            tool,
            caller=manager,      # placeholder – the actual caller will be any agent that uses the tool
            executor=executor,
            name=tool.__name__,
            description=tool.__doc__ or ""
        )

    # Share the function_map with all agents so they can call the tools
    for agent in all_agents:
        if hasattr(agent, 'update_function_map'):
            agent.update_function_map(executor.function_map)

    # Override receive methods for all agents to capture messages for the frontend
    if message_queue:
        for agent in all_agents:
            original_receive = agent.receive

            def make_wrapper(orig_recv):
                def receive_wrapper(message, sender, request_reply=None, silent=False):
                    # Extract content (handle both string and dict messages)
                    if isinstance(message, str):
                        content = message
                    else:
                        content = message.get('content', '') if isinstance(message, dict) else str(message)

                    msg = {
                        'sender': sender.name if sender else 'system',
                        'content': content,
                        'timestamp': time.time()
                    }
                    message_queue.put(msg)
                    return orig_recv(message, sender, request_reply, silent)
                return receive_wrapper

            agent.receive = make_wrapper(original_receive)

    # Create GroupChat
    groupchat = GroupChat(
        agents=all_agents,
        messages=[],
        max_round=50,
        speaker_selection_method="auto"
    )

    # Start the chat
    user_proxy.initiate_chat(manager, message=task, groupchat=groupchat)