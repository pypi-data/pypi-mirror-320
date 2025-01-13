from sirius_common_utils.core.logging import logging

def init():
    logging.config.fileConfig('../conf/logging.conf')
    global_var.init()
