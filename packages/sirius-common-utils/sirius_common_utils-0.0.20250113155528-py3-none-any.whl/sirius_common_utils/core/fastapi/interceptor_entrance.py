import time

from sirius_common_utils.core.logging import logging, log_name

logger = logging.get_logger(log_name.LOG_COMMON_CORE)
loggerWebInterceptor = logging.get_logger(log_name.LOG_COMMON_CORE_WEB_INTERCEPTOR)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.global_var import global_var

async def trace_log_filter_entrance(request: Request, call_next):
    start_time = time.time()
    loggerWebInterceptor.info(f"Request: {request.method} {request.url}")

    try:
        response = await call_next(request)
    except Exception as ex:
        # 全局异常处理
        loggerWebInterceptor.error(f"Error: {ex}", exc_info=True)
        response = JSONResponse(
            status_code=500,
            content={"errorCode": "500", "msg": str(ex)}
        )

    # 请求后逻辑
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    loggerWebInterceptor.info(f"Response status: {response.status_code} in {process_time:.4f} seconds")

    return response
