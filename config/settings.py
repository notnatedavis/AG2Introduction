#   config/settings.py
#   Global settings

# ----- Imports -----
import os

# ----- Constants -----
# directory where code will be executed/saved
WORK_DIR = os.path.join(os.getcwd(), "workspace")
os.makedirs(WORK_DIR, exist_ok=True)
DEFAULT_TEMPERATURE = 0.2 # default temperature for LLM
TERMINATION_KEYWORD = "TERMINATE" # termination message keyword