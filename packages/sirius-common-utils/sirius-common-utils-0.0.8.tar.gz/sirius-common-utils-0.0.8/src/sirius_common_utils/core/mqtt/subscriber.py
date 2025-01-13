import json
import traceback
from typing import Callable, Dict

from app.mqtt.connection import get_client

from sirius_common_utils.core.logging import logging, log_name

logger = logging.get_logger(log_name.LOG_COMMON_CORE_MQTT)


def init():
    return

def subscribe(topic_name: str, qos: int, handler: Callable[[Dict], None]):
    client = get_client()

    def message_callback(client, user_data, msg):
        logger.debug(f"Receive message from MQTT Topic {topic_name}: {msg.payload}")

        data = None
        try:
            payload = msg.payload.decode()
            data = json.loads(payload)
        except Exception as e:
            logger.error(f"Cannot parse the JSON message from MQTT Topic {topic_name}, msg: {msg.payload}, exception: {e}")

        try:
            handler(data)
        except Exception as e:
            logger.error(f"Handle MQTT Topic {topic_name}, msg: {msg.payload} with error: {e}")
            traceback.print_exc()

    client.message_callback_add(topic_name, message_callback)
    client.subscribe(topic_name, qos)
    logger.info(f"subscribe MQTT topic: {topic_name}")

