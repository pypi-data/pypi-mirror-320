from pymongo import ASCENDING, DESCENDING
from typing import Optional, Any
import datetime
import pandas as pd

from utils_hj3415 import tools

from db_hj3415.mymongo.base import Base
from db_hj3415.mymongo.corps import Corps

class C108(Corps):
    def __init__(self, code: str):
        super().__init__(code=code, page='c108')

    @classmethod
    def save(cls, code: str, c108_data: pd.DataFrame):
        assert tools.is_6digit(code), f'Invalid value : {code}'
        page = 'c108'

        Base.mongo_client[code][page].create_index([('날짜', ASCENDING)], unique=False)
        cls._save_df(code=code, page=page, df=c108_data, clear_table=True)

    def get_recent_date(self) -> Optional[datetime.datetime]:
        # 저장되어 있는 데이터베이스의 최근 날짜를 찾는다.
        try:
            r_date = self._col.find({'날짜': {'$exists': True}}).sort('날짜', DESCENDING).next()['날짜']
        except StopIteration:
            # 날짜에 해당하는 데이터가 없는 경우
            return None

        return datetime.datetime.strptime(r_date, '%y/%m/%d')

    def get_recent(self) -> Optional[list[Any]]:
        """

        저장된 데이터에서 가장 최근 날짜의 딕셔너리를 가져와서 리스트로 포장하여 반환한다.

        Returns:
            list: 한 날짜에 c108 딕셔너리가 여러개 일수 있어서 리스트로 반환한다.
        """
        try:
            r_date = self.get_recent_date().strftime('%y/%m/%d')
        except AttributeError:
            # 최근데이터가 없어서 None을 반환해서 에러발생한 경우
            return None
        # 찾은 날짜를 바탕으로 데이터를 검색하여 리스트로 반환한다.
        r_list = []
        for r_c108 in self._col.find({'날짜': {'$eq': r_date}}):
            del r_c108['_id']
            r_list.append(r_c108)
        return r_list