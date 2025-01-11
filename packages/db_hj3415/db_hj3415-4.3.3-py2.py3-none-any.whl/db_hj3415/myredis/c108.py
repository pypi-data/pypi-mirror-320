from typing import List, Optional
import datetime

from db_hj3415.myredis.corps import Corps
from db_hj3415 import mymongo


class C108(Corps):
    def __init__(self, code: str):
        super().__init__(code, 'c108')
        self.mymongo_c108 = mymongo.C108(code)

    @property
    def code(self) -> str:
        return super().code

    @code.setter
    def code(self, code: str):
        # 부모의 세터 프로퍼티를 사용하는 코드
        super(C108, self.__class__).code.__set__(self, code)
        self.mymongo_c108.code = code

    def list_rows(self, refresh=False):
        redis_name = self.code_page + '_rows'
        return super()._list_rows(self.mymongo_c108, redis_name, refresh)

    def get_recent_date(self, refresh=False) -> Optional[datetime.datetime]:
        redis_name = self.code_page + '_get_recent_date'

        def fetch_get_recent_date() -> str:
            # json은 datetime 형식은 저장할 수 없어서 문자열로 저장한다.
            recent_date = self.mymongo_c108.get_recent_date()
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

    def get_recent(self, refresh=False) -> Optional[List[dict]]:
        """
        저장된 데이터에서 가장 최근 날짜의 딕셔너리를 가져와서 리스트로 포장하여 반환한다.

        Returns:
            list: 한 날짜에 c108 딕셔너리가 여러개 일수 있어서 리스트로 반환한다.
        """
        redis_name = self.code_page + '_recent'

        def fetch_get_recent() -> Optional[List[dict]]:
            return self.mymongo_c108.get_recent()

        return self.fetch_and_cache_data(redis_name, refresh, fetch_get_recent)