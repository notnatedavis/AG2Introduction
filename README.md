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

## Features

- features

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

## Configuration

- update

## Project-Structure

AG2Introduction/   
- agents/  
   - `__init__.py`  
   - `base_agent.py`  
   - `coding_agent.py`  
   - `executor_agent.py`  
   - `webpage_agent.py`  
- config/  
   - `__init__.py`  
   - `llm_config.py`  
   - `settings.py`  
- tools/  
   - `__init__.py`  
   - `code_execution.py`  
   - `file_tools.py`  
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
   - `webpage_workflow.py`  
- `.env.example`  
- `main.py`  
- `requirements.txt`  
- `.gitignore`  
- `ReadMe.md`  

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