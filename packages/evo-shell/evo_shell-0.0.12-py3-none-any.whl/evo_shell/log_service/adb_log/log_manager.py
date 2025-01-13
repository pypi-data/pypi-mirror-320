import logging
import time
import re
from os import getenv
from multiprocessing import Event
from iterators import TimeoutIterator
import clickhouse_connect
from datetime import datetime, timezone
from nlevoconn.rabbitmq_config import RabbitMQConfig
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

from ...core.rabbitmq.rabbitmq_producer import RabbitMQProducer
from ...connections.redis import update_connection_status
from ...core.rabbitmq.rabbitmq_utils import publish_message_by_shell
from ..device_command_handler import DeviceCommandHandler
from ...util.common import insert_to_clickhouse
from .parse import logcat_parse, cpu_top_parse, memory_parse

logger = logging.getLogger("adb_log_manager")


class ADBLogManager:
    class LogConfig:
        STREAM_TIMEOUT = 5  # sec
        DATA_CLEAR_INTERVAL = 1  # sec

        class Commands:
            LOGCAT = "logcat -c; logcat -v long"
            CPU = "top -n 1 -b"
            MEMORY = "cat /proc/meminfo"

        class Tables:
            class Logcat:
                NAME = "default.logcat"
                COLUMNS = [
                    "timestamp",
                    "pid",
                    "tid",
                    "log_level",
                    "module",
                    "message",
                    "process_name",
                    "service",
                    "type",
                ]

            class Resource:
                NAME = "default.stb_info"
                COLUMNS = [
                    "timestamp",
                    "total_ram",
                    "memory_usage",
                    "used_ram",
                    "free_ram",
                    "available_ram",
                    "total",
                    "cpu_usage",
                    "user",
                    "kernel",
                    "iowait",
                    "irq",
                    "softirq",
                ]

    def __init__(self, adb_client, reconnect_required_event: Event, stop_event: Event):
        self.clickhouse_host = getenv(key="CLICKHOUSE_HOST")
        self.clickhouse_port = getenv(key="CLICKHOUSE_PORT")
        self.clickhouse_username = getenv(key="CLICKHOUSE_USERNAME")
        self.clickhouse_password = getenv(key="CLICKHOUSE_PASSWORD")
        if None in [
            self.clickhouse_host,
            self.clickhouse_port,
            self.clickhouse_username,
            self.clickhouse_password,
        ]:
            raise Exception(
                f"ClickHouse authentication failed: Required environment variables not set"
            )

        self.reconnect_required_event = reconnect_required_event
        self.stop_event = stop_event
        self.timeout = 10

        try:
            self.command_handler = DeviceCommandHandler(
                client=adb_client, timeout=self.timeout
            )
        except Exception as e:
            logger.error(f"Construtor Error: {e}")
            raise Exception(f"ADBLogManager Construtor Error: {e}")

    # device 연결 상태 점검
    def check_device_connection(self):
        try:
            device = self.command_handler.device
            session = device.create_connection(timeout=self.timeout)
            cmd = "shell:echo good"
            session.send(cmd)
            socket = session.socket
            socket.settimeout(self.timeout)
            stdout = socket.makefile()
            response = stdout.readline().strip()
            logger.info(f"ADB Device status: {response}")
            session.close()
            return response == "good"
        except Exception as e:
            logger.error(f"device disconnect: {e}")
            return False

    def durable_log_collection(self, collector):
        retry_count = 0
        max_retries = 10

        collector_name = collector.__name__

        while not self.stop_event.is_set():
            try:
                # 수집 시작
                collector()
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    self.stop_event.set()
                    logger.warning(
                        f"{collector_name} failed after {max_retries} retries - triggering log collection system shutdown"
                    )
                    logger.error(f"Critical {collector_name} error: {e}")
                    break

            if self.stop_event.is_set():
                logger.info(
                    f"Close durable_log_collection {collector_name} by stop_event"
                )
                break

            logger.info(f"{collector_name} close")

            time.sleep(0.1)

            # 재연결 시도
            logger.warning("Checking ADB device connection status...")

            if self.check_device_connection():
                logger.info(f"Device connection confirmed, restarting {collector_name}")
                continue

            logger.error(
                "Device connection check failed - setting stop event to trigger process termination",
            )
            self.reconnect_required_event.set()
            break

    # parse, db insert, except reconnection
    def logcat_collector(self):
        logger.info("Starting logcat_collector")
        try:
            clickhouse_client = clickhouse_connect.get_client(
                host=self.clickhouse_host,
                port=self.clickhouse_port,
                username=self.clickhouse_username,
                password=self.clickhouse_password,
            )

            start_pattern = r"\[ \d{2}-\d{2}"

            last_flush_time = time.time()
            logcat_data = []
            log_cell_lines = ""

            stdout = self.command_handler.exec_command(
                command=self.LogConfig.Commands.LOGCAT
            )
            timeout_stdout = TimeoutIterator(
                stdout, timeout=self.timeout, sentinel=None
            )

            if None in [stdout, timeout_stdout]:
                logger.error("stdout, timeout_stdout is None")
                return

            enabled_logcat = True
            update_connection_status({"enable_logcat": int(enabled_logcat)})
            publish_message_by_shell(
                target="logcat", data={"enable_logcat": int(enabled_logcat)}
            )

            for line in timeout_stdout:
                if self.stop_event.is_set() or self.reconnect_required_event.is_set():
                    break

                # 1초 주기 db insert
                current_time = time.time()
                if (
                    len(logcat_data) > 0
                    and current_time - last_flush_time
                    >= self.LogConfig.DATA_CLEAR_INTERVAL
                ):
                    try:
                        insert_to_clickhouse(
                            clickhouse=clickhouse_client,
                            table=self.LogConfig.Tables.Logcat.NAME,
                            data=logcat_data,
                            column=self.LogConfig.Tables.Logcat.COLUMNS,
                        )
                        last_flush_time = time.time()
                        logcat_data.clear()
                    except Exception as e:
                        self.stop_event.set()
                        logger.warning("logcat set stop_event")
                        logger.error(f"logcat insert clickhouse error: {e}")
                        break

                # Timeout 안걸렸을 때
                if line is not None:
                    if log_cell_lines != "" and re.match(start_pattern, line):
                        result = logcat_parse(log_cell_lines)
                        if result is not None:
                            logcat_data.append(result)
                        log_cell_lines = ""

                    log_cell_lines += line
        except Exception as e:
            logger.error(f"logcat_collector error: {e}")
        finally:
            enabled_logcat = False
            update_connection_status({"enable_logcat": int(enabled_logcat)})
            publish_message_by_shell(
                target="logcat", data={"enable_logcat": int(enabled_logcat)}
            )
            logger.info("Ended logcat_collector")

    def cpu_info(self):
        try:
            stdout = self.command_handler.exec_command(
                command=self.LogConfig.Commands.CPU
            )
            timeout_stdout = TimeoutIterator(
                stdout, timeout=self.timeout, sentinel=None
            )
            for line in timeout_stdout:
                if self.stop_event.is_set() or self.reconnect_required_event.is_set():
                    break

                result = cpu_top_parse(line)
                if result is not None:
                    return result

            return None
        except Exception as e:
            logger.error(f"cpu_info error: {e}")
            return None

    def memory_info(self):
        memory_data = {}

        collect_count = 0
        try:
            stdout = self.command_handler.exec_command(
                command=self.LogConfig.Commands.MEMORY
            )
            timeout_stdout = TimeoutIterator(
                stdout, timeout=self.timeout, sentinel=None
            )
            for line in timeout_stdout:
                if self.stop_event.is_set() or self.reconnect_required_event.is_set():
                    break

                if collect_count >= 3:
                    break

                result = memory_parse(line)
                if result is not None:
                    collect_count += 1
                    memory_data = dict(**memory_data, **result)

            if collect_count == 3:
                total_byte = memory_data["total_byte"]
                free_byte = memory_data["free_byte"]
                available_byte = memory_data["available_byte"]
                used_ram_byte = total_byte - available_byte
                usage = round(used_ram_byte / total_byte * 100, 1)
                return [
                    str(total_byte),
                    str(usage),
                    str(used_ram_byte),
                    str(available_byte),
                    str(free_byte),
                ]

            return None
        except Exception as e:
            logger.error(f"cpu_info error: {e}")
            return None

    def cpu_memory_collector(self):
        logger.info("Starting cpu_memory_collector")

        try:
            config = RabbitMQConfig(override=True)
            credentials = PlainCredentials(
                config.RABBITMQ_USER, config.RABBITMQ_PASSWORD
            )
            connection = BlockingConnection(
                ConnectionParameters(
                    host=config.RABBITMQ_HOST,
                    port=config.RABBITMQ_PORT,
                    credentials=credentials,
                )
            )
            channel = connection.channel()
            producer = RabbitMQProducer(channel)
            clickhouse_client = clickhouse_connect.get_client(
                host=self.clickhouse_host,
                port=self.clickhouse_port,
                username=self.clickhouse_username,
                password=self.clickhouse_password,
            )

            while True:
                memory_info = self.memory_info()
                cpu_info = self.cpu_info()

                if None in [memory_info, cpu_info]:
                    logger.warning(
                        f"cpu or memory is None. memory_info: {memory_info}, cpu_info: {cpu_info}"
                    )
                    break

                local_time = datetime.now()
                utc_time = local_time.astimezone(timezone.utc)
                timestamp = utc_time.replace(tzinfo=None)
                combined_info = [timestamp] + memory_info + cpu_info
                try:
                    insert_to_clickhouse(
                        clickhouse=clickhouse_client,
                        table=self.LogConfig.Tables.Resource.NAME,
                        data=[tuple(combined_info)],
                        column=self.LogConfig.Tables.Resource.COLUMNS,
                    )
                    producer.publish_message(
                        exchange="x.act.core",
                        routing_key="res.resource",
                        body={
                            "msg": "stb_resource_response",
                            "service": "shell",
                            "data": {
                                "cpu_usage": cpu_info[1].split(".")[0],
                                "memory_usage": memory_info[1].split(".")[0],
                            },
                            "level": "info",
                            "time": time.time(),
                        },
                    )
                except Exception as e:
                    self.stop_event.set()
                    raise Exception(f"stb_info set stop_event. error: {e}")

                time.sleep(1)
        except Exception as e:
            logger.error(f"cpu_memory_collector error: {e}")
        finally:
            logger.info("Ended cpu_memory_collector")
