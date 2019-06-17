from coinmarketcap import Market
from datetime import datetime
import pprint

def get_tickers_with_max_volume():
    coinmarketcap = Market()
    start = datetime.today().timestamp()

    tickers = coinmarketcap.ticker(start=0, limit=10, sort='volume_24h')
    tickers_size = sys.getsizeof(tickers)

    pprint.pprint(tickers_size)
    # for ticker in tickers:


    time_spent = datetime.today().timestamp() - start
    return {'time_spent': time_spent,
            'tickers': tickers}
