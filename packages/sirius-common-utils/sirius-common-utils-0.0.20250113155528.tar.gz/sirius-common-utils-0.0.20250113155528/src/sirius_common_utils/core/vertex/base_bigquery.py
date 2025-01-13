from sirius_common_utils.core.logging import logging, log_name
logger = logging.get_logger(log_name.LOG_COMMON_CORE_CLOUD_BIGQUERY)


from google.cloud import bigquery

from app.global_var import constant

import google.api_core.exceptions as core_exceptions

g_client = None
g_dataset = None
g_table_asset = None

g_project_id = None
g_dataset_id = None
g_region_id = None

def init(project_id, dataset_id, region_id):
    global g_client, g_dataset

    g_project_id = project_id
    g_dataset_id = dataset_id
    g_region_id = region_id

    if g_client is None:
        g_client = bigquery.Client(g_project_id)

    if g_dataset is None:
        g_dataset = bigquery.Dataset(g_dataset_id)
        create_dataset()


def client():
    return g_client


def create_dataset():
    global g_client, g_dataset, g_region_id, g_dataset_id

    g_dataset.location = g_region_id
    g_dataset.description = "sirius"
    g_dataset.labels = {"environment": "production", "type": "timeseries"}

    g_dataset = g_client.create_dataset(bigquery.Dataset(g_dataset_id), exists_ok=True)
    logger.info(f"Dataset {g_dataset.full_dataset_id} created in project {g_dataset.project}.")


def delete_dataset():
    global g_client, g_dataset

    g_client.delete_dataset(g_dataset, True)
    logger.info(f"Dataset '{g_dataset.full_dataset_id}' deleted successfully.")


def dataset():
    return g_dataset


def create_table(table_id, schema, re_create_flag):
    global g_client, g_dataset

    if not isinstance(table_id, str):
        raise ValueError("Input must be a tableId string")

    is_table_exist = exist_table(table_id)

    if is_table_exist:
        if re_create_flag:
            delete_table(table_id)
        else:
            return bigquery.Table(table_id)

    table = g_client.create_table(bigquery.Table(table_id, schema=schema))
    logger.info(f"Table '{table.full_table_id}' created successfully.")

    return table


def exist_table(tableId):
    global g_client, g_dataset

    try:
        g_client.get_table(tableId)
        return True
    except core_exceptions.NotFound:
        return False


def delete_table(table_id):
    global g_client

    # g_client.delete_table(bigquery.Table(tableId), True)
    g_client.Table(table_id).delete()
    # logger.info(f"Table '{table.full_table_id}' deleted successfully.")


def list_tables():
    global g_client, g_dataset
    tables = g_client.list_tables(g_dataset)

    for table in tables:
        print(table.table_id)


def delete_table(tableId):
    global g_client, g_table_trenddata

    g_client.delete_table(bigquery.Table(tableId))
    logger.info(f"Table '{tableId}' deleted successfully.")


