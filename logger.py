import logging


def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - Line %(lineno)d - %(message)s')

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
