"""
Logging files taken from instrumentserver.
"""

import sys
import logging

logging.basicConfig(level=logging.DEBUG)


def setup_logging(add_stream_handler=True, log_file=None, name='filechecker', stream_handler_level=logging.DEBUG):

    logger = logging.getLogger(name)

    for h in logger.handlers:
        logger.removeHandler(h)
        del h

    if log_file is not None:
        fmt = logging.Formatter(
            "%(asctime)s:%(name)s:%(levelname)s:%(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        fh = logging.FileHandler(log_file)
        fh.setFormatter(fmt)
        fh.setLevel(stream_handler_level)
        logger.addHandler(fh)

    if add_stream_handler:
        fmt = logging.Formatter(
            "[%(asctime)s] [%(name)s: %(levelname)s] %(message)s",
            datefmt='%m/%d %H:%M',
        )
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(fmt)
        stream_handler.setLevel(stream_handler_level)
        logger.addHandler(stream_handler)

    logger.info(f"Logging set up for {name}.")


def log_logger(name='filechecker'):
    """Get the (root) logger for the package."""
    return logging.getLogger(name)


