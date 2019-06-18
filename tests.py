import asyncio
from coinmarketcap import Market
from datetime import datetime
import numpy
import threading
import sys, os
import unittest


class TestApiCoinmarketcap(unittest.TestCase):

    def get_tickers_with_max_volume(self):
        coinmarketcap = Market()
        start = datetime.today().timestamp()

        data_for_parsing = coinmarketcap.ticker(start=0, limit=10, sort='volume_24h')['data']

        dates = []
        for ticker in data_for_parsing:
            updated = datetime.fromtimestamp(data_for_parsing[ticker]['last_updated'])
            updated = updated.date().isoformat()
            dates.append(updated)

        time_spent = datetime.today().timestamp() - start
        return {'time_spent': time_spent,
                'dates': dates,
                'size': sys.getsizeof(data_for_parsing)}

    def test_time_spent_less_then_500_ms(self):
        self.assertTrue(self.get_tickers_with_max_volume()['time_spent'] < 0.5)

    def test_data_size_less_then_10_kb(self):
        self.assertTrue(self.get_tickers_with_max_volume()['size'] < 10000)

    def test_updated_today(self):
        for date in self.get_tickers_with_max_volume()['dates']:
            self.assertTrue(date == str(datetime.today().date()))


class TestServerSpeed(unittest.TestCase):

    def getting_data_multiproc(self):
        testing_func = TestApiCoinmarketcap().get_tickers_with_max_volume
        time_spent = []
        for i in range(8):
            try:
                t = threading.Thread(target=testing_func)
                t.start()
                time_spent.append(testing_func()['time_spent'])
            except:
                return False
        percentile = numpy.percentile(time_spent, 80)
        rps = 8/sum(time_spent)
        return {'rps': rps,
                'percentile': percentile}

    def test_connection_all_processes(self):
        self.assertTrue(self.getting_data_multiproc() != False)

    def test_rps_less_then_5_sec(self):
        self.assertTrue(self.getting_data_multiproc()['rps'] > 5)

    def test_80_perc_latency(self):
        self.assertTrue(self.getting_data_multiproc()['percentile'] < 450)


if __name__ == '__main__':
    suite_1 = unittest.TestLoader().loadTestsFromTestCase(TestApiCoinmarketcap)
    suite_2 = unittest.TestLoader().loadTestsFromTestCase(TestServerSpeed)
    unittest.TextTestRunner(verbosity=2).run(suite_1)
    unittest.TextTestRunner(verbosity=2).run(suite_2)
