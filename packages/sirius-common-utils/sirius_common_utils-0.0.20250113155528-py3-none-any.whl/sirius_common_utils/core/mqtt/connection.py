import json
import time

from core.datetime import date_formatter

import paho.mqtt.client as mqtt

from app.global_var import constant

from sirius_common_utils.core.logging import logging, log_name

logger = logging.get_logger(log_name.LOG_COMMON_CORE_MQTT)

g_mqtt_broker = None
g_mqtt_port = None


g_mqtt_client = None
g_status = {
    "ConnStatus": "",
    "Date": 0,
}


def init(broker, port):
    global g_mqtt_broker, g_mqtt_port

    g_mqtt_broker = broker
    g_mqtt_port = port

    get_client()


def connect():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        logger.debug(f"Establish MQTT Connection to {g_mqtt_broker}:{g_mqtt_port}")
        client.connect(g_mqtt_broker, g_mqtt_port, 60)

        client.loop_start()
    except Exception as e:
        print(f"连接失败：{e}")

    return client


def get_client():
    global g_mqtt_client

    if g_mqtt_client is None:
        g_mqtt_client = connect()

    return g_mqtt_client


def on_connect(client, userdata, flags, rc):
    global g_status

    if rc == 0:
        g_status['ConnStatus'] = 'Connected'
        logger.info("Establish MQTT Connection success")
    else:
        g_status['ConnStatus'] = 'Disconnected'
        logger.error(f"Establish MQTT Connection failed: {rc}")

    g_status['Date'] = date_formatter.convert_date_to_text(time, "%Y%m%d%H%M%S")

    msg = json.dumps(g_status)
    logger.debug(f"Send MQTT Status: {msg}")

    client.publish(constant.MQTT_TOPIC_STATUS, msg)


def on_message(client, userdata, msg):
    logger.error(f"Receive MQTT message from Topic: {msg.topic} without any handler, msg: {msg}")
