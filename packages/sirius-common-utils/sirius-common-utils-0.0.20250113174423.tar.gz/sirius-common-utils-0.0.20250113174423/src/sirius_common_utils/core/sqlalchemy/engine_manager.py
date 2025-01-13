from sirius_common_utils.core.logging import logging, log_name
logger = logging.get_logger(log_name.LOG_COMMON_CORE_ODBC_QUERY)


from sqlalchemy import create_engine, inspect

# Key: data source name
g_engine_map = {}


def get_engine(ds_name, server_name, server_port, db_name, username, password):
    global g_conn_map

    engine = g_engine_map.get(ds_name)
    if engine is None:
        engine = open_engine(server_name, server_port, db_name, username, password)
        g_engine_map[ds_name] = engine

    return engine


def open_engine(server_name, server_port, db_name, username, password):
    conn_str = f'mssql+pyodbc://{username}:{password}@{server_name}:{server_port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server'
    engine = create_engine(conn_str)
    return engine


def get_table_names(engine):
    inspector = inspect(engine)
    return inspector.get_table_names()


def close_engine(ds_name:None):
    global g_conn_map

    if ds_name is None:
        for conn in g_engine_map.values():
            conn.close()
    else:
        conn = g_engine_map[ds_name]
        if conn is not None:
            conn.close()
