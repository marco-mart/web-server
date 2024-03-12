from logging_config.logger_tools import get_logger

logger = get_logger()

logger.debug('bruh')
logger.warning('warning')
logger.critical('frick man')

try:
    x = 3 / 0
except ZeroDivisionError:
    logger.exception('Oh snap!!')