import logging
import sys
from BackTestFramework import BackTestFramework
from DataProvider.MySQLBackTestDataProvider import MySQLBackTestDataProvider
import argparse

def processBacktestRequest(algoId):
    logging.debug("Backtest {0}".format(algoId))

    code = ""
    cursor.callproc('AlgorithmInfo', (algoId,))
    for result in cursor.stored_results():
        for results in result.fetchall():
            code = results[4]

    module = imp.new_module('Algorithm')

    compiled_code = compile(code, '<string>', 'exec')
    exec compiled_code in module.__dict__
    sys.modules['Algorithm'] = module

    algo = module.Algo()

    fn = None
    if args.show_progress == True:
        fn = lambda x : logging.progress(x)
    backTest = BackTestFramework(MySQLBackTestDataProvider, algo, progressCallback = fn)
    MySQLResults(algo, algoId).display(backTest.context)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Backtest an algorithm.')
    parser.add_argument("-a", "--algo", dest="algo", required=True, help="algorithm identifier")
    parser.add_argument("-l", "--log-level", dest="log_level", choices=['DEBUG', 'INFO', 'WARN'], default="INFO", help="logging level")
    parser.add_argument("-p", "--show-progress", dest="show_progress", action='store_true', help="log progress")

    global args
    args = parser.parse_args()

    logging.PROGRESS = 60  # positive yet important
    logging.addLevelName(logging.PROGRESS, 'PROGRESS')      # new level
    logging.progress = lambda msg, *args: logging.getLogger()._log(logging.PROGRESS, msg, args)

    level = logging.INFO
    if args.log_level == 'DEBUG':
        level = logging.DEBUG
    elif args.log_level == 'INFO':
        level = logging.INFO
    elif args.log_level == 'WARN':
        level = logging.WARN
    logging.basicConfig(format='%(levelname)s: %(message)s', level=level)

    successful = True

    # log_capture_string = StringIO.StringIO()
    # logger = logging.getLogger()
    # ch = logging.StreamHandler(log_capture_string)
    # ch.setLevel(logging.DEBUG)
    # logger.addHandler(ch)

    try:
        processBacktestRequest(args.algo)
    except Exception as e:
        logging.exception(e)
        successful = False

    # log_contents = log_capture_string.getvalue()
    # log_capture_string.close()
    # logger.removeHandler(ch)

    logging.debug('...all done')
