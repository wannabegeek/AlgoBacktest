from bisect import bisect_left
from datetime import timedelta

from strategycontainer.position import PositionDirection


class ResultsProcessorResults(object):
    TIMESTAMP = 0
    BENCHMARK = 1
    ALGORITHM = 2

class ResultsProcessor(object):

    def __init__(self, algo):
        self.algo = algo

    def findActivePositionsAtTime(self, positions, timestamp):
        active = filter(lambda x: x.entryQuote.timestamp < timestamp and (x.exitQuote == None or x.exitQuote.timestamp >= timestamp), positions)
        if len(active) > 0:
            return active
        return None

    def display(self, context):
        raise NotImplementedError("'display' must be implemented by sub-class")

    def calculatePerformance(self, context):
        # work out the performance vs benchmark
        # thi is temporary to find the start/end dates for the backtest
        minQuote = None
        maxQuote = None
        for symbol in self.algo.portfolio_symbols():
            data = [x.timestamp for x in context.symbolContexts[symbol].quotes()]
            if minQuote is None:
                minQuote = data[0]
            if maxQuote is None:
                maxQuote = data[0]
            minQuote = min(minQuote, min(data))
            maxQuote = max(maxQuote, max(data))

        processingDate = minQuote
        processingDate += timedelta(seconds=(self.algo.period() * self.algo.warmupPeriod()))

        performance = []
        benchmark = 0.0
        algorithm = 0.0

        while processingDate <= maxQuote:
            totalVolume = 0.0
            for symbol in self.algo.analysis_symbols():
                quote = context.symbolContexts[symbol].quoteAtTime(processingDate)
                prevQuote = context.symbolContexts[symbol].previousQuote(quote)
                if prevQuote is not None:
                    delta = (quote.close - prevQuote.close)
                    benchmark += delta
                    for position in context.closedPositions:
                        # if we have a position, calculate the point change
                        if position.symbol == symbol and position.entryQuote.timestamp < processingDate and position.exitQuote.timestamp >= processingDate:
                            multiplier = 1 if position.direction == PositionDirection.LONG else -1
                            algorithm += (delta * multiplier) * position.ratio

                    for position in context.openPositions:
                        # if we have a position, calculate the point change
                        if position.symbol == symbol and position.entryQuote.timestamp < processingDate:
                            multiplier = 1 if position.direction == PositionDirection.LONG else -1
                            algorithm += (delta * multiplier) * position.ratio

                    totalVolume = totalVolume + quote.volume

                    performance.append([processingDate, benchmark, algorithm, totalVolume, ])

            processingDate += timedelta(seconds=self.algo.period())
            while processingDate.weekday() >= 5:
                processingDate += timedelta(seconds=self.algo.period())

        return performance

    def customDataAtTime(self, context, value, timestamp):
        data = context.custom_data[value]
        keys = sorted(data.keys())
        val = bisect_left(keys, timestamp) - 1
        return data[keys[val]]
