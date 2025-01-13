import logging
import time
from threading import Thread
from paramiko import SSHClient, AutoAddPolicy
from multiprocessing import Event
from typing import Dict, Optional


from ..connections.connections import Connection
from ..connections.redis import get_connection_info, update_connection_status
from ..core.process_controller import ProcessController
from .adb_log.log_manager import ADBLogManager
from ..core.rabbitmq.rabbitmq_utils import publish_message_by_shell


logger = logging.getLogger(f"logcollector_controller")


# 생각보다 일반화가 쉽지 않음.
class LogCollectorController:
    _instance = None
    actions = ["connect", "close", "config", "run_cmd", "run_cmd_with_timeout"]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False

        return cls._instance

    def __init__(self, services=["log_collector"]):
        if self.__initialized:
            return
        self.services = services
        self.conf = {}
        self.connection = None
        self.extern_stop_event = Event()
        self.extern_stop_event.clear()
        self.command_running_thread = None
        self.__initialized = True
        self.reconnect_required_event = Event()
        self.log_stop_event = Event()
        self.process_controller = ProcessController()
        self.monitor_connection_thread = None
        self.is_request_disconnect = False

    def dummy(self, body):
        logger.info(f"call dummy:{body}")

    def setup_response(self, body):
        # 셋업 응답시에 일단 연결 시도
        logger.info(f"call setup_response:{body}")
        return self.connect()

    def create_response(self, exchange, routing_key, msg, data):
        return {
            "exchange": exchange,
            "routing_key": routing_key,
            "message": {
                "msg": msg,
                "service": "shell",
                "data": data,
                "level": "info",
                "time": time.time(),
            },
        }

    def command(self, body):
        logger.info(f"call command:{body}")
        mode = body.get("mode")
        command = body.get("command")
        try:
            # 일단 ADB IP 연결 기준
            if self.connection is None or self.connection.device is None:
                self.connect()
                # return self.create_response("x.act.core", "res.stb.cmd", "command_response", {
                #     "mode": mode,
                #     "command": command,
                #     "log": "Connection is not established",
                # })
            result = self.connection.shell(command, timeout=5)
            return self.create_response(
                "x.act.core",
                "res.stb.cmd",
                "command_response",
                {
                    "mode": mode,
                    "command": command,
                    "log": result,
                },
            )
        except Exception as e:
            logger.error(f"Error command: {e}")
            return self.create_response(
                "x.act.core",
                "res.stb.cmd",
                "command_response",
                {
                    "mode": mode,
                    "command": command,
                    "log": f"Error occurred.",
                },
            )

    def initialize_log_collection(self):
        config = get_connection_info()
        mode = config.get("mode", "adb")

        self.reconnect_required_event.clear()
        self.log_stop_event.clear()
        self.is_request_disconnect = False

        if self.process_controller.is_alive():
            logger.info("Terminating all child processes")
            self.process_controller.terminate_process()

        if mode == "adb":
            adb_log_manager = ADBLogManager(
                adb_client=self.connection.client,
                reconnect_required_event=self.reconnect_required_event,
                stop_event=self.log_stop_event,
            )
            self.process_controller.start_process(
                target_func=adb_log_manager.durable_log_collection,
                args=(adb_log_manager.logcat_collector,),
            )
            self.process_controller.start_process(
                target_func=adb_log_manager.durable_log_collection,
                args=(adb_log_manager.cpu_memory_collector,),
            )

    # ADB/SSH 연결 해제
    def disconnect(self, data: Optional[Dict] = None):
        logger.info(f"Starting disconnect")

        self.is_request_disconnect = True

        try:
            device_config = get_connection_info()
            mode = device_config.get("mode")
            host = device_config.get("host")
            port = device_config.get("port")
            connection_config = get_connection_info("status_info")
            if mode == "adb" and self.connection is not None:
                adb_connection = connection_config.get("adb")
                if adb_connection != "connecting":
                    self.connection.adb_disconnect(host, port)
                self.log_stop_event.set()
                self.process_controller.terminate_process()
                logger.info("Terminating all child processes")
                enabled_logcat = False
                update_connection_status({"enable_logcat": int(enabled_logcat)})
                publish_message_by_shell(
                    target="logcat", data={"enable_logcat": int(enabled_logcat)}
                )
            # elif mode == "ssh" and self.connection is not None:
            #     try:
            #         client = SSHClient()
            #         client.set_missing_host_key_policy(AutoAddPolicy)
            #         client.close()
            #         logger.info(f"success ssh disconnect")
            #         # self.is_disconnect = True
            #         is_success = True
            #     except Exception as e:
            #         logger.error(f"ssh disconnect Unexpected error: {e}")
        except Exception as e:
            logger.error(f"adb disconnect Unexpected error: {e}")
            return self.create_response(
                "x.act.core",
                "res.stb.ctrl",
                "connect_response",
                {
                    "mode": mode,
                    "status": "connected",
                    "log": "Failed disconnect",
                },
            )

        return self.create_response(
            "x.act.core",
            "res.stb.ctrl",
            "connect_response",
            {
                "mode": mode,
                "status": "disconnected",
                "log": "Connection is disconnected",
            },
        )

    def reconnect(self, data: Optional[Dict] = None):
        logger.info("Starting reconnection")

        config = get_connection_info()
        mode = config.get("mode", "adb")
        host = config.get("host")
        port = config.get("port", 5555)
        username = config.get("username", None)
        password = config.get("password", None)

        self.is_request_disconnect = True

        publish_message_by_shell(
            target="connect",
            data={
                "mode": mode,
                "status": "disconnected",
                "log": "Connection is disconnected",
            },
        )

        self.disconnect()

        time.sleep(2)

        self.connection = Connection(mode, host, port, username, password)

        if self.connection.connected:
            try:
                self.initialize_log_collection()

                publish_message_by_shell(
                    target="connect",
                    data={
                        "mode": mode,
                        "status": "connected",
                        "log": "Connection is established",
                    },
                )
            except Exception as e:
                self.log_stop_event.set()
                logger.warning(f"Stopped reconnect by set log_stop_event")
                logger.error(f"Connection error in reconnect: {e}")

    # 참고: ssh connection 고려되지 않음
    def monitor_log_collection(self):
        logger.info(f"Starting monitor_log_collection")

        config = get_connection_info()
        mode = config.get("mode", "adb")
        retry_sec = config.get("retry", 10)  # second
        host = config.get("host")
        port = config.get("port", 5555)
        username = config.get("username", None)
        password = config.get("password", None)

        retry_count = 0

        while not self.log_stop_event.is_set():
            logger.info("Monitoring connection status...")
            if self.reconnect_required_event.is_set():
                try:
                    publish_message_by_shell(
                        target="connect",
                        data={
                            "mode": mode,
                            "status": "connecting",
                            "log": "Connection lost. Connecting...",
                        },
                    )

                    retry_count += 1
                    logger.info(
                        f"reconnecting by log stop event. retry_sec: {retry_sec}, retry_count: {retry_count}"
                    )

                    self.connection = Connection(mode, host, port, username, password)

                    if self.connection.connected:
                        self.initialize_log_collection()

                        logger.info(
                            f"Connection is established mode in monitor_connection: {mode}"
                        )
                        publish_message_by_shell(
                            target="connect",
                            data={
                                "mode": mode,
                                "status": "connected",
                                "log": "Connection is established",
                            },
                        )
                        self.reconnect_required_event.clear()
                        retry_count = 0

                    time.sleep(float(retry_sec))
                    continue

                except Exception as e:
                    self.log_stop_event.set()
                    logger.warning(f"Stopped monitor_connection by set log_stop_event")
                    logger.error(f"Connection error in monitor_connection: {e}")
                    break

            # 평상시 이벤트 확인 주기
            time.sleep(5)

        if not self.is_request_disconnect:
            try:
                enabled_logcat = False
                update_connection_status({"enable_logcat": int(enabled_logcat)})
                publish_message_by_shell(
                    target="logcat", data={"enable_logcat": int(enabled_logcat)}
                )
                publish_message_by_shell(
                    target="connect",
                    data={
                        "mode": mode,
                        "status": "disconnected",
                        "log": "Connection is disconnected",
                    },
                )
            except Exception as e:
                logger.error(f"Connection error in monitor_connection: {e}")
                pass
        logger.info(f"Ended monitor_connection")

    def connect(self, data: Optional[Dict] = None):
        logger.info("Starting connect")

        # TODO: 여기에 로그 parsing 해서 clickhouse로 올리는 작업을 추가
        # def consume_queue(queue: Queue, stop_event):
        #     print("====start  main_consume")
        #     while True:
        #         if stop_event.is_set or self.extern_stop_event.is_set():
        #             break
        #         if queue.empty():
        #             continue
        #         msg = queue.get()
        #         print(msg)
        #     print("====exit_main_consume")
        #     while True:
        #         if queue.empty():
        #             break
        #         msg = queue.get()
        #         print(msg)
        #     stop_event.set()
        #     self.extern_stop_event.set()
        #     print("=====exit_consume_queue")

        config = get_connection_info()
        mode = config.get("mode", "adb")
        host = config.get("host")
        port = config.get("port", 5555)
        username = config.get("username", None)
        password = config.get("password", None)

        self.connection = Connection(mode, host, port, username, password)

        if self.connection.connected:
            try:
                self.initialize_log_collection()

                logger.info(f"Connection is established mode: {mode}")

                if (
                    self.monitor_connection_thread is None
                    or not self.monitor_connection_thread.is_alive()
                ):
                    self.monitor_connection_thread = Thread(
                        target=self.monitor_log_collection,
                        daemon=True,
                    )
                    self.monitor_connection_thread.start()

                return self.create_response(
                    "x.act.core",
                    "res.stb.ctrl",
                    "connect_response",
                    {
                        "mode": mode,
                        "status": "connected",
                        "log": "Connection is established",
                    },
                )
            except Exception as e:
                logger.error(f"Connection is not established. error: {e}")
                return self.create_response(
                    "x.act.core",
                    "res.stb.ctrl",
                    "connect_response",
                    {
                        "mode": mode,
                        "status": "disconnected",
                        "log": "Connection is not established",
                    },
                )

        else:
            logger.error(
                f"Connection is not established. mode: {mode}, host: {host}, port: {port}, username: {username}, password: {password}"
            )
            return self.create_response(
                "x.act.core",
                "res.stb.ctrl",
                "connect_response",
                {
                    "mode": mode,
                    "status": "disconnected",
                    "log": "Connection is not established",
                },
            )

    def close(self, body):
        # 이러면 죽고 새로운 컨테이너가 올라오도록 한다.
        self.extern_stop_event.set()
        logger.info(f"call dummy:{body}")
        self.command_running_thread.join()
        self.command_running_thread = None
        self.extern_stop_event.clear()

    def run_cmd(self, body):
        if self.command_running_thread is None:
            cmd = body.get("cmd", "\n")
            timeout = body.get("timeout", None)
            self.command_running_thread = Thread(
                target=self.connection.run_command(cmd, timeout)
            ).run()  # 기다리지 않는다.
        logger.info(f"run_cmd:{body}")

    # 이건 그냥 처리 할 까?
    def run_cmd_with_timeout(self, body):
        logger.info(f"call dummy:{body}")

    def config(self, data: dict):
        is_succeed, err_msg = False, None
        if "service" in data:
            for service in self.services:
                if service in data["service"]:
                    self.conf = data["service"][service]
                    is_succeed = True
                else:
                    err_msg += f"there is no `service` like {service}"
                    pass
            is_succeed = True
        else:
            err_msg = "there is no `service` field in data"
        return is_succeed, err_msg

    # 처리 해야 할 것들...
    def control_connection(self, data):
        action_map = {
            "connect": self.connect,
            "close": self.close,
            "config": self.config,
            "run_cmd": self.run_cmd,
            "run_cmd_with_timeout": self.run_cmd_with_timeout,
        }
        action = data.get("action", None)
        is_succeed = False
        err_msg = None
        logger.info(f"action:{action}")

        if action in action_map:
            action_map[action](data)
        else:
            logger.error(f"{action} is not in {self.actions}!")
        is_succeed = True

        return (is_succeed, err_msg)
