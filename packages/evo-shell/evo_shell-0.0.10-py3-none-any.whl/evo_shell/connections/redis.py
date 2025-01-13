import redis

from ..core.config import settings


def get_connection_info(key: str = "device_connection_info"):
    redis_conn = None
    # 반환 원형.
    device_connection_info = {
        "mode": "adb",
        "host": "",
        "port": 5555,
        "username": "",
        "password": "",
        "retry": 1,
    }
    try:
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True,
        )
        device_connection_info = redis_conn.hgetall(key)
    except Exception as e:
        raise e
    finally:
        if redis_conn:
            redis_conn.close()
    return device_connection_info


def set_connection_info(info):
    redis_conn = None
    try:
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True,
        )
        redis_conn.hmset("device_connection_info", info)
    except Exception as e:
        raise e
    finally:
        if redis_conn:
            redis_conn.close()


def update_connection_status(connection_status):
    redis_conn = None
    try:
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True,
        )
        redis_conn.hmset("status_info", connection_status)
    except Exception as e:
        raise e
    finally:
        if redis_conn:
            redis_conn.close()
