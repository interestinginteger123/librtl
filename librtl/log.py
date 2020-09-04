"""Standardised logging setup for the library
"""
import logging
from logging.handlers import RotatingFileHandler
import sys

def make_logger(name: str, stream_level=logging.WARN, file_level=logging.DEBUG):
    """Create a logger for a given name

    The log file on disk will rotate every 65536 bytes or when there is another execution.
    There should always be a historic log file for each of the last two runs. The stream
    handler is conventionally set to a higher level than the file handler, the defaults are
    WARN and DEBUG. This is to reduce chattyness on cli.

    :param name: name of the logger
    :param stream_level: One of logging level [default: logging.WARN]
    :param file_level: One of logging level [default: logging.DEBUG]
    :returns: logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(stream_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    file_handler = RotatingFileHandler(f"{name}.log", backupCount=1, maxBytes=65536)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    file_handler.doRollover()
    return logger
