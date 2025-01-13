import logging
from json import dumps

from pika import BasicProperties, DeliveryMode
from pika import exceptions as pika_exceptions

logger = logging.getLogger("rabbitmq")


class RabbitMQProducer:
    def __init__(self, channel):
        self.channel = channel

    def publish_message(
        self, exchange: str, routing_key: str, body: dict, correlation_id=None
    ):
        if self.channel is not None:
            try:
                self.channel.exchange_declare(
                    exchange=exchange, exchange_type="topic", auto_delete=False
                )
                message = dumps(body)
                properties = BasicProperties(
                    content_type="application/json",
                    content_encoding="utf-8",
                    delivery_mode=DeliveryMode.Persistent,
                    correlation_id=correlation_id,
                )
                self.channel.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=message,
                    properties=properties,
                )
                logger.info(
                    f'Message sent to exchange: {exchange} with routing_key: {routing_key}')
            except pika_exceptions.ConnectionClosedByBroker:
                logger.error(
                    "Connection closed by broker. Failed to publish the message"
                )
            except Exception as e:
                logger.exception("Unexpected error occurred during message publishing")
        else:
            logger.warning("Failed to obtain a channel for publishing the message")
