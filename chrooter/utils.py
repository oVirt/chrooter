#!/bin/env python
import logging
from datetime import datetime
from functools import wraps
from subprocess import call as subprocess_call


LOGGER = logging.getLogger(__name__)


def call(command):
    LOGGER.debug('Executing command:')
    LOGGER.debug(' \\\n    '.join(command))
    return subprocess_call(command)


def timed(logger_name=__name__):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = datetime.now()
            func(*args, **kwargs)
            time_spent = datetime.now() - start
            logger = logging.getLogger(logger_name)
            logger.info('Took %sh' % time_spent)
        return wrapper
    return decorator
