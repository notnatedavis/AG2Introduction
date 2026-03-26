# workflows/team_workflow.py

# ----- Imports -----

import autogen
import threading
import time
from autogen import register_function, GroupChat, GroupChatManager
from agents.coding_agent import CodingAgent
from agents.tester_agent import TesterAgent
from agents.documenter_agent import DocumenterAgent
from agents.reviewer_agent import ReviewerAgent
from agents.tool_executor_agent import ToolExecutorAgent
from agents.manager_agent import ManagerAgent
from tools.file_tools import list_files, read_file, write_file, search_files, grep, get_project_structure
from tools.code_execution import execute_command
from tools.tool_security import require_approval
from typing import Optional, Any, List, Dict

# ----- Helper Functions -----

def run_group_chat(
    agents: List[autogen.Agent],
    manager: autogen.GroupChatManager,
    initial_message: str,
    message_queue: Optional[Any] = None,
    user_input_queue: Optional[Any] = None,
    logger: Optional[Any] = None,
) -> List[Dict] :
    # Run a group chat with the given agents and manager
    # Returns the list of messages in the conversation
    # The user proxy is assumed to be part of agents

    user_proxy = next((a for a in agents if a.name == "user"), None)
    if not user_proxy :
        raise ValueError("User proxy not found in agents list")

    # Override receive methods to capture messages (if not already done)
    # This is already handled outside, but we ensure it's done once.
    # The conversation will be recorded via the message queue and logger.
    user_proxy.initiate_chat(manager, message=initial_message, groupchat=GroupChat(agents=agents, messages=[], max_round=50))
    return manager.groupchat.messages

def get_final_keyword(messages: List[Dict]) -> Optional[str]:
    # extract the completion keyword from the last message of the group chat
    if not messages :
        return None
    last_msg = messages[-1]
    content = last_msg.get('content', '')
    keywords = ["CODE_COMPLETE", "TESTS_PASSED", "TESTS_FAILED", "REVIEW_APPROVED", "REVIEW_REJECTED", "DOC_COMPLETE"]
    for kw in keywords :
        if kw in content :
            return kw
    return None

# ----- Main -----

# run the team workflow with a timeout
def run_team_workflow( 
    task: str,
    message_queue: Optional[Any] = None,
    user_input_queue: Optional[Any] = None,
    timeout_seconds: int = 300,  # 5 min default
    logger: Optional[Any] = None,   # StructuredLogger instance
) -> None :
    # args :
    #     task: user's request
    #     message_queue: Queue for sending messages to the frontend (optional)
    #     user_input_queue: Queue for receiving user input from the frontend (optional)
    #     timeout_seconds: Maximum allowed execution time (seconds)
    
    # Instantiate agents
    coder = CodingAgent().get_agent()
    tester = TesterAgent().get_agent()
    documenter = DocumenterAgent().get_agent()
    reviewer = ReviewerAgent().get_agent()
    executor = ToolExecutorAgent().get_agent()
    manager = ManagerAgent().get_agent()

    # log system prompts if logger is provided
    if logger :
        # assuming agents have a `system_message` attribute (should via AG2)
        for agent in [coder, tester, documenter, reviewer, executor, manager] : 
            # get system message from the agent's internal config
            sys_msg = getattr(agent, 'system_message', None)
            if sys_msg :
                logger.log_system_prompt(agent.name, sys_msg)
        
        # also log user proxy's role? It doesn't have a system message, but can log its description
        logger.log_system_prompt("user", "Human user interacting via proxy agent.")

    # define a custom input function that reads from the user_input_queue
    def get_human_input(prompt) :
        if user_input_queue :
            # optionally send a notification to the frontend that input is needed
            if message_queue :
                msg = {
                    'sender': 'system',
                    'content': f'[Waiting for your input] {prompt}',
                    'timestamp': time.time()
                }
                message_queue.put(msg)
            # Block until user replies
            return user_input_queue.get()
        else :
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

    # --- tool descriptions w/ permission hints ---
    tool_descriptions = {
        list_files : "[READ] List files in a directory.",
        read_file : "[READ] Read the content of a file.",
        write_file : "[WRITE] Write content to a file (overwrites!).",
        search_files : "[READ] Find files matching a pattern.",
        grep : "[READ] Search inside files for a pattern.",
        get_project_structure: "[READ] Get a tree view of the workspace.",
        execute_command : "[EXECUTE] Run a shell command in the workspace. **Requires approval**."
    }

    # define dangerous tools that need approval
    DANGEROUS_TOOLS = {"write_file", "write_html_file", "execute_command"}

    # --- Wrap tools with logging and optional approval ---
    def wrap_tool(tool_func, tool_name):
        # Apply approval wrapper first if tool is dangerous
        if tool_name in DANGEROUS_TOOLS:
            tool_func = require_approval(
                tool_func,
                tool_name,
                user_input_queue=user_input_queue,
                message_queue=message_queue,
                read_only_by_default=True
            )
        # Then wrap with logging
        def wrapper(*args, **kwargs):
            if logger:
                # Log tool call
                logger.log_tool_call(executor.name, tool_name, {"args": args, "kwargs": kwargs})
            try:
                result = tool_func(*args, **kwargs)
            except Exception as e:
                result = f"Error: {str(e)}"
                if logger:
                    logger.log_tool_output(executor.name, tool_name, result)
                raise
            if logger:
                logger.log_tool_output(executor.name, tool_name, str(result))
            return result
        return wrapper

    # Register wrapped tools with the executor
    for tool_func in [list_files, read_file, write_file, search_files, grep, get_project_structure, execute_command]:
        tool_name = tool_func.__name__
        wrapped = wrap_tool(tool_func, tool_name)
        register_function(
            wrapped,
            caller=manager, # any agent can call
            executor=executor,
            name=tool_name,
            description=tool_func.__doc__ or ""
        )

    # Share the function_map with all agents so they can call the tools
    for agent in all_agents :
        if hasattr(agent, 'update_function_map') :
            agent.update_function_map(executor.function_map)

    # Override receive methods for all agents to capture messages for the frontend
    if message_queue or logger :
        for agent in all_agents :
            original_receive = agent.receive

            def make_wrapper(orig_recv, agent_name) :
                def receive_wrapper(message, sender, request_reply=None, silent=False) :
                    # Extract content (handle both string and dict messages)
                    if isinstance(message, str) :
                        content = message
                        token_usage = None
                    else :
                        content = message.get('content', '') if isinstance(message, dict) else str(message)
                        token_usage = message.get('usage', None) if isinstance(message, dict) else None

                    # log to message queue
                    if message_queue :
                        msg = {
                            'sender': sender.name if sender else 'system',
                            'content': content,
                            'timestamp': time.time()
                        }
                        message_queue.put(msg)

                    # log to structured logger
                    if logger : 
                        logger.log_message(
                            sender.name if sender else 'system',
                            content,
                            metadata={'agent': agent_name} if token_usage else None
                        )
                        if token_usage :
                            logger.log_token_usage(agent_name, token_usage)

                    return orig_recv(message, sender, request_reply, silent)
                return receive_wrapper

            agent.receive = make_wrapper(original_receive, agent.name)

    # --- State Machine ---
    # Define the phases and the agents involved in each
    phases = {
        "CODE": {
            "agents": [coder, executor, user_proxy],
            "initial_message": f"Task: {task}\nPlease write the necessary code. When done, output 'CODE_COMPLETE'."
        },
        "TEST": {
            "agents": [tester, executor, user_proxy],
            "initial_message": f"Task: {task}\nNow test the code. Output 'TESTS_PASSED' if all tests pass, else 'TESTS_FAILED'."
        },
        "REVIEW": {
            "agents": [reviewer, executor, user_proxy],
            "initial_message": f"Task: {task}\nReview the code. Output 'REVIEW_APPROVED' if it's good, else 'REVIEW_REJECTED'."
        },
        "DOCUMENT": {
            "agents": [documenter, executor, user_proxy],
            "initial_message": f"Task: {task}\nUpdate documentation. Output 'DOC_COMPLETE' when done."
        }
    }

    # Run the state machine
    current_state = "CODE"
    while current_state not in ("FINISH", "FAIL"):
        phase = phases.get(current_state)
        if not phase:
            raise ValueError(f"Unknown state: {current_state}")

        # Create group chat manager for this phase
        groupchat = GroupChat(
            agents=phase["agents"],
            messages=[],
            max_round=50,
            speaker_selection_method="auto"
        )
        manager = GroupChatManager(
            name=f"{current_state.lower()}_manager",
            groupchat=groupchat,
            llm_config=coder.llm_config  # reuse LLM config from any agent
        )

        # Run the group chat with a timeout
        result_holder = {'exception': None, 'messages': None}
        def run_chat() :
            try :
                user_proxy.initiate_chat(manager, message=phase["initial_message"], groupchat=groupchat)
                result_holder['messages'] = groupchat.messages
            except Exception as e :
                result_holder['exception'] = e

        chat_thread = threading.Thread(target=run_chat)
        chat_thread.daemon = True
        chat_thread.start()
        chat_thread.join(timeout_seconds)

        if chat_thread.is_alive() :
            raise TimeoutError(f"Workflow timed out after {timeout_seconds} seconds in state {current_state}")
        if result_holder['exception'] :
            raise result_holder['exception']

        # Determine next state based on the final keyword
        final_keyword = get_final_keyword(result_holder['messages'])
        
        if current_state == "CODE" :
            if final_keyword == "CODE_COMPLETE" :
                current_state = "TEST"
            else :
                current_state = "FAIL"
        elif current_state == "TEST" :
            if final_keyword == "TESTS_PASSED" :
                current_state = "REVIEW"
            elif final_keyword == "TESTS_FAILED" : 
                current_state = "CODE"   # loop back to fix
            else :
                current_state = "FAIL"
        elif current_state == "REVIEW" :
            if final_keyword == "REVIEW_APPROVED" :
                current_state = "DOCUMENT"
            elif final_keyword == "REVIEW_REJECTED" :
                current_state = "CODE"   # loop back to fix
            else:
                current_state = "FAIL"
        elif current_state == "DOCUMENT" :
            if final_keyword == "DOC_COMPLETE" :
                current_state = "FINISH"
            else :
                current_state = "FAIL"
        else :
            current_state = "FAIL"

    # If we reached FINISH, we're done. If FAIL, raise an error (optional)
    if current_state == "FAIL" :
        raise RuntimeError("Workflow ended in FAIL state.")

    # Close logger if provided
    if logger :
        logger.close()