from sirius_common_utils.core.logging import logging
from sirius_common_utils.core.global_var import global_var

def init():
    logging.init()
    global_var.init()
