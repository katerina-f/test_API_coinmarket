from api import API_GOOGlE, API_YANDEX
from datetime import datetime
import json
from multiprocessing.dummy import Pool as ThreadPool
import numpy
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import sys
import unittest


URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
PARAMS = {'start':'1',
            'limit':'10',
            'convert':'USD',
            'sort': 'volume_24h'}

HEADERS = {'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_YANDEX}


def get_data_from_coinmarket():

    session = Session()
    session.headers.update(HEADERS)

    try:
      response = session.get(URL, params=PARAMS)
      data = json.loads(response.text)
      return data

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return e


class TestApiCoinmarketcap(unittest.TestCase):

    def _get_data_for_tests(self):
        start = datetime.now().timestamp()

        data = get_data_from_coinmarket()
        try:
            dates = [ticker['last_updated'][:10] for ticker in data['data']]
        except:
            dates = [0]
            print(data['status']['error_message'])

        end = datetime.now().timestamp()
        time_spent = end - start

        size = sys.getsizeof(str(data))
        return {'time_spent': time_spent,
                'dates': dates,
                'size': size}

    def test_time_spent_less_then_500_ms(self):
        self.assertTrue(self._get_data_for_tests()['time_spent'] < 0.5)
        print(self._get_data_for_tests()['time_spent'])

    def test_data_size_less_then_10_kb(self):
        self.assertTrue(self._get_data_for_tests()['size'] < 10000)
        print(self._get_data_for_tests()['size'])

    def test_updated_today(self):
        for date in self._get_data_for_tests()['dates']:
            self.assertTrue(date == str(datetime.today().date()))
        print(self._get_data_for_tests()['dates'])


class TestServerSpeed(unittest.TestCase):

    clear_data = {}

    def setUp(self):
        self._getting_data_multiproc()

    def _getting_data_multiproc(self):
        list = [TestApiCoinmarketcap() for c in range(8)]
        pool = ThreadPool(8)
        results = pool.map(self._getting_time_spent_per_call, list)
        rps = 8/sum(results)
        percentile = numpy.percentile(results[0], 80)*1000

        self.clear_data['rps'] = rps
        self.clear_data['percentile'] = percentile

    def _getting_time_spent_per_call(self, obj):
        time_spent = obj._get_data_for_tests()['time_spent']
        return time_spent

    def test_rps_less_then_5_sec(self):
        self.assertTrue(self.clear_data['rps'] < 5)
        print(self.clear_data['rps'])

    def test_80_perc_latency(self):
        self.assertTrue(self.clear_data['percentile'] < 450)
        print(self.clear_data['percentile'])


if __name__ == '__main__':
    suite_1 = unittest.TestLoader().loadTestsFromTestCase(TestApiCoinmarketcap)
    suite_2 = unittest.TestLoader().loadTestsFromTestCase(TestServerSpeed)
    if unittest.TextTestRunner(verbosity=2).run(suite_1).failures:
        print('\nSecond test will be passed, there are failures in the first one\n')
    else:
        unittest.TextTestRunner(verbosity=2).run(suite_2)
