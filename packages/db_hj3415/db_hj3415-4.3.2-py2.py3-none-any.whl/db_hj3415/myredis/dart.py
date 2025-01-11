from typing import Optional
import datetime

from db_hj3415.myredis.corps import Corps
from db_hj3415 import mymongo


class Dart(Corps):
    def __init__(self, code: str):
        super().__init__(code, 'dart')
        self.mymongo_dart = mymongo.Dart(code)

    def get_recent_date(self, refresh=False) -> Optional[datetime.datetime]:
        redis_name = self.code_page + '_get_recent_date'

        def fetch_get_recent_date() -> str:
            # json은 datetime 형식은 저장할 수 없어서 문자열로 저장한다.
            recent_date = self.mymongo_dart.get_recent_date()
            if recent_date is None:
                str_data_in = ''
            else:
                str_data_in = recent_date.isoformat()
            return str_data_in

        str_data = self.fetch_and_cache_data(redis_name, refresh, fetch_get_recent_date)
        if str_data == '':
            return None
        else:
            return datetime.datetime.fromisoformat(str_data)

