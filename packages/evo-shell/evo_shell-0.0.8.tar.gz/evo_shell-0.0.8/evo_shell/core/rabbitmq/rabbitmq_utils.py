import logging
from contextlib import contextmanager
from time import time

from .rabbitmq_producer import RabbitMQProducer
from nlevoconn.rabbitmq_config import RabbitMQConfig
from nlevoutils.constant import ServiceType
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from nlevoutils.constant import ServiceType
from json import JSONDecodeError, loads

logger = logging.getLogger("rabbitmq")


@contextmanager
def get_rabbitmq_connection(host, port, username, password):
    credentials = PlainCredentials(username, password)
    connection = BlockingConnection(
        ConnectionParameters(host=host, port=port, credentials=credentials)
    )
    try:
        yield connection
    finally:
        connection.close()


def publish_message_to_rabbitmq(exchange: str, routing_key: str, body: dict):
    config = RabbitMQConfig(override=True)
    with get_rabbitmq_connection(
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        username=config.RABBITMQ_USER,
        password=config.RABBITMQ_PASSWORD,
    ) as connection:
        channel = connection.channel()
        producer = RabbitMQProducer(channel)
        producer.publish_message(exchange, routing_key, body)


def publish_message_by_shell(target: str, data: dict):
    exchange = ""
    routing_key = ""
    body = {
        "service": "shell",
        "data": data,
        "level": "info",
        "time": time(),
    }

    if target == "connect":
        exchange = "x.act.core"
        routing_key = "res.stb.ctrl"
        body["msg"] = "connect_response"
    elif target == "logcat":
        exchange = "x.act.core"
        routing_key = "res.logcat"
        body["msg"] = "adb_logcat_response"
    else:
        logger.warning(f"MQ Message target miss. target: {target}")
        return

    config = RabbitMQConfig(override=True)
    with get_rabbitmq_connection(
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        username=config.RABBITMQ_USER,
        password=config.RABBITMQ_PASSWORD,
    ) as connection:
        channel = connection.channel()
        producer = RabbitMQProducer(channel)
        producer.publish_message(exchange, routing_key, body)


def validate_log_collector_msg_body(body: dict):
    msg = body.get("msg", None)
    service = body.get("service", None)
    data = body.get("data", None)
    action = body.get("action", None)

    err_msgs = []
    if msg is None:
        _e1 = f"Invalid Message Field: Message is None"
        err_msgs.append(_e1)
        logger.warning(_e1)
    if service is None:
        _e2 = f"Invalid Service Field: {msg}: Service is None"
        err_msgs.append(_e2)
        logger.warning(_e2)
        # 아래 녀석의 위치는 약간 애매 하다.
        if service not in [my_service_type, ServiceType.SVC_CORE]:
            _e3 = f"Invalid Service: {service}"
            err_msgs.append(_e3)
            logger.warning(_e3)
    if data is None:
        _e4 = f"Invalid Data Field: {msg}: {service}: Data is None"
        err_msgs.append(_e4)
        logger.warning(_e4)
    if len(err_msgs) > 0:
        raise Exception(f"Invalid Message Body: {err_msgs}")
    return (msg, service, data, action)


def decode_body_bytes(body):
    err_msg = ""
    result = ""
    try:
        if isinstance(body, bytes):
            result = loads(body.decode().replace("'", '"'))
        else:
            logger.debug(msg=f"body type : {type(body)}")
            err_msg = "not a byte"
    except (JSONDecodeError, TypeError) as e:
        err_msg = f"json decode error {e}"
        raise Exception(err_msg)
    return result
