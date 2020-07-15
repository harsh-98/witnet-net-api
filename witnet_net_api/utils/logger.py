import logging
import os


def get_logger():
    logger = logging.getLogger('witnet_api')
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s, %(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    return logger


log = get_logger()
