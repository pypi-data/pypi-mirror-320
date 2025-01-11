import logging


def log_message(message: str, level: str = "info"):
    logging.basicConfig(level=logging.INFO)
    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)
