from typing import Dict, List, Any, TypeVar, Callable, Type, get_type_hints
import requests
from requests import Response
import time
import logging
from pydantic import BaseModel
import functools

# Type aliases
MultiLanguageField = Dict[str, str]
MultiLanguageKeywords = Dict[str, List[str]]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_error(error: Exception) -> None:
    """
    Handles errors by logging the details and re-raising the error.
    
    Args:
        error: The error object to handle.
    Raises:
        Exception: Re-raises the provided error after logging it.
    """
    if isinstance(error, requests.exceptions.RequestException):
        if error.response is not None:
            logger.error(f"Error response: {error.response.text}")
            logger.error(f"Error status: {error.response.status_code}")
        elif error.request is not None:
            logger.error(f"No response received: {error.request}")
        else:
            logger.error(f"Error: {str(error)}")
    else:
        logger.error(f"Error: {str(error)}")
    raise error

def handle_request_error(error: requests.exceptions.RequestException) -> None:
    """
    Handles requests-specific errors by logging the details and re-raising the error.
    
    Args:
        error: The error object to handle, typically from a requests request.
    Raises:
        requests.exceptions.RequestException: Re-raises the provided error after logging it.
    """
    if error.response is not None:
        logger.error(f"Error: {error.response.status_code} - {error.response.text}")
    else:
        logger.error(str(error))
    raise error

def deep_freeze(obj: Any) -> Any:
    """
    Recursively makes an object immutable (read-only).
    Note: In Python, true immutability is harder to achieve than in TypeScript,
    but we can use some techniques to make objects more immutable-like.
    
    Args:
        obj: The object to deep freeze.
    Returns:
        A more immutable version of the input object.
    """
    if isinstance(obj, dict):
        return frozenset((k, deep_freeze(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        return tuple(deep_freeze(x) for x in obj)
    elif isinstance(obj, set):
        return frozenset(deep_freeze(x) for x in obj)
    return obj

T = TypeVar('T')

def retry_request(
    request_fn: Callable[[], Response],
    max_retries: int = 30,
    delay_ms: int = 1000,
    system_processing_flag: str = "SYSTEM_PROCESSING"
) -> Response:
    """
    Repeatedly tries a request until the response meets specific criteria.
    
    Args:
        request_fn: A function that executes a request and returns a response.
        max_retries: Maximum number of retries before giving up.
        delay_ms: Delay between retries in milliseconds.
        system_processing_flag: Flag indicating system is still processing.
    
    Returns:
        The response that meets the criteria.
    
    Raises:
        Exception: If max retries reached or if an error occurs.
    """
    retries = 0
    
    while retries < max_retries:
        try:
            response = request_fn()
            if response.status_code == 200:
                data = response.json()
                if data.get('flag') != system_processing_flag:
                    return response
            
            retries += 1
            time.sleep(delay_ms / 1000)  # Convert ms to seconds
            
        except Exception as e:
            handle_error(e)
    
    raise Exception(f"Maximum retries ({max_retries}) reached")

def auto_setters(cls: Type[T]) -> Type[T]:
    """Decorator to automatically generate setter methods for all fields in a Pydantic model."""
    
    hints = get_type_hints(cls)
    
    for field_name, field_type in hints.items():
        # Skip class variables and internal fields
        if field_name.startswith('_') or field_name.isupper():
            continue
            
        # Generate setter method name
        setter_name = f'set_{field_name}'
        
        # Skip if setter already exists
        if hasattr(cls, setter_name):
            continue
            
        # Create setter method
        def make_setter(name):
            @functools.wraps(setattr)
            def setter(self, value):
                """Auto-generated setter method."""
                setattr(self, name, value)
            return setter
            
        # Add setter to class
        setattr(cls, setter_name, make_setter(field_name))
    
    return cls
