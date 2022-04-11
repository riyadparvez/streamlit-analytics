import sys

try:
    # This is for development
    from loguru import logger as _logger

    def log_formatter(record):
        if len(record["extra"]) > 0:
            fmt = "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> |{extra}| - <level>{message}</level>"
        else:
            fmt = "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> - <level>{message}</level>"
        return fmt + "\n{exception}"


    _logger.remove()
    _logger.add(
        sys.stdout, level="INFO", colorize=True, format=log_formatter, backtrace=True
    )
    raise Exception("")

except Exception:
    # This is for production use
    import logging
    import logging.config

    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default_formatter': {
                'format': "%(asctime)s |%(name)s| [%(levelname)-7.5s] {%(filename)-20s:%(lineno)-3d }:%(message)s",
            },
        },
        'handlers': {
            'stream_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'default_formatter',
            },
        },
        'loggers': {
            'streamlit-analytics': {
                'handlers': ['stream_handler',],
                'level': 'INFO',
                'propagate': False,
            }
        }
    }

    logging.config.dictConfig(LOGGING_CONFIG)
    _logger = logging.getLogger('streamlit-analytics')

logger = _logger
