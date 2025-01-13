import time

from sirius_common_utils.core.logging import logging, log_name

logger = logging.get_logger(log_name.LOG_COMMON_CORE)
loggerWebInterceptor = logging.get_logger(log_name.LOG_COMMON_CORE_WEB_INTERCEPTOR)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.global_var import global_var




async def trace_log_filter_user_info(request: Request, call_next):
    # user = 'Joey'

    # try:
    response = await call_next(request)
    # finally:
    # loggerWebInterceptor.info(f"User Info: {user}")

    return response

