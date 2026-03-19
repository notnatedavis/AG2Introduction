#   utils/helpers.py
#   Miscellaneous helper functions

# ----- Imports -----
import os

# ----- Helper Functions -----
def ensure_dir(path: str) -> str :
    # ensure a directory exists; create if necessary
    os.makedirs(path, exist_ok=True)
    return path