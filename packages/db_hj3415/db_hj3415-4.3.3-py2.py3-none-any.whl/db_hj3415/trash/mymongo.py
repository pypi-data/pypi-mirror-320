# cryptography 관련 경고 메시지 억제하는 코드
import warnings
from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

# 이후에 pymongo를 임포트하거나 관련 코드를 실행합니다.

from pymongo import  MongoClient
from typing import List


class EvalByDate(Base):
    """
    각 날짜별로 만들어진 eval-report 데이터프레임을 관리하는 클래스
    DB_NAME : eval
    COL_NAME : Ymd형식 날짜
    """
    EVAL_DB = 'eval'

    def __init__(self, client: MongoClient, date: str):
        super().__init__(client, self.EVAL_DB, date)
        # 인덱스 설정
        #self.my_col.create_index('code', unique=True)

    @staticmethod
    def get_dates(client: MongoClient) -> List[str]:
        # 데이터베이스에 저장된 날짜 목록을 리스트로 반환한다.
        dates_list = client.eval.list_collection_names()
        dates_list.sort()
        return dates_list

    @classmethod
    def get_recent(cls, client: MongoClient, type: str):
        """
        eval 데이터베이스의 가장 최근의 유요한 자료를 반환한다.
        type의 종류에 따라 반환값이 달라진다.[date, dataframe, dict]
        """
        dates = cls.get_dates(client)

        while len(dates) > 0:
            recent_date = dates.pop()
            recent_df = cls(client, recent_date).load_df()
            if len(recent_df) != 0:
                if type == 'date':
                    return recent_date
                elif type == 'dataframe':
                    return recent_df
                elif type == 'dict':
                    return recent_df.to_dict('records')
                else:
                    raise Exception(f"Invalid type : {type}")

        return None
