import logging
from market.interfaces.orderbook_persist import OrderbookPersist


class BacktestOrderbookPersist(OrderbookPersist):
    def recover_open_positions(self):
        return {}

    def recover_open_orders(self):
        return {}

    def add_position(self, position):
        logging.debug("Adding position to store: %s" % (position,))

    def update_position(self, position):
        logging.debug("Updating position in store: %s" % (position,))

    def add_order(self, order):
        logging.debug("Adding order to store: %s" % (order,))

    def update_order(self, order):
        logging.debug("Updating order in store: %s" % (order,))
