from sirius_common_utils.core.logging import logging, log_name

logger = logging.get_logger(log_name.LOG_COMMON_CORE_PLATFORM)

import platform

def is_platform_arm():
    text = platform.machine();
    logger.debug(f"{text}")
    return text.startswith(("arm", "aarch64"))


def is_os_windows():
    return "windows" in platform.system()
