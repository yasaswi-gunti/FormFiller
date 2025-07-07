import os
import logging
import re

def get_output_file_name(player_name: str):
    cleaned = re.sub(r'[^A-Za-z0-9 ]+', '', player_name)
    cleaned = cleaned.replace(' ', '-')
    return os.path.join(f"{cleaned}.pdf")

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