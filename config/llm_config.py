#   config/llm_config.py
#   Centralized LLM configuration (DeepSeek)

# ----- Imports -----
import os
from dotenv import load_dotenv

# ----- Constants -----
load_dotenv()  # Load environment variables from .env
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_API_BASE = "https://api.deepseek.com/v1"

# ----- Helper Functions -----
def get_llm_config(model: str = None, temperature: float = 0.2) :
    # Return the LLM configuration dictionary for autogen
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
    
    config_list = [
        {
            "model": model or DEFAULT_MODEL,
            "api_key": api_key,
            "base_url": DEFAULT_API_BASE,
        }
    ]
    return {
        "config_list": config_list,
        "temperature": temperature,
    }

def set_api_key(key: str) :
    # Helper to set API key programmatically (not recommended for production)
    os.environ["DEEPSEEK_API_KEY"] = key