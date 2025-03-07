import logging
import sys


def setup_logger() -> logging.Logger:
    """
    Setups logging to stdout
    :return: Logger
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)

    return logger