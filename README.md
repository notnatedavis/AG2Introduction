# AG2Introduction

AG2 is a framework that allows you to create multiple AI agents that talk to each other to solve complex tasks. Example; have a `Planner` agent that breaks down a problem, a `Coder` agent that writes code, and an `Executor` agent that runs that code and reports back. AG2 supports any LLM that follows the OpenAI API format and DeepSeek does exactly that, with free tier.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Usage](#usage)
- [Configuration](#Configuration)
- [Project-Structure](#Project-Structure)
- [Additional-Information](#Additional-Info)

## Introduction

update

---

## Features

### Safety & Determinism
To prevent runaway workflows, the following safeguards are in place :
- **Chat Timeout**: Each workflow is limited to 5 minutes of execution time.
- **Message Limit**: Sessions are stopped after 200 messages to avoid infinite loops.
- **Inactivity Timeout**: If no new message appears for 2 minutes, the session is terminated.
- **Termination Signal**: All agents are instructed to reply `TERMINATE` when their task is complete; the system respects this signal and ends the workflow.
- These limits can be adjusted in `web/agent_manager.py` by modifying the constants `MAX_MESSAGES_PER_SESSION`, `INACTIVITY_TIMEOUT_SECONDS`, and the timeout value passed to `run_team_workflow`.

### Security & Least Privilege
To protect the system from unintended actions, the following security measures are enforced:
- **Human‑in‑the‑loop (HITL)** for dangerous tools: `write_file`, `write_html_file`, and `execute_command` require explicit user approval before execution.
- **Read‑only by default**: Shell commands are checked against a whitelist of read‑only commands (e.g., `ls`, `cat`, `grep`). Any command not in the whitelist (or any write operation) triggers an approval request.
- **Clear tool descriptions**: All tool names and descriptions indicate whether they are read (`[READ]`), write (`[WRITE]`), or execute (`[EXECUTE]`) operations, helping agents (and humans) understand the permission level.
- The approval mechanism uses the same user input queue as the conversation, so the frontend can display approval prompts and wait for user response

### Observability & Logging
To support debugging and replayability, every agent session produces a structured log file in `logs/session_<id>.jsonl`. Each line is a JSON object with a `type` field. The logs capture :
- **System prompts** of all agents at session start.
- **Every conversation message** (sender, content, timestamp).
- **Tool calls** (agent, tool name, arguments) and **tool outputs**.
- **Token usage** (if provided by the LLM).
- These logs can be replayed or analyzed to understand the exact decision path of the agents.
- To disable logging, simply omit the `logger` argument when calling workflows.

---

## Usage 

1. `git clone` & `cd AG2Introduction` in
2. create a python virtual environment
   - `python -m venv venv` on Windows , `python3 -m venv venv` on macOS
3. activate virtual environment
   - `venv\Scripts\activate` on Windows , `source venv/bin/activate` on macOS
4. download prerequisites
   - `pip install -r requirements.txt` on Windows , `pip3 install -r requirements.txt` on macOS
5. Copy&Paste `.env.example` file in same  directory and rename to `.env` , update `your_api_key_here` with actual deepseek api key
6. Launch Flask backend API `python main.py web` on Windows , `python3 main.py web` on macOS
7. `cd web/frontend` + `npm install` + `npm start`

---

## Configuration

- update

---

## Project-Structure

AG2Introduction/   
- agents/  
   - `__init__.py`  
   - `base_agent.py`  
   - `coding_agent.py`  
   - `documenter.py`
   - `executor_agent.py`  
   - `manager_agent.py`
   - `reviewer_agent.py`
   - `tester_agent.py`
   - `tool_executor_agent.py`
   - `webpage_agent.py`  
- config/  
   - `__init__.py`  
   - `llm_config.py`  
   - `settings.py`  
- tools/  
   - `__init__.py`  
   - `code_execution.py`  
   - `file_tools.py`  
   - `tool_security.py`
- utils/  
   - `__init__.py`  
   - `helpers.py`  
   - `logging_utils.py`  
- web/  
   - frontend/  
      - public/  
         - `index.html`
      - src/  
         - components/  
            - `Conversation.css`
            - `Conversation.js`
            - `GraphPanel.css`
            - `GraphPanel.js`
            - `Message.css`
            - `Message.js`
            - `NewSessionForm.css`
            - `NewSessionForm.js`
            - `SessionItem.css`
            - `SessionItem.js`
            - `SessionList.css`
            - `SessionList.js`
         - services/  
            - `api.js`
         - `App.css`
         - `App.js`
         - `index.js`
      - `package.json`
   - `__init__.py`  
   - `agent_manager.py`  
   - `app.py`  
   - `routes.py`  
- workflows/  
   - `__init__.py`    
   - `coding_workflow.py`  
   - `team_workflow.py`
   - `webpage_workflow.py`  
- `.env.example`  
- `main.py`  
- `.gitignore`  
- `ReadMe.md`  
- `requirements.txt`  

---

## Additional-Info

This portion is for logging or storing notes relevent to the project and its scope.

- agents/ Contains agent definitions. Each agent is a class that returns an AutoGen AssistantAgent or UserProxyAgent. 
   - base_agent.py provides factory functions (create_assistant_agent, create_user_proxy) to standardize agent creation with the LLM config and common defaults.

- tools/ Plain Python functions that agents can invoke. They are registered with autogen.register_function() in the workflows.

- workflows/ Defines the conversation flows that use one or more agents and tools. Each workflow is a function that sets up agents, registers tools, and initiates the chat.

- web/ Flask backend and React frontend for the dashboard.
   - agent_manager.py manages sessions and runs workflows in background threads.
   - routes.py exposes API endpoints and serves the frontend.
   - The frontend (web/frontend/src/) lets users start sessions and view messages.

- config/ – Holds LLM configuration (llm_config.py) and global settings (settings.py).

- utils/ – Logging and helper functions.