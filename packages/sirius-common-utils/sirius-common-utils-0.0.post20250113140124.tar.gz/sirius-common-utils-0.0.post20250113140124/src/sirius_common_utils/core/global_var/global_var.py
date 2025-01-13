from sirius_common_utils.core.logging import logging, log_name
logger = logging.get_logger(log_name.LOG_COMMON_CORE)

from pathlib import Path

import logging

g_project_root = None

def init():
    global g_project_root

    g_project_root = Path(__file__).resolve().parent.parent.parent.parent
    logger.debug(f"project_root: {g_project_root}")
    logger.debug(f"init")


def get_project_root():
    global g_project_root

    if g_project_root is None:
        g_project_root = Path(__file__).resolve().parent.parent.parent.parent
        logger.debug(f"project_root: {g_project_root}")

    return g_project_root