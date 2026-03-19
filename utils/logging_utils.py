#   utils/logging_utils.py
#   Configure logging for the project

# ----- Imports -----
import logging

# ----- Helper Functions -----
def setup_logging(level=logging.INFO) :
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=level
    )
    return logging.getLogger(__name__)