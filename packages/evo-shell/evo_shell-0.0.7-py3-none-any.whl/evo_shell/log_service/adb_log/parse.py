import logging
import re
from datetime import datetime, timedelta

from ...util.common import regex_match_dict

logger = logging.getLogger("adb_log_manager")


# Amp 로그 처리를 위한 모듈 이름 파싱 함수 추가 (LG STB)
def parse_amp_module_logcat(module_str: str) -> str:
    if "Amp" in module_str:
        try:
            # 1. ANSI 이스케이프 코드 제거
            clean_str = re.sub(r"\x1b\[\d+(?:;\d+)*m", "", module_str)

            # 2. 문자열 끝의 콜론만 제거
            if clean_str.endswith(":"):
                # module: [54645.441] Amp2@@[MODULE_SNDSRV:snd_port_bind_aout_path():10116]
                return clean_str[:-1]

            return clean_str.strip()

        except Exception as e:
            logger.error(f"Error parsing logcat Amp module: {e}")
            return module_str.strip()

    return module_str.strip()


def logcat_parse(line: str):
    if not line.strip():
        return None
    # [ 12-15 15:44:47.200   811:  917 W/ProcessStats ] Tracking association SourceState{f6d08fe com.google.android.katniss:search/10104 BTopFgs #236205} whose proc state 2 is better than process ProcessState{3c74d84 com.google.android.gms.persistent/10108 pkg=com.google.android.gms} proc state 3 (243 skipped)
    pattern = re.compile(
        r"\[\s(?P<timestamp>\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3})\s*(?P<pid>\d+)\s*:\s*(?P<tid>\d+)\s*(?P<log_level>[\w])\/(?P<module>.*?)\s*\]\n(?P<message>.*)"
    )
    match_dict = regex_match_dict(pattern=pattern, text=line)
    # {'timestamp': '10-22 13:37:07.402', 'pid': '1766', 'tid': '6757', 'log_level': 'D', 'module': 'BluetoothLeScanner ', 'message': 'onScannerRegistered() - status=0 scannerId=7 mScannerId=0\n'}

    if match_dict is None:
        logger.warning(f"Failed logcat parse. origin_line: {line}")
        return None

    timestamp = match_dict["timestamp"]
    full_date_string = f"{datetime.now().year}-{timestamp}+00:00"
    parsed_timestamp = datetime.strptime(full_date_string, "%Y-%m-%d %H:%M:%S.%f%z")
    utc_timestamp = parsed_timestamp - timedelta(hours=9)

    pid = match_dict["pid"]
    tid = match_dict["tid"]
    log_level = match_dict["log_level"]
    module = parse_amp_module_logcat(match_dict["module"])
    message = match_dict["message"].strip()
    process_name = "-"  # 보류
    service = "log"
    type = "adb"

    return (
        utc_timestamp,
        pid,
        tid,
        log_level,
        module,
        message,
        process_name,
        service,
        type,
    )


def cpu_top_parse(line: str):
    if not line.strip():
        return None
    # MemTotal:        3067816 kB
    # MemFree:          286352 kB
    pattern = re.compile(
        r"^(?P<cpu_total>\d+)%cpu\s+(?P<user>\d+)%user\s+(?P<nice>\d+)%nice\s+(?P<sys>\d+)%sys\s+(?P<idle>\d+)%idle\s+(?P<iow>\d+)%iow\s+(?P<irq>\d+)%irq\s+(?P<sirq>\d+)%sirq"
    )
    match_dict = regex_match_dict(pattern=pattern, text=line)

    if match_dict is None:
        return None

    cpu_total = int(match_dict["cpu_total"])
    idle = int(match_dict["idle"])
    cpu_usage = cpu_total - idle

    return [
        str(cpu_total),
        str(cpu_usage),
        match_dict["user"],
        match_dict["sys"],
        match_dict["iow"],
        match_dict["irq"],
        match_dict["sirq"],
    ]


def memory_parse(line: str):
    if not line.strip():
        return None
    # MemTotal:        3067816 kB
    # MemFree:          286352 kB
    # MemAvailable:    2686352 kB
    patterns = [
        re.compile(r"^MemTotal:\s+(?P<total>\d+)"),
        re.compile(r"^MemFree:\s+(?P<free>\d+)"),
        re.compile(r"^MemAvailable:\s+(?P<available>\d+)"),
    ]

    if line.startswith("MemTotal"):
        match_dict = regex_match_dict(pattern=patterns[0], text=line)
        total_byte = int(match_dict["total"]) * 1024
        return {"total_byte": total_byte}

    if line.startswith("MemFree"):
        match_dict = regex_match_dict(pattern=patterns[1], text=line)
        free_byte = int(match_dict["free"]) * 1024
        return {"free_byte": free_byte}

    if line.startswith("MemAvailable"):
        match_dict = regex_match_dict(pattern=patterns[2], text=line)
        available_byte = int(match_dict["available"]) * 1024
        return {"available_byte": available_byte}

    return None
