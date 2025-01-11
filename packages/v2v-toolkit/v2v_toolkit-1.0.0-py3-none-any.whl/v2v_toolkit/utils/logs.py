import logging


def setup_logger(loggername, filename=None, level=logging.INFO, null=False):
    """Compose logger object with console and file handlers or null.

    Args:
        loggername: name of logger
        filename: path to log file
        level: logging level
        null: boolean flag for null logger

    Returns:
        Logger - composed logger object
    """
    logger = logging.getLogger(loggername)
    logger.setLevel(level)
    if null:
        logger.addHandler(logging.NullHandler())
        return logger
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s:\t%(module)s@%(lineno)s:\t%(message)s"
    )
    console_formatter = logging.Formatter("[%(levelname)s]\t\t%(message)s")
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(console_formatter)
    logger.addHandler(console)

    if filename:
        full = logging.FileHandler(filename, mode="w")
        full.setLevel(level)
        full.setFormatter(formatter)
        logger.addHandler(full)

    return logger
