import logging
import io


def make_noop_logger() -> logging.Logger:
    null_logger = logging.getLogger("NOOP")
    null_logger.handlers.clear()
    null_logger.addHandler(logging.NullHandler())  # read below for reason
    null_logger.propagate = False
    return null_logger


def make_string_logger(name: str, sio: io.StringIO) -> logging.Logger:
    string_logger = logging.getLogger(name)
    string_logger.handlers.clear()
    string_logger.addHandler(logging.StreamHandler(sio))
    string_logger.propagate = False
    return string_logger


NOOP_LOGGER = make_noop_logger()
