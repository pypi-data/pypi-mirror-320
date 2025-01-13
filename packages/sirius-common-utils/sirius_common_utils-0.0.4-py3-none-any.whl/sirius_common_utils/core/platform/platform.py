

def is_platform_arm():
    return platform.machine().startswith(("arm", "aarch64"))

def is_os_windows():
    return "windows" in platform.system()