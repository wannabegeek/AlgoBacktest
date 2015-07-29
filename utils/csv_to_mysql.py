import argparse
import glob
import logging
import os
from mysql.connector import errors
from mysql import connector
from data.csv_tickdata_provider import CSVProvider
from data.mysql_symbol_provider import MySQLSymbolProvider
from market.symbol import Symbol

class Handler(object):
    def __init__(self, symbol, user, database, host, input_files):
        self.pending = []
        self.totalTicks = 0
        self._db_connection = connector.connect(user=user, database=database, host=host)
        self.cursor = self._db_connection.cursor(buffered=True)
        self.cursor.execute("SET unique_checks=0;")
        self.cursor.execute("SET autocommit=0;")

        for filename in input_files:
            logging.info("Processing '%s'" % (filename,))
            data = CSVProvider(Symbol.get(symbol), filename)
            data.start_publishing(self.tick_handler)

        self._db_connection.commit()
        self.cursor.execute("SET unique_checks=1;")
        self.cursor.close()
        self._db_connection.close()

    def tick_handler(self, symbol, tick):
        try:
            self.cursor.execute("INSERT INTO tick_data(symbol_id, timestamp, bid, offer) VALUES(%s, %s, %s, %s)", (symbol.identifier, tick.timestamp, tick.bid, tick.offer))
            self.totalTicks += 1
            if self.totalTicks >= 100000:
                self._db_connection.commit()
                logging.debug("Commited %s" % (self.totalTicks,))
                self.totalTicks = 0
        except connector.errors.IntegrityError as e:
            # probably a duplicate entry
            pass

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    Symbol.setDataProvider(MySQLSymbolProvider())

    parser = argparse.ArgumentParser(description='Parse CSV Tick data into sqlite db.')
    parser.add_argument("-s", "--symbol", dest="symbol", required=True, help="symbol identifier")
    parser.add_argument("-u", "--user", dest="user", default="blackbox", help="mysql host")
    parser.add_argument("-x", "--host", dest="host", default="localhost", help="mysql host")
    parser.add_argument("-d", "--database", dest="database", default="blackbox", help="mysql database")
    parser.add_argument("-i", "--in", dest="in_filename", help="csv file to read")

    args = parser.parse_args()
    input_files = glob.glob(os.path.expanduser(os.path.expandvars(args.in_filename)))
    logging.debug("Processing %s files: %s" % (len(input_files), input_files))

    h = Handler(args.symbol, args.user, args.database, args.host, input_files)
