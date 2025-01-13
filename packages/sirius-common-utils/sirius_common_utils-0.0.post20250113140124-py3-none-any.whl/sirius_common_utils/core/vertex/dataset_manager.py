from app.global_var import constant, log_name

import logging

def create(ds_name:None):
    global g_engine_map

    if ds_name is None:
        for conn in g_engine_map.values():
            conn.close()
    else:
        conn = g_engine_map[ds_name]
        if conn is not None:
            conn.close()
