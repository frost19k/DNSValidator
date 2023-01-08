import logging

from .colors import colors
from .emoji import emoji

class CustomFormatter(logging.Formatter):
    """ Logging Formatter that adds colors and, count warning & errors. """

    log_HeadFormat = '%(asctime)s ⋞ {levelEmoji} ⋟ '

    FORMATS = {
        logging.DEBUG: log_HeadFormat.format(levelEmoji=emoji['dashing_away']) + '%(message)s' + colors['reset'],
        logging.INFO: log_HeadFormat.format(levelEmoji=emoji['speech_balloon']) + '%(msgC)s%(message)s' + colors['reset'],
        logging.WARNING: log_HeadFormat.format(levelEmoji=emoji['bomb']) + colors['yellow'] + '%(message)s' + colors['reset'],
        logging.ERROR: log_HeadFormat.format(levelEmoji=emoji['anger_symbol']) + colors['red'] + '%(message)s' + colors['reset'],
        logging.CRITICAL: log_HeadFormat.format(levelEmoji=emoji['collision']) + colors['bold_red'] + '%(message)s (%(filename)s:%(lineno)d)' + colors['reset'],
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        # formatter = logging.Formatter(log_fmt, datefmt='%I:%M:%S %p')
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)
