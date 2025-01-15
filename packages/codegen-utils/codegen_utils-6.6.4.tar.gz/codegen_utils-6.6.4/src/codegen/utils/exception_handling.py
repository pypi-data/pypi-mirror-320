import logging
from collections.abc import Callable
from functools import wraps

logger = logging.getLogger(__name__)


def try_catch(description: str | None = None, exception_handler: Callable | None = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {description or func.__name__}: {e}")
                if exception_handler:
                    return exception_handler(e, description or func.__name__)

        return wrapper

    return decorator
