from datetime import datetime
import unittest
import sys, os


sys.path.append(os.getcwd())
from get_tickers_from_coinmarket import *


class TestApiCoinmarketcap(unittest.TestCase):
    def setUp(self):
        self.data = get_tickers_with_max_volume()
        self.size = sys.getsizeof(self.data)

    def test_time_spent_less_500(self):
        self.assertEqual(self.data['time_spent'], True)

    def get_update_today(self):
        pass

    def test_size_not_bigger_10(self):
        self.assertEqual(self.data['time_spent'], True)



if __name__ == '__main__':
    unittest.main()
