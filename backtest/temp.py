import logging
from algorithms.sample_algorithm import Algo
from data.csvtickdataprovider import CSVProvider
from strategycontainer.container import Container


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    client = Container(Algo(), CSVProvider())
    client.start()
    logging.info("All done... shutting down")

if __name__ == '__main__':
    main()