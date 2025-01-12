import logging
from logging.handlers import RotatingFileHandler
from .path_utils import mkdirs
def get_logFile(bpName,maxBytes=100000, backupCount=3):
    log_dir = mkdirs('logs')
    log_path = os.path.join(log_dir,f'{bpName}.log')
    log_handler = RotatingFileHandler(log_path, maxBytes=100000, backupCount=backupCount)
    log_handler.setLevel(logging.INFO)
    logger = logging.getLogger(bpName)
    logger.addHandler(log_handler)
    return logger
