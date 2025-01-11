import unittest
import pprint
import pandas as pd
import datetime
from db_hj3415 import mymongo
from scraper_hj3415.nfscraper import run as run_nfs
from dart_hj3415 import opendart


class EvalByDateTests(unittest.TestCase):
    def setUp(self):
        today_str = datetime.datetime.today().strftime('%Y%m%d')
        today_str = '20230426'
        self.eval_db = mongo.EvalByDate(client, today_str)

    def test_load_df(self):
        print(self.eval_db.load_df())
        pprint.pprint(self.eval_db.load_df().to_dict('records'))

    def test_get_dates(self):
        print(mongo.EvalByDate.get_dates(client))

    def test_get_recent(self):
        print(mongo.EvalByDate.get_recent(client, 'date'))
        print(mongo.EvalByDate.get_recent(client, 'dataframe'))
        pprint.pprint(mongo.EvalByDate.get_recent(client, 'dict')[:5])
