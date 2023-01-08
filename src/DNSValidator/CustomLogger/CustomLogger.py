from .CustomFormatter import CustomFormatter
import logging

def CustomLogger(name: 'str') -> 'logging.Logger':
    """ Creates a custom formatted logger named <name> """

    # Create logger with "someName"
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    return logger

def add_CustomFileHandler(logger: 'logging.Logger', logFile: 'str') -> 'logging.Logger':
    fh = logging.FileHandler(logFile, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(CustomFormatter())
    logger.addHandler(fh)
    return logger
