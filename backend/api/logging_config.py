import logging
import os

def setup_logging(log_file=None):
    if log_file is None:
        # Default log file in the same directory as this script
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sovren_ai.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    ) 