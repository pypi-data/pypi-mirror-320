import logging

def init():
    logging.config.fileConfig('../conf/logging.conf')

def get_logger(name=None):
    return logging.getLogger(name)
