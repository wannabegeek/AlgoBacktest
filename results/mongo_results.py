import datetime
import locale

from pymongo import MongoClient
from market.order import Direction

locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')

def calculate_capital(self, change):
    self.capital += change
    return self.capital

def display_results(container):
    client = MongoClient('192.168.0.8', 27017)
    db = client.test

    total_positions = len(list(filter(lambda x: not x.is_open(), container.context.positions)))
    percent_change = ((container.context.working_capital - container.starting_capital) / container.starting_capital) * 100.0

    # create summary
    result = db.backtest_results.insert({
        "name": container.algo.identifier(),
        "change": percent_change,
    })

    # now for the main algo details
    closed_positions = sorted(filter(lambda x: not x.is_open(), container.context.positions), key=lambda x: x.exit_tick.timestamp)

    timestamps = [o.exit_tick.timestamp for o in closed_positions]
    algorithm_performance = [calculate_capital(float(o.equity())) for o in closed_positions]
    performance = dict(zip(timestamps, algorithm_performance))

    algo_data = {
        "algo_id": result,
        "name": container.algo.identifier(),
        "positions": total_positions,
        "starting_capital": container.starting_capital,
        "current_capital": container.context.working_capital,
        "change": percent_change,
        "performance": performance
    }

    have_quote = False
    start_time = container.context.start_time
    end_time = datetime.datetime.min
    for symbol_context in container.context.symbol_contexts.values():
        have_quote = True
        quote = symbol_context.quotes[-1]
        end_time = max(quote.start_time + quote.period, end_time)

    if have_quote is True:
        algo_data["start"] = start_time.timestamp() * 1000
        algo_data["end"] = end_time.timestamp() * 1000

    if total_positions != 0:
        winning = list(filter(lambda x: x.points_delta() > 0.0, closed_positions))

        algo_data["winning_ratio"] = (len(winning)/total_positions * 100)
        algo_data["total_pts"] = sum([x.points_delta() for x in closed_positions])

    positions = []
    if total_positions != 0:
        for position in container.context.positions:
            limits = []
            for version in position.version:
                limits.append({
                    "stop_px": version.stop_price,
                    "take_profit_px": version.take_profit
                })
            position_data = {
                "_id": position.id,
                "symbol_id": position.order.symbol.identifier,
                "status": position.status.name,
                "direction": position.order.direction.value,
                "qty": position.order.quantity,
                "is_open": position.is_open(),
                "entry_ts": position.entry_tick.timestamp * 1000,
                "entry_px": position.entry_tick.offer if position.order.direction == Direction.LONG else position.entry_tick.bid,
                "limits": limits
            }

            if not position.is_open():
                position_data["points"] = position.points_delta()
                position_data["p/l"] = position.equity()
                position_data["exit_ts"] = position.exit_tick.timestamp * 1000
                position_data["exit_px"] = position.exit_tick.offer if position.order.direction == Direction.LONG else position.exit_tick.bid

            positions.append(position_data)

    algo_data["positions"] = positions

    orders = []
    algo_data["orders"] = orders

    db.backtest_details.insert(algo_data)
