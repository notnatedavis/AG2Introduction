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
   - `venv\Scripts\activate` on Windows , `source venv/bin activate` on macOS
4. download prerequisites
   - `pip install -r requirements.txt` on Windows , `pip3 install -r requirements.txt` on macOS
5. Copy `.env.example` file into root directory and rename to `.env` , update `your_api_key_here` with actual deepseek api key
6. Launch web interface with `python main.py web` on Windows , `python3 main.py web` on macOS
7. open within browser @ `http://127.0.0.1:5000/` (use `Ctrl + C` to end)

## Configuration

- update

## Project-Structure

AG2Introduction/   
├── agents/  
│   ├── `__init__.py`  
│   ├── `base_agent.py`  
│   ├── `coding_agent.py`  
│   ├── `executor_agent.py`  
│   └── `webpage_agent.py`  
├── config/  
│   ├── `__init__.py`  
│   ├── `llm_config.py`  
│   └── `settings.py`  
├── tools/  
│   ├── `__init__.py`  
│   ├── `code_execution.py`  
│   └── `file_tools.py`  
├── utils/  
│   ├── `__init__.py`  
│   ├── `helpers.py`  
│   └── `logging_utils.py`  
├── workflows/  
│   ├── `__init__.py`    
│   ├── `coding_workflow.py`  
│   └── `webpage_workflow.py`  
├── `.env.example`  
├── `.gitignore`  
├── `main.py`  
├── `ReadMe.md`  
└── `requirements.txt`  

## Additional-Info

This portion is for logging or storing notes relevent to the project and its scope.
