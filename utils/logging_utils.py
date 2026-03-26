#   utils/logging_utils.py
#   Configure logging for the project

# ----- Imports -----

import json
import logging
import os
import time
from typing import Any, Dict, Optional

# ----- Helper Functions -----

def setup_logging(level=logging.INFO) :
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=level
    )
    return logging.getLogger(__name__)

# ----- Main -----

class StructuredLogger :
    # Writes structured log entries to a JSON Lines file for a given session
    # each log entry is a JSON object with a 'type' field and other relevant data
    
    def __init__(self, session_id: str, log_dir: str = "logs") :
        self.session_id = session_id
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, f"session_{session_id}.jsonl")
        self.file = open(self.log_path, "a", encoding="utf-8")

    def _write(self, entry: Dict[str, Any]) :
        # write a JSON line to the log file
        entry["timestamp"] = time.time()
        entry["session_id"] = self.session_id
        self.file.write(json.dumps(entry) + "\n")
        self.file.flush()  # ensure immediate write for replayability

    def log_system_prompt(self, agent_name: str, system_message: str) :
        # log the system prompt of an agent at session start
        self._write({
            "type": "system_prompt",
            "agent": agent_name,
            "prompt": system_message
        })

    def log_message(self, sender: str, content: str, metadata: Optional[Dict] = None) :
        # log a conversation message
        entry = {
            "type": "message",
            "sender": sender,
            "content": content
        }
        if metadata:
            entry["metadata"] = metadata
        self._write(entry)

    def log_tool_call(self, agent: str, tool_name: str, arguments: Dict) :
        # log a tool call before execution
        self._write({
            "type": "tool_call",
            "agent": agent,
            "tool": tool_name,
            "arguments": arguments
        })

    def log_tool_output(self, agent: str, tool_name: str, output: str) :
        # log the raw output of a tool after execution
        self._write({
            "type": "tool_output",
            "agent": agent,
            "tool": tool_name,
            "output": output
        })

    def log_token_usage(self, agent: str, usage: Dict) :
        # log token usage from an LLM response
        # might not be needed if on free plan
        self._write({
            "type": "token_usage",
            "agent": agent,
            "usage": usage
        })

    def close(self) :
        # close the log file
        self.file.close()