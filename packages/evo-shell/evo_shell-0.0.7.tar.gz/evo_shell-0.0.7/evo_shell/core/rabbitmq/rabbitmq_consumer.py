import logging
from time import sleep
from abc import ABC, abstractmethod
from nlevoutils.constant import Exchange, RoutingKey
from json import JSONDecodeError
from retry import retry
from pika import DeliveryMode, BasicProperties, exceptions as pika_exceptions

from nlevoconn.rabbitmq import RabbitMQConnection
from .rabbitmq_utils import publish_message_to_rabbitmq
from ..generator.message_generator import setup_message


logger = logging.getLogger("rabbitmq")


class RabbitMQConsumerBase(ABC):
    """
    RabbitMQ 연결과 연결 후 첫 Setup Process를 수행
    이후 데이터 처리는 상속받은 Consumer의 process_message method에서 수행
    """

    def __init__(
        self, binding_info: dict, host: str, port: str, username: str, password: str
    ):
        self.binding_info = binding_info
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.channel = {}
        self.queue_name = {}
        self.setup = False

    @abstractmethod
    def process_message(self, channel, method, properties, body):
        """
            The class defines an abstract method called process_message.

            Subclasses must override this method \
            to provide custom processing logic for received messages.
        """
        print("Received message:", body.decode())
        pass

    def on_message_callback(self, channel, method, properties, body):
        """
            The on_message_callback method is responsible for invoking \
            the process_message method of the subclass\
            and acknowledging the message.

            Within the on_message_callback method, \
            the process_message method is called, \
            passing the received parameters. \
            After processing the message, \
            the consumer acknowledges it using channel.basic_ack to inform \
            RabbitMQ that the message has been successfully processed.
        """
        self.process_message(channel, method, properties, body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    @retry(pika_exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
    def consume(self):
        with RabbitMQConnection(
            self.host, self.port, self.username, self.password
        ) as connection:
            # binding 할 exchange, routing_key 등을 설정
            self.channel = connection.get_channel()
            for exchange, routing_key in self.binding_info.items():
                self.channel.exchange_declare(
                    exchange=exchange, exchange_type="topic", auto_delete=False
                )
                result = self.channel.queue_declare(queue="", exclusive=True)
                self.queue_name[exchange] = result.method.queue

                for _routing_key in routing_key:
                    self.channel.queue_bind(
                        queue=self.queue_name[exchange],
                        exchange=exchange,
                        routing_key=_routing_key,
                    )
            try:
                _retries = 0
                while _retries < 10:
                    if self.setup is True:
                        break
                    # setup을 진행할 channel 을 생성
                    # setup_channel = connection.get_channel()
                    # setup request
                    publish_message_to_rabbitmq(
                        exchange=Exchange.MODULE_TO_CORE,
                        routing_key=RoutingKey.SETUP_REQ,
                        body=setup_message(),
                    )

                    # 5초 timeout으로 consume
                    for method, _, body in self.channel.consume(
                        self.queue_name[Exchange.FOR_SYSTEM_SETUP], inactivity_timeout=5
                    ):
                        if method is not None and body is not None:
                            logger.info(
                                f"Received {method.routing_key} message:{body.decode()}"
                            )
                            self.channel.basic_ack(method.delivery_tag)
                            # 설정 응답인 경우에만 각 설정 항목을 화면에 출력
                            if method.routing_key == RoutingKey.SETUP_RESP:
                                try:
                                    # 설정을 읽어 json 형태로 저장
                                    if isinstance(body, bytes):
                                        properties = BasicProperties(
                                            content_type="application/json",
                                            content_encoding="utf-8",
                                            delivery_mode=DeliveryMode.Persistent,
                                        )
                                        self.process_message(
                                            self.channel,
                                            method,
                                            properties,
                                            body,
                                        )
                                        self.setup = True
                                    else:
                                        logger.info(f"body type : {type(body)}")
                                except JSONDecodeError as e:
                                    # json 변환 시 에러
                                    # 에러 메시지를 추가해 재요청
                                    publish_message_to_rabbitmq(
                                        exchange=Exchange.MODULE_TO_CORE,
                                        routing_key=RoutingKey.SETUP_REQ,
                                        body=setup_message(e),
                                    )
                                except TypeError as e:
                                    # json 변환 시 에러
                                    # 에러 메시지를 추가해 재요청
                                    publish_message_to_rabbitmq(
                                        exchange=Exchange.MODULE_TO_CORE,
                                        routing_key=RoutingKey.SETUP_REQ,
                                        body=setup_message(e),
                                    )
                                break
                            else:
                                logger.warning(
                                    f"Incorrect Message Routing-Key: {method.routing_key}"
                                )
                                self.setup = False
                        else:
                            # 5초 간격 setup 데이터를 요청
                            publish_message_to_rabbitmq(
                                exchange=Exchange.MODULE_TO_CORE,
                                routing_key=RoutingKey.SETUP_REQ,
                                body=setup_message(),
                            )
                if self.setup:
                    logger.info("Success setup")
                    self.channel.cancel()

                    # setup 이 완료되고 consumer가 동작
                    for exchange, _ in self.binding_info.items():
                        self.channel.basic_consume(
                            queue=self.queue_name[exchange],
                            auto_ack=False,
                            on_message_callback=self.on_message_callback,
                        )
                        logger.info(
                            f"Started consuming messages from queue: {self.queue_name[exchange]}"
                        )
                    self.channel.start_consuming()
                else:
                    logger.warning("Failed setup")
                    # setup 이 실패하고, retry 10회
                    _retries += 1
                    wait_time = 2**_retries
                    logger.warning(f"Retrying in {wait_time} seconds...")
                    sleep(wait_time)
            except pika_exceptions.ConnectionClosedByBroker:
                logger.error("Connection closed by broker.")
            except KeyboardInterrupt:
                for exchange, _ in self.binding_info.items():
                    self.channel.stop_consuming()
            finally:
                logger.info("Consumer stopped...")
