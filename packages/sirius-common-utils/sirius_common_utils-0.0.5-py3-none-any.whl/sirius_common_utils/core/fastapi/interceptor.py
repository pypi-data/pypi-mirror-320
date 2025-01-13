from . import interceptor_entrance
from . import interceptor_user_info

def register_middlewares(app):
    app.middleware("http")(interceptor_entrance.trace_log_filter_entrance)
    app.middleware("http")(interceptor_user_info.trace_log_filter_user_info)
