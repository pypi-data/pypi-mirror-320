import logging

logger = logging.getLogger("AutoRPE")

# Create console handler
ch = logging.StreamHandler()

# Define log format to include timestamp and log level
log_format = "%(asctime)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(log_format, date_format)

# Set formatter for console handler
ch.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(ch)

def clean_line():
    """
    Clears the current line in the terminal using ANSI escape codes.

    Returns:
        None
    """
    # ANSI escape code to clear the line and move cursor to the beginning
    print("\r\033[K", end="")


