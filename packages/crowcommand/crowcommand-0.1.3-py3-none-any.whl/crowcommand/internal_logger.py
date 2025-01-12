import logging
import sys

# Create module-level logger
logger = logging.getLogger("crowcommander")

# Add handler if none exist
if not logger.handlers:
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('[Crowcommander] %(levelname)s: %(message)s'))
    logger.addHandler(handler)

def set_silent(silent: bool):
    """Enable or disable logging."""
    logger.setLevel(logging.CRITICAL if silent else logging.INFO)