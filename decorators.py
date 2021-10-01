import logging


def suppress_request_warnings(original_function):
    """
    If Django gives a warning for a known http status code (404, 405, 402),
    this decorator can suppress the warning to keep test log output clean.
    """
    def new_function(*args, **kwargs):
        # raise logging level to ERROR
        logger = logging.getLogger('django.request')
        previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        # trigger original function that would throw warning
        original_function(*args, **kwargs)

        # lower logging level back to previous
        logger.setLevel(previous_logging_level)

    return new_function
