__version__ = "1.0.0"


def logger_init(DEBUG: bool = False, file: bool = True):
    from loguru import logger
    from sys import stdout
    logger.remove()
    if file:
        logger.add("./log/log_paul-tools_{time}.log")
    logger.add(stdout, level=("DEBUG" if DEBUG else "INFO"),
               format="<level>{message}</level>")
    return logger


logger = logger_init()
