from datetime import datetime
import time
from data.mysql_tickdata_provider2 import MySQLProvider
from market.symbol import Symbol
from utils.config import Config

total = 0

def handleTickUpdate(symbol, tick):
    # do something complex
    global total
    total += 1
    if total % 10 == 0:
        time.sleep(0.001)

if __name__ == '__main__':
    config = Config("../backtest/config.conf")
    provider = MySQLProvider(Symbol.get('EURUSD:CUR'), startDate=datetime(2015, 6, 29))
    startTime = datetime.utcnow()
    provider.startPublishing(handleTickUpdate)
    taken = datetime.utcnow() - startTime

    print("Processing %s records took %s" % (total, taken))
