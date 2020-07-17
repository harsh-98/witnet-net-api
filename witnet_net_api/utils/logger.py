import logging
import os


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        # %(asctime)s
        '%(levelname)-8s [%(filename)s:%(lineno)d]' + logger_name + ': %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    return logger


log = get_logger('witnet_api')
