from sirius_common_utils.core.logging import logging, log_name

import logging
import pyodbc


logger = logging.getLogger(log_name.LOG_COMMON_CORE_ODBC_CONNECTION)

# Key: conn name
g_conn_map = {}

def get_conn(ds_name, server_name, db_name, username, password):
    global g_conn_map

    conn = g_conn_map.get(ds_name)
    if conn is None:
        conn = open_conn(server_name, db_name, username, password)
        g_conn_map[ds_name] = conn

    return conn

def open_conn(server_name, db_name, username, password):
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={db_name};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    return conn

def close_conn(ds_name:None):
    global g_conn_map

    if ds_name is None:
        for conn in g_conn_map.values():
            conn.close()
    else:
        conn = g_conn_map[ds_name]
        if conn is not None:
            conn.close()
