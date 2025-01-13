import os

import time

# import re
# from multiprocessing import Event
# from iterators import TimeoutIterator
# from datetime import datetime, timedelta
# import io
from ppadb.client import Client as AdbClient

# import socket
# import traceback


# def regex_match_dict(
#     pattern: re.Pattern[str],
#     text: str,
# ) -> dict[str, str] | None:
#     match_result = pattern.match(text)
#     if match_result:
#         return match_result.groupdict()
#     else:
#         return None


# class DeviceCommandHandler:
#     def __init__(self, client, timeout: float = 2):

#         self.mode = "adb"
#         self.host = "192.168.219.50"
#         self.port = "5555"

#         self.timeout = timeout

#         self.client = client
#         self.device = None
#         self.session_pool = {}

#         if self.mode == "adb":
#             self.device = client.device(f"{self.host}:{self.port}")

#     def initialize_session(self, command):
#         if self.mode == "adb":
#             self.session_pool[command] = self.create_connection()
#             if self.session_pool[command] is None:
#                 raise Exception("ADB Invalid IP or Port")

#     def create_connection(self) -> any:
#         start_time = time.time()
#         # time out을 설정하고, create_connection에 성공할 때 까지 계속 시도
#         while True:
#             try:
#                 time.sleep(0.1)
#                 return self.device.create_connection(timeout=self.timeout)
#             except Exception as e:
#                 if time.time() - start_time >= self.timeout:
#                     print(f"Create session error: {e}")
#                     return None

#     def is_session_valid(self, command):
#         if command not in self.session_pool:
#             return False

#         try:
#             session = self.session_pool[command]
#             if not session or not session.socket:
#                 return False

#             if session.socket.fileno() == -1:
#                 return False

#             return True
#         except Exception as e:
#             print(f"is_session_valid error: {e}")
#             return False

#     def ensure_valid_session(self, command):
#         try:
#             if not self.is_session_valid(command):
#                 if command in self.session_pool:
#                     try:
#                         self.session_pool[command].close()
#                     except Exception:
#                         pass

#                 self.initialize_session(command)
#             else:
#                 print("used prev session")

#         except Exception as e:
#             raise Exception(f"Session validation error: {e}")

#     def preprocess_stdout_stream(self, stdout: io.TextIOWrapper, command):
#         retry_count = 0
#         max_retries = 10
#         try:
#             while True:
#                 try:
#                     line = stdout.readline()
#                     if line == "":  # EOF 도달
#                         break
#                     retry_count = 0
#                     yield line

#                 except Exception as e:
#                     if retry_count >= max_retries:
#                         break
#                     print(f"Stream read error: {e}")
#                     retry_count += 1

#                     line = ""

#                     while True:
#                         try:
#                             if self.mode == "adb":
#                                 x = stdout.read(1).encode()
#                             else:
#                                 x = stdout.read(1)

#                             if not x:  # EOF 체크
#                                 return

#                             line += x.decode()
#                             if x == b"\n":
#                                 yield line
#                                 break

#                         except Exception as e:
#                             if retry_count >= max_retries:
#                                 break
#                             retry_count += 1
#                             print(f"Byte read error: {e}")
#                             time.sleep(0.1)
#         except Exception as e:
#             raise Exception(f"Error processing stdout: {e}")
#         finally:
#             # 리소스 정리
#             self.close_client(stdout, command)

#     def close_client(self, stdout: io.TextIOWrapper, command):
#         if self.mode == "ssh":
#             self.client.close()
#         elif self.mode == "adb":
#             stdout.close()
#             if self.session_pool[command]:
#                 self.session_pool[command].close()
#         del stdout

#     def exec_command(self, command: str):
#         if self.mode == "ssh":
#             stdin, stdout, stderr = self.client.exec_command(command)
#         elif self.mode == "adb":
#             self.ensure_valid_session(command)
#             cmd = "shell:{}".format(command)
#             self.session_pool[command].send(cmd)
#             socket = self.session_pool[command].socket
#             socket.settimeout(self.timeout)
#             stdout = socket.makefile()
#         return self.preprocess_stdout_stream(stdout, command)


# class ADBLogManager:
#     class LogConfig:
#         STREAM_TIMEOUT = 5  # sec
#         DATA_CLEAR_INTERVAL = 1  # sec

#         class Commands:
#             LOGCAT = "logcat -c; logcat -v long"
#             CPU = "top -n 1 -b"
#             MEMORY = "cat /proc/meminfo"

#         class Tables:
#             class Logcat:
#                 NAME = "default.logcat"
#                 COLUMNS = [
#                     "timestamp",
#                     "pid",
#                     "tid",
#                     "log_level",
#                     "module",
#                     "message",
#                     "process_name",
#                     "service",
#                     "type",
#                 ]

#             class Resource:
#                 NAME = "default.stb_info"
#                 COLUMNS = [
#                     "timestamp",
#                     "total_ram",
#                     "memory_usage",
#                     "used_ram",
#                     "free_ram",
#                     "available_ram",
#                     "total",
#                     "cpu_usage",
#                     "user",
#                     "kernel",
#                     "iowait",
#                     "irq",
#                     "softirq",
#                 ]

#     def __init__(self, client, stop_event: Event):
#         self.stop_event = stop_event
#         try:
#             self.command_handler = DeviceCommandHandler(client=client, timeout=10)
#         except Exception as e:
#             print(f"Construtor Error: {e}")
#             raise Exception(f"ADBLogManager Construtor Error: {e}")

#     def logcat_parse(self, log_cell_lines: str):
#         pattern = re.compile(
#             r"\[\s(?P<timestamp>\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s*(?P<pid>\d+)\s*:\s*(?P<tid>\d+)\s*(?P<log_level>[\w])\/(?P<module>.*?)\s*\]\n(?P<message>.*)"
#         )
#         match_dict = regex_match_dict(pattern=pattern, text=log_cell_lines)
#         # {'timestamp': '10-22 13:37:07.402', 'pid': '1766', 'tid': '6757', 'log_level': 'D', 'module': 'BluetoothLeScanner ', 'message': 'onScannerRegistered() - status=0 scannerId=7 mScannerId=0\n'}

#         if not match_dict:
#             print(f"=========Failed logcat parse. origin_line: {log_cell_lines}")
#             return None

#         # Amp 로그 처리를 위한 모듈 이름 파싱 함수 추가 (LG STB)
#         def parse_amp_module(module_str: str) -> str:
#             if "Amp" in module_str:
#                 try:
#                     # 1. ANSI 이스케이프 코드 제거
#                     clean_str = re.sub(r"\x1b\[\d+(?:;\d+)*m", "", module_str)

#                     # 2. 문자열 끝의 콜론만 제거
#                     if clean_str.endswith(":"):
#                         return clean_str[:-1]

#                     return clean_str.strip()

#                 except Exception as e:
#                     print(f"Error parsing Amp module: {e}")
#                     return module_str.strip()

#             return module_str.strip()

#         timestamp = match_dict["timestamp"]
#         full_date_string = f"{datetime.now().year}-{timestamp}+00:00"
#         parsed_timestamp = datetime.strptime(full_date_string, "%Y-%m-%d %H:%M:%S.%f%z")
#         utc_timestamp = parsed_timestamp - timedelta(hours=9)

#         pid = match_dict["pid"]
#         tid = match_dict["tid"]
#         log_level = match_dict["log_level"]
#         module = parse_amp_module(match_dict["module"])
#         message = match_dict["message"].strip()
#         process_name = "-"  # 보류
#         service = "log"
#         type = "adb"

#         if "@@" in log_cell_lines:
#             print(log_cell_lines)
#             print(f"module: {module}")

#         return (
#             utc_timestamp,
#             pid,
#             tid,
#             log_level,
#             module,
#             message,
#             process_name,
#             service,
#             type,
#         )

#     # 해당 함수의 직접적인 역할은 db insert, 재연결 (collector에서 하면 안됨. cpu_ram의 재연결 동작이 분리되어 관리 복잡해짐)
#     def logcat_collector(self):
#         LOGCAT_START_PATTERN = r"\[ \d{2}-\d{2}"

#         # clickhouse_client = clickhouse_connect.get_client(
#         #     host="clickhouse", port=8123, username="admin", password=".nextlab6318!"
#         # )

#         stdout = self.command_handler.exec_command(command="logcat -c; logcat -v long")
#         timeout_stdout = TimeoutIterator(
#             stdout, timeout=self.LogConfig.STREAM_TIMEOUT, sentinel=None
#         )

#         start_time = time.time()
#         last_flush_time = time.time()
#         logcat_data = []
#         log_cell_lines = ""
#         count = 0

#         for line in timeout_stdout:
#             if self.stop_event.is_set():
#                 break

#             # 클릭하우스 인서트
#             current_time = time.time()
#             if current_time - last_flush_time >= self.LogConfig.DATA_CLEAR_INTERVAL:
#                 try:
#                     last_flush_time = time.time()
#                     logcat_data.clear()
#                 except Exception as e:
#                     print(f"logcat insert clickhouse error: {e}")
#                     break

#             # Timeout 안걸렸을 때
#             if line is not None:
#                 if log_cell_lines != "" and re.match(LOGCAT_START_PATTERN, line):
#                     # log_cell_lines이 완성됨. 파싱해
#                     result = self.logcat_parse(log_cell_lines)
#                     if result is not None:
#                         print(f"append time: {time.time()}")
#                         logcat_data.append(result)
#                     log_cell_lines = ""

#                 log_cell_lines += line

#         print(f"logcat end time: {time.time()}")

#     def cpu_top_parse(self, line: str):
#         # MemTotal:        3067816 kB
#         # MemFree:          286352 kB
#         pattern = re.compile(
#             r"^(?P<cpu_total>\d+)%cpu\s+(?P<user>\d+)%user\s+(?P<nice>\d+)%nice\s+(?P<sys>\d+)%sys\s+(?P<idle>\d+)%idle\s+(?P<iow>\d+)%iow\s+(?P<irq>\d+)%irq\s+(?P<sirq>\d+)%sirq"
#         )
#         match_dict = regex_match_dict(pattern=pattern, text=line)

#         if match_dict is None:
#             return None

#         cpu_total = int(match_dict["cpu_total"])
#         idle = int(match_dict["idle"])
#         cpu_usage = cpu_total - idle

#         return [
#             str(cpu_total),
#             str(cpu_usage),
#             match_dict["user"],
#             match_dict["sys"],
#             match_dict["iow"],
#             match_dict["irq"],
#             match_dict["sirq"],
#         ]

#     def memory_parse(self, line: str):
#         # MemTotal:        3067816 kB
#         # MemFree:          286352 kB
#         # MemAvailable:    2686352 kB
#         patterns = [
#             re.compile(r"^MemTotal:\s+(?P<total>\d+)"),
#             re.compile(r"^MemFree:\s+(?P<free>\d+)"),
#             re.compile(r"^MemAvailable:\s+(?P<available>\d+)"),
#         ]

#         if line.startswith("MemTotal"):
#             match_dict = regex_match_dict(pattern=patterns[0], text=line)
#             total_byte = int(match_dict["total"]) * 1024
#             return {"total_byte": total_byte}

#         if line.startswith("MemFree"):
#             match_dict = regex_match_dict(pattern=patterns[1], text=line)
#             free_byte = int(match_dict["free"]) * 1024
#             return {"free_byte": free_byte}

#         if line.startswith("MemAvailable"):
#             match_dict = regex_match_dict(pattern=patterns[2], text=line)
#             available_byte = int(match_dict["available"]) * 1024
#             return {"available_byte": available_byte}

#         return None

#     def cpu_info(self):
#         try:
#             stdout = self.command_handler.exec_command(
#                 command=self.LogConfig.Commands.CPU
#             )
#             timeout_stdout = TimeoutIterator(
#                 stdout, timeout=self.LogConfig.STREAM_TIMEOUT, sentinel=None
#             )
#             for line in timeout_stdout:
#                 result = self.cpu_top_parse(line)
#                 if result is not None:
#                     return result

#             return None
#         except Exception as e:
#             print(f"cpu_info error: {e}")
#             return None

#     def memory_info(self):
#         memory_data = {}

#         collect_count = 0
#         try:
#             stdout = self.command_handler.exec_command(
#                 command=self.LogConfig.Commands.MEMORY
#             )
#             timeout_stdout = TimeoutIterator(
#                 stdout, timeout=self.LogConfig.STREAM_TIMEOUT, sentinel=None
#             )
#             for line in timeout_stdout:
#                 if collect_count >= 3:
#                     break

#                 result = self.memory_parse(line)
#                 if result is not None:
#                     collect_count += 1
#                     memory_data = dict(**memory_data, **result)

#             if collect_count == 3:
#                 total_byte = memory_data["total_byte"]
#                 free_byte = memory_data["free_byte"]
#                 available_byte = memory_data["available_byte"]
#                 used_ram_byte = total_byte - available_byte
#                 usage = round(used_ram_byte / total_byte * 100, 1)
#                 return [
#                     str(total_byte),
#                     str(usage),
#                     str(used_ram_byte),
#                     str(available_byte),
#                     str(free_byte),
#                 ]

#             return None
#         except Exception as e:
#             print(f"cpu_info error: {e}")
#             return None

#     def cpu_memory_collector(self):
#         print("Starting cpu_memory_collector")
#         # clickhouse_client = clickhouse_connect.get_client(
#         #     host=self.clickhouse_host,
#         #     port=self.clickhouse_port,
#         #     username=self.clickhouse_username,
#         #     password=self.clickhouse_password,
#         # )

#         while True:

#             memory_info = self.memory_info()
#             cpu_info = self.cpu_info()

#             print("==========")
#             print(memory_info)
#             print("==========")
#             print(cpu_info)
#             print("==========")

#             # if None in [memory_info, cpu_info]:
#             #     print(
#             #         f"cpu or memory is None. memory_info: {memory_info}, cpu_info: {cpu_info}"
#             #     )
#             #     break

#             # local_time = datetime.now()
#             # utc_time = local_time.astimezone(timezone.utc)
#             # timestamp = utc_time.replace(tzinfo=None)
#             # combined_info = [timestamp] + memory_info + cpu_info

#             # try:
#             #     insert_to_clickhouse(
#             #         clickhouse=clickhouse_client,
#             #         table=resource_table_name,
#             #         data=[tuple(combined_info)],
#             #         column=resource_columns_name,
#             #     )
#             # except Exception as e:
#             #     self.system_error_event.set()
#             #     logger.error("cpu_memory_collector set system_error_event")
#             #     logger.error(f"stb_info insert clickhouse error: {e}")
#             #     break

#             time.sleep(1)

#         logger.info("Ended cpu_memory_collector")

#     def durable_log_collection(self):
#         retry_count = 0
#         max_retries = 10

#         # collector_name = collector.__name__
#         collector_name = "logcat"

#         while True:
#             # self.cpu_memory_collector()
#             self.logcat_collector()

#             # collector()
#             # try:
#             #     # 수집 시작
#             # except Exception as e:
#             #     retry_count += 1
#             #     if retry_count >= max_retries:
#             #         self.stop_event.set()
#             #         print(
#             #             f"{collector_name} failed after {max_retries} retries - triggering log collection system shutdown"
#             #         )
#             #         print(f"Critical {collector_name} error: {e}")
#             #         break

#             # if self.stop_event.is_set():
#             #     print(
#             #         f"Close durable_log_collection {collector_name} by stop_event"
#             #     )
#             #     break

#             # print(f"{collector_name} close")

#             time.sleep(10)

#             # 재연결 시도
#             print("Checking ADB device connection status...")

#             # if self.check_device_connection():
#             #     print(f"Device connection confirmed, restarting {collector_name}")
#             #     continue

#             # print(
#             #     "Device connection check failed - setting stop event to trigger process termination",
#             # )
#             # break


if __name__ == "__main__":
    # mode = "adb"
    # host = "192.168.219.50"
    # port = "5555"
    # adb_stop_event = Event()

    os.system("adb kill-server")
    os.system("adb start-server")
    os.system("adb tcpip 5555")
    time.sleep(1)
    client = AdbClient(host="127.0.0.1", port=5037)
    result = client.remote_connect("192.168.100.148", 5555)
    print(f"=={result}")

    # adb_log_manager = ADBLogManager(client=client, stop_event=adb_stop_event)
    # adb_log_manager.durable_log_collection()

    # result = os.system("adb tcpip 5555")
    # result = os.system("adb tcpip 5555")
