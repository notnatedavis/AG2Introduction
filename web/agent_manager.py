#   web/agent_manager.py
#   Added detailed logging in message addition for debugging

# ----- Imports -----
import uuid
import threading
import queue
import time
import logging
from typing import Dict, Optional
from workflows import run_webpage_workflow, run_coding_workflow
from workflows.team_workflow import run_team_workflow
from agents.executor_agent import ExecutorAgent
from agents.webpage_agent import WebpageAgent
from agents.coding_agent import CodingAgent
import autogen
from autogen import register_function
from tools.file_tools import write_html_file
from utils.logging_utils import StructuredLogger

# constants
MAX_MESSAGES_PER_SESSION = 200
INACTIVITY_TIMEOUT_SECONDS = 120   # 2 minutes

# Setup logger
logger = logging.getLogger(__name__)

# ----- AgentSession Class -----
class AgentSession :
    # represents a running agent workflow session
    
    def __init__(self, session_id: str, workflow: str, task: str) :
        self.session_id = session_id
        self.workflow = workflow
        self.task = task
        self.status = "starting"  # starting, running, stopping, finished
        self.messages = []        # store all messages for history
        self.message_queue = queue.Queue()
        self.user_input_queue = queue.Queue()   # queue for receiving user replies from frontend
        self.thread = None
        self.stop_event = threading.Event()
        self.agents = {}          # store references to agents if needed
        self.logger = StructuredLogger(session_id)
        self.message_count = 0
        self.last_activity_time = time.time()
        self.stop_event = threading.Event()
        self.watchdog_thread = None

    def start(self) :
        # launch the workflow in a background thread + start watchdog
        self.thread = threading.Thread(target=self._run_workflow)
        self.thread.daemon = True
        self.thread.start()
        # start watchdog thread to monitor activity
        self.watchdog_thread = threading.Thread(target=self._watchdog)
        self.watchdog_thread.daemon = True
        self.watchdog_thread.start()
    
    def _run_workflow(self) :
        # execute the appropriate workflow with message capturing
        self.status = "running"
        try :
            if self.workflow == "webpage" :
                self._run_webpage_workflow()
            elif self.workflow == "coding" :
                self._run_coding_workflow()
            elif self.workflow == "team" :
                self._run_team_workflow()
            else :
                raise ValueError(f"Unknown workflow: {self.workflow}")
        except TimeoutError as e :
            self._add_message("system", f"Workflow timed out: {e}")
        except Exception as e :
            self._add_message("system", f"Error: {str(e)}")
        finally :
            self.status = "finished"
            self._add_message("system", "Workflow finished.")
            self.logger.close()

    def _run_webpage_workflow(self) : 
        # custom webpage workflow that captures messages
        # create agents
        designer = WebpageAgent().get_agent()
        executor = ExecutorAgent().get_agent()
        
        # register tool
        register_function(
            write_html_file,
            caller=designer,
            executor=executor,
            name="write_html_file",
            description="Write HTML content to a file and open it in the browser."
        )
        
        # override the receive methods to capture messages
        original_designer_receive = designer.receive
        original_executor_receive = executor.receive
        
        def designer_receive(message, sender, request_reply=None, silent=False) :
            self._add_message(sender.name, message)
            return original_designer_receive(message, sender, request_reply, silent)
        
        def executor_receive(message, sender, request_reply=None, silent=False) :
            self._add_message(sender.name, message)
            return original_executor_receive(message, sender, request_reply, silent)
        
        designer.receive = designer_receive
        executor.receive = executor_receive
        
        # start chat
        executor.initiate_chat(designer, message=self.task)
    
    def _run_coding_workflow(self) :
        # custom coding workflow that captures messages
        coder = CodingAgent().get_agent()
        executor = ExecutorAgent().get_agent()
        
        original_coder_receive = coder.receive
        original_executor_receive = executor.receive
        
        def coder_receive(message, sender, request_reply=None, silent=False) :
            self._add_message(sender.name, message)
            return original_coder_receive(message, sender, request_reply, silent)
        
        def executor_receive(message, sender, request_reply=None, silent=False) :
            self._add_message(sender.name, message)
            return original_executor_receive(message, sender, request_reply, silent)
        
        coder.receive = coder_receive
        executor.receive = executor_receive
        
        executor.initiate_chat(coder, message=self.task)
    
    def _run_team_workflow(self) :
        # team workflow using group chat – will capture messages via the workflow's own mechanism
        # We pass the message_queue and user_input_queue so the workflow can stream messages
        # and receive user input

        from workflows.team_workflow import run_team_workflow
        
        run_team_workflow(
            task=self.task,
            message_queue=self.message_queue,
            user_input_queue=self.user_input_queue,
            timeout_seconds=300,
            logger=self.logger
        )

        # Note: The workflow itself handles message capture via overriding receive,
        # so we don't need separate receive overrides here.
    
    def _add_message(self, sender: str, content: str, metadata: Optional[Dict] = None) :
        # store msg -> put in queue -> write to structured log
        # Ensure content is a string (handle dict responses)
        if isinstance(content, dict) :
            content = content.get('content', str(content))
        elif content is None :
            content = ''
        
        msg = {
            'sender': sender,
            'content': content,
            'timestamp': time.time()
        }
        if metadata:
            msg['metadata'] = metadata
        
        self.messages.append(msg)
        self.message_queue.put(msg)
        self.message_count += 1
        self.last_activity_time = time.time()
        
        # Debug logging to verify queue population
        logger.debug(f"Session {self.session_id}: Added message from {sender} (queue size: {self.message_queue.qsize()})")

        # log to structured log
        self.logger.log_message(sender, content, metadata)

        # Safety: stop if message count exceeds limit
        if self.message_count > MAX_MESSAGES_PER_SESSION :
            self.status = "stopping"
            self.stop_event.set()
            self._add_message("system", f"Maximum messages ({MAX_MESSAGES_PER_SESSION}) reached. Stopping session.")

    def _watchdog(self) :
        # Periodically check for inactivity and stop if necessary
        while not self.stop_event.is_set() :
            time.sleep(10)  # Check every 10 seconds
            if self.status == "running" :
                now = time.time()
                if now - self.last_activity_time > INACTIVITY_TIMEOUT_SECONDS :
                    self.status = "stopping"
                    self.stop_event.set()
                    self._add_message("system", f"Inactivity timeout ({INACTIVITY_TIMEOUT_SECONDS}s) reached. Stopping session.")
                    break

    def send_user_input(self, text: str) :
        # Put a user message into the input queue for the running workflow
        if self.status == "finished" :
            raise RuntimeError("Cannot send user input: session already finished")
    
        self.user_input_queue.put(text)
        self._add_message("user", text)   # also store in message history
    
    def stop(self) :
        # Signal the thread to stop (if possible)
        self.status = "stopping"
        self.stop_event.set()
        # no further action needed; the workflow will eventually exit
        # when the timeout or max messages is reached.

    def get_messages(self) :
        return self.messages

# ----- AgentManager Singleton -----

class AgentManager :
    # Singleton to manage all active sessions
    
    def __init__(self):
        self.sessions: Dict[str, AgentSession] = {}
    
    def create_session(self, workflow: str, task: str) -> str :
        # create and start a new session
        session_id = str(uuid.uuid4())[:8]
        session = AgentSession(session_id, workflow, task)
        self.sessions[session_id] = session
        session.start()
        logger.info(f"Created session {session_id} ({workflow})")
        return session_id
    
    def stop_session(self, session_id: str) -> bool :
        # stop and remove a session
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.stop()
            del self.sessions[session_id]
            logger.info(f"Stopped session {session_id}")
            return True
        return False
    
    def get_session(self, session_id: str) -> Optional[AgentSession] :
        return self.sessions.get(session_id)
    
    def get_message_queue(self, session_id: str) -> Optional[queue.Queue] :
        session = self.get_session(session_id)
        return session.message_queue if session else None
    
    def list_sessions(self) :
        # return summary of all sessions
        return [
            {
                'id': sid,
                'workflow': s.workflow,
                'status': s.status,
                'task': s.task[:50] + '...' if len(s.task) > 50 else s.task,
                'message_count': len(s.messages)
            }
            for sid, s in self.sessions.items()
        ]
    
    def terminate_session(self, session_id: str) -> bool :
        # Hard terminate (same as stop for now)
        return self.stop_session(session_id)

# Global instance
agent_manager = AgentManager()