import logging
from typing import Optional

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

GREEN = '\x1b[32m'
GREY = '\x1b[38;21m'
BLUE = '\x1b[36m'
YELLOW = '\x1b[38;5;226m'
RED = '\x1b[31m'
BOLD_RED = '\x1b[31;1m'
RESET = '\x1b[0m'

class CustomFormatter(logging.Formatter):

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.formats = {
            logging.DEBUG: "[%(levelname)s] " + self.fmt + RESET,
            logging.INFO: BLUE + "[%(levelname)s] " + RESET + self.fmt + RESET,
            logging.WARNING: YELLOW + "[%(levelname)s] " + RESET + self.fmt + RESET,
            logging.ERROR: RED + "[%(levelname)s] " + RESET + self.fmt + RESET,
            logging.CRITICAL: BOLD_RED + "[%(levelname)s] "+ RESET + self.fmt + RESET
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def getLogger(name: str, level: int, fmt: Optional[str] = None):
    if fmt is None:
        fmt = '%(message)s'

    logger = logging.getLogger(name)
    logger.setLevel(level)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(CustomFormatter(fmt))
    logger.addHandler(stdout_handler)
    return logger
