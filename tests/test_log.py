import logging

from librtl.log import make_logger

def test_make_logger():
    logger = make_logger("foo")
    print(logger.handlers)
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2
