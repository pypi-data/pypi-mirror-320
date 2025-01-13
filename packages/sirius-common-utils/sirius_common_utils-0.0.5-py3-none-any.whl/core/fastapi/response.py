from datetime import datetime


def success():
    return {
        "result": "success",
        "message": "success",
        "timestamp": datetime.now(),
    }


def failure(code='999', message=''):
    return {
        "result": "failure",
        "code": code,
        "message": message,
        "timestamp": datetime.now(),
    }
