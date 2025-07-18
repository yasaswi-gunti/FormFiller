import os
import logging
import re

def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))

def get_path(*paths):
    return os.path.join(get_project_root(),'files', *paths)

def format_date(value):
    # Remove any non-digit characters (like '-' or '/')
    digits = re.sub(r'\D', '', value)
    
    # Match the cleaned-up string with a pattern and reformat
    match = re.fullmatch(r'(\d{2})(\d{2})(\d{4})', digits)
    if match:
        return f"{match.group(1)} {match.group(2)} {match.group(3)}"
    else:
        return None  # or raise an error if you want strict handling

def setup_logger():
    log_file = os.path.join(get_project_root(), 'logs', 'app.log')
    os.makedirs(os.path.dirname(log_file),exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger

logger = setup_logger()