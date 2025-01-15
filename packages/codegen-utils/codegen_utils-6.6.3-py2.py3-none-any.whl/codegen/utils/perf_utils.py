import logging
import time
from functools import wraps

import sentry_sdk

from codegen.utils.time_utils import humanize_duration

logger = logging.getLogger(__name__)


def stopwatch(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logger.info(f"Function '{func.__name__}' took {humanize_duration(execution_time)} to execute.")
        return result

    return wrapper


def stopwatch_with_sentry(name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with sentry_sdk.start_transaction(name=name):
                start_time = time.perf_counter()
                res = func(*args, **kwargs)
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                logger.info(f"Function '{func.__name__}' took {humanize_duration(execution_time)} to execute.")
                return res

        return wrapper

    return decorator
