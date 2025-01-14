from loguru import logger


__version__ = "1.0.0"


def logger_init(DEBUG: bool = False, file: bool = True) -> None:
    from sys import stdout
    logger.remove()
    if file:
        logger.add("./log/log_paul-tools_{time}.log")
    logger.add(stdout, level=("DEBUG" if DEBUG else "INFO"),
               format="<level>{message}</level>")


logger_init()
