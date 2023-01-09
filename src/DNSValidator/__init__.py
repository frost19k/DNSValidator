##->> Configure version info
from .version import __version__

##->> Configure logger
from .CustomLogger import CustomLogger
logger = CustomLogger('DNSValidator')
logger.propagate = False
