#   web/agent_manager.py
#   Manages active agent sessions 
#   (create, stop, list, message streaming)

# ----- Imports -----
import uuid
import threading
import queue
import time
from typing import Dict, Optional
from workflows import run_webpage_workflow, run_coding_workflow
from agents.executor_agent import ExecutorAgent
from agents.webpage_agent import WebpageAgent
from agents.coding_agent import CodingAgent
import autogen
from autogen import register_function
from tools.file_tools import write_html_file

# ----- AgentSession Class -----
class AgentSession:
    # Represents a running agent workflow session
    
    def __init__(self, session_id: str, workflow: str, task: str) :
        self.session_id = session_id
        self.workflow = workflow
        self.task = task
        self.status = "starting"  # starting, running, stopping, finished
        self.messages = []        # store all messages for history
        self.message_queue = queue.Queue()
        self.thread = None
        self.stop_event = threading.Event()
        self.agents = {}          # store references to agents if needed
    
    def start(self) :
        # launch the workflow in a background thread
        self.thread = threading.Thread(target=self._run_workflow)
        self.thread.daemon = True
        self.thread.start()
    
    def _run_workflow(self) :
        # execute the appropriate workflow with message capturing
        self.status = "running"
        try :
            if self.workflow == "webpage" :
                self._run_webpage_workflow()
            elif self.workflow == "coding" :
                self._run_coding_workflow()
            else :
                raise ValueError(f"Unknown workflow: {self.workflow}")
        except Exception as e :
            self._add_message("system", f"Error: {str(e)}")
        finally :
            self.status = "finished"
            self._add_message("system", "Workflow finished.")
    
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
    
    def _add_message(self, sender: str, content: str) :
        # Store a message and put it in the queue for streaming
        msg = {
            'sender': sender,
            'content': content,
            'timestamp': time.time()
        }
        self.messages.append(msg)
        self.message_queue.put(msg)
    
    def stop(self) :
        # Signal the thread to stop (if possible)
        self.status = "stopping"
        self.stop_event.set()
        # Note: AG2 doesn't have a clean way to stop a running chat.
        # We'll rely on the thread finishing naturally.
        # For now, we just mark it as stopping and remove the session.
        # In a more advanced implementation, you could inject a termination message.
    
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
        return session_id
    
    def stop_session(self, session_id: str) -> bool :
        # stop and remove a session
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.stop()
            del self.sessions[session_id]
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