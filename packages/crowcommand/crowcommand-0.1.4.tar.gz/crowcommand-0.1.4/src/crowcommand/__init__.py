"""Top-level package for crowcommand."""

__author__ = """Samuel Edorodion"""
__email__ = 'sedorodion2003@gmail.com'
__version__ = '0.1.4'

from .logger import Logger
from .client import APIClient
from .internal_logger import logger as internal_logger, set_silent
from typing import Literal

# Define valid environment types
Environment = Literal['development', 'production']

_client_instance = None
logger = Logger()

def setup(
    api_key: str, 
    environment: Environment = 'development',
    silent: bool = True
) -> APIClient:
    """Initialize the SDK with your API key.
    
    Args:
        api_key: Your API key for authentication.
        environment: Either 'development' or 'production'. Defaults to 'development'.
        silent: Whether to silence internal SDK logs. Defaults to True.
        
    Returns:
        APIClient: The configured API client instance.
        
    Raises:
        ValueError: If environment is not 'development' or 'production'.
    """
    global _client_instance

    if environment not in ('development', 'production'):
        raise ValueError("environment must be either 'development' or 'production'")

    _client_instance = APIClient(api_key=api_key)
    
    # Update the logger's client and settings
    logger._client = _client_instance
    logger._environment = environment
    
    set_silent(silent)
    internal_logger.info(f"Initialized Crowcommander SDK in {environment} mode")
    
    return _client_instance

__all__ = ['logger', 'setup']