import argparse
import glob
import logging
import os
import json
from data.csv_tickdata_provider import CSVProvider
from data.mysql_symbol_provider import MySQLSymbolProvider
from market.symbol import Symbol

class Handler(object):
    def __init__(self, symbol, outfile, input_files):
        self.pending = []
        self.totalTicks = 0

        self.outfile = open(outfile, 'w+')

        for filename in input_files:
            logging.info("Processing '%s'" % (filename,))
            data = CSVProvider(Symbol.get(symbol), filename)
            data.start_publishing(self.tick_handler)

        self.outfile.close()

    def tick_handler(self, symbol, tick):
        data = {
            "symbol_id": symbol.identifier,
            "timestamp": tick.timestamp.timestamp() * 1000, # timestamp in ms
            "bid": tick.bid,
            "offer": tick.offer
        };
        self.outfile.write(json.dumps(data) + '\n');
        self.totalTicks += 1
        if self.totalTicks >= 100000:
            logging.debug("Commited %s" % (self.totalTicks,))
            self.totalTicks = 0

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    database = {'user': 'blackbox', 'database': 'blackbox', 'host': "192.168.0.8"};
    Symbol.set_info_provider(MySQLSymbolProvider(database))

    parser = argparse.ArgumentParser(description='Parse CSV Tick data into sqlite db.')
    parser.add_argument("-s", "--symbol", dest="symbol", required=True, help="symbol identifier")
    parser.add_argument("-o", "--outfile", dest="outfile", required=True, help="File to output to")
    parser.add_argument("-i", "--in", dest="in_filename", help="csv file to read")

    args = parser.parse_args()
    input_files = glob.glob(os.path.expanduser(os.path.expandvars(args.in_filename)))
    logging.debug("Processing %s files: %s" % (len(input_files), input_files))

    h = Handler(args.symbol, args.outfile, input_files)
