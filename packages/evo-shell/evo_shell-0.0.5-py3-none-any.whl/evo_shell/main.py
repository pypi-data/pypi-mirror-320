import logging

from nlevoutils.log_organizer import LogOrganizer
from nlevoutils.exceptions import handle_errors
from .core.core_consumer import CoreConsumer
from nlevoconn.rabbitmq_config import RabbitMQConfig


logger = logging.getLogger("main")


@handle_errors
def main():
    config = RabbitMQConfig(override=True)

    CoreConsumer(
        binding_info=config.LOG_COLLECTOR_BINDING_INFO,
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        username=config.RABBITMQ_USER,
        password=config.RABBITMQ_PASSWORD,
    ).consume()


if __name__ == "__main__":
    try:
        log_organizer = LogOrganizer(name="shell")
        log_organizer.set_stream_logger("main")
        log_organizer.set_stream_logger("rabbitmq")
        log_organizer.set_stream_logger("logcollector_controller")
        log_organizer.set_stream_logger("connection")
        log_organizer.set_stream_logger("process_controller")
        log_organizer.set_stream_logger("device_command_handler")
        log_organizer.set_stream_logger("adb_log_manager")

        logger.info("Start shell container")
        main()

    finally:
        logger.info("Close shell container")
        log_organizer.close()
