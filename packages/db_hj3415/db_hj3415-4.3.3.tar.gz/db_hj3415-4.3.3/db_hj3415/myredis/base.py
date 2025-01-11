from typing import Optional, Callable, Any
import os
import redis
import pickle

from utils_hj3415 import setup_logger
mylogger = setup_logger(__name__,'WARNING')


def connect_to_redis(addr: str, password: str) -> redis.Redis:
    conn_str = f"Connect to Redis ..."
    print(conn_str, f"Server Addr : {addr}")
    # decode_responses=False 로 설정해서 바이트 반환시켜 피클을 사용할 수 있도록한다.
    return redis.StrictRedis(host=addr, port=6379, db=0, decode_responses=False, password=password)

def select_redis_addr() -> str:
    mode = os.getenv("DB_MODE", 'LOCAL')
    if mode == 'DEV':
        redis_addr = os.getenv('DEV_REDIS', '')
    elif mode == 'LOCAL':
        redis_addr = os.getenv('LOCAL_REDIS', 'redis://localhost:6379/')
    elif mode == 'DOCKER':
        redis_addr = os.getenv('DOCKER_REDIS', 'redis://redis:6379/')
    else:
        raise Exception("Invalid value in MODE env variable.")
    return redis_addr


class Base:
    redis_client = connect_to_redis(addr=select_redis_addr(), password=os.getenv('REDIS_PASSWORD', ''))

    # 기본 Redis 캐시 만료 시간 (1일)
    DEFAULT_CACHE_EXPIRATION_SEC = 3600 * 24

    def __init__(self):
        if Base.redis_client is None:
            raise ValueError("myredis.Base.redis_client has not been initialized!")

    @classmethod
    def exists(cls, key_name: str) -> bool:
        # 키가 존재하는지 확인
        if cls.redis_client.exists(key_name):
            return True
        else:
            return False

    @classmethod
    def get_ttl(cls, redis_name: str) -> Optional[int]:
        # 해당 키의 남은 시간(TTL) 확인
        ttl = cls.redis_client.ttl(redis_name)

        if ttl == -1:
            mylogger.warning(f"{redis_name}는 만료 시간이 설정되어 있지 않습니다.")
        elif ttl == -2:
            mylogger.warning(f"{redis_name}는 Redis에 존재하지 않습니다.")
        else:
            mylogger.info(f"{redis_name}의 남은 시간은 {ttl}초입니다.")
            return ttl


    @classmethod
    def delete(cls, redis_name: str):
        """
        redis_name 에 해당하는 키/값을 삭제하며 원래 없으면 아무일 없음
        :param redis_name:
        :return:
        """
        mylogger.debug(Base.list_redis_names())
        cls.redis_client.delete(redis_name)
        mylogger.debug(Base.list_redis_names())

    @classmethod
    def delete_all_with_pattern(cls, pattern: str) -> bool:
        """
        pattern에 해당하는 모든 키를 찾아서 삭제한다.
        :param pattern: ex) 005930.c101* - 005930.c101로 시작되는 모든키 삭제
        :return:
        """
        # print(Redis.list_redis_names())
        # SCAN 명령어를 사용하여 패턴에 맞는 키를 찾고 삭제
        cursor = '0'
        while cursor != 0:
            cursor, keys = cls.redis_client.scan(cursor=cursor, match=pattern, count=1000)
            if keys:
                cls.redis_client.delete(*keys)

        mylogger.debug(Base.list_redis_names())
        return True

    @classmethod
    def list_redis_names(cls, filter:str="all") -> list:
        # SCAN 명령어 파라미터
        pattern = b"*" if filter == "all" else f"*{filter}*".encode('utf-8')  # 부분 일치: *filter*
        mylogger.debug(f"pattern : {pattern}")
        cursor = "0"
        matched_keys = []

        while True:
            # SCAN 호출
            cursor, keys = cls.redis_client.scan(cursor=cursor, match=pattern, count=1000)
            mylogger.debug(f"cursor : {cursor}/{type(cursor)}")
            matched_keys.extend(keys)
            # 커서가 '0'이면 스캔이 끝났다는 의미
            if str(cursor) == "0":
                break

        return sorted(matched_keys)

    @classmethod
    def set_value(cls, redis_name: str, value: Any, expiration_sec: int = DEFAULT_CACHE_EXPIRATION_SEC) -> None:

        cls.redis_client.setex(redis_name, expiration_sec, pickle.dumps(value))
        mylogger.info(f"Redis 캐시에 저장 (만료시간: {expiration_sec}초) - redis_name : {redis_name}")


    @classmethod
    def get_value(cls, redis_name: str) -> Any:
        # 값 가져오기
        stored_data = cls.redis_client.get(redis_name)  # 키 "my_key"의 값을 가져옴
        value = pickle.loads(stored_data) if stored_data is not None else None
        return value


    @classmethod
    def fetch_and_cache_data(cls, redis_name: str, refresh: bool, fetch_function: Callable, *args, timer=DEFAULT_CACHE_EXPIRATION_SEC) -> Any:
        """
        캐시에서 데이터를 가져오거나, 없으면 fetch_function을 호출하여 데이터를 계산 후 캐싱합니다.
        :param redis_name: 저장할 레디스이름
        :param refresh: 캐시에 데이터가 있어도 무조건 데이터베이스를 이용하여 캐시를 리프레시한다.
        :param fetch_function: 데이터베이스에서 데이터를 가지고 오는 함수
        :param timer: 캐시만료시간(초) - 기본 3600초(1시간)
        :param args: fetch_function에서 인자가 있는경우 사용한다.
        :return: 데이터 값은 json.loads()로 후처리를 해야할 수 있다.
        """
        if not refresh:
            value = cls.get_value(redis_name)
            ttl_hours = round(cls.redis_client.ttl(redis_name) / timer, 1)
            mylogger.info(f"Redis 캐시에서 데이터 가져오기 (남은시간: {ttl_hours} 시간) - redis_name : {redis_name}")
            if value:
                return value

        # 캐시된 데이터가 없거나 refresh=True인 경우
        value = fetch_function(*args)

        if value:
            cls.set_value(redis_name=redis_name, value=value, expiration_sec=timer)
        return value