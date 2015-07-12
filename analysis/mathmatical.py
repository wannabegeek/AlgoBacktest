import math

import numpy as np

from market.symbol import SymbolContext


def gradient(x, y):
    """ Calculates the avererage gradient over the tuples provided """
    if len(x) < 2 or len(x) != len(y):
        raise ArithmeticError("data argument must contain at 2 or more data points")

    result = 0
    for idx in range(1, len(x)):
        dx = x[idx] - x[idx - 1]
        dy = y[idx] - y[idx - 1]
        if dy != 0:
            result = result + (dx / dy)

    if result != 0:
        return result / (len(x) - 1)
    return 0


def sma(context, periods):
    ''' average '''
    if not isinstance(context, SymbolContext):
        raise TypeError("context must be of type 'SymbolContext'")

    values = np.asarray([x.close for x in context.quotes()[-min(periods, len(context.quotes())):]])
    return np.mean(values)

def ema(context, periods):
    if not isinstance(context, SymbolContext):
        raise TypeError("context must be of type 'SymbolContext'")

    adjPeriod = min(periods, len(context.quotes()))

    values = np.asarray([x.close for x in context.quotes()[-adjPeriod:]])

    weights = np.exp(np.linspace(-1.0, 0.0, adjPeriod))
    weights /= weights.sum()

    a =  np.convolve(values, weights, 'valid')
    return a[-1]

def stddev(context, periods):
    ''' Standard Deviation '''
    if not isinstance(context, SymbolContext):
        raise TypeError("context must be of type 'SymbolContext'")

    values = np.asarray([x.close for x in context.quotes()[-min(periods, len(context.quotes())):]])
    return np.std(values, axis=0)

def vwap(context, periods):
    ''' Volume Weighted Average Price '''
    if not isinstance(context, SymbolContext):
        raise TypeError("context must be of type 'SymbolContext'")

    v1 = sum([x.close * x.volume for x in context.quotes()[-min(periods, len(context.quotes())):]])
    v2 = sum([x.close for x in context.quotes[-min(periods, len(context.quotes)):]])
    return v1 / v2


"""
The Sharpe ratio characterizes how well the return of an asset compensates the investor for the risk taken.

When comparing two assets versus a common benchmark, the one with a higher Sharpe ratio provides better return
for the same risk (or, equivalently, the same return for lower risk). However, like any other mathematical
model, it relies on the data being correct. Pyramid schemes with a long duration of operation would typically
provide a high Sharpe ratio when derived from reported returns, but the inputs are false. When examining the
investment performance of assets with smoothing of returns (such as with-profits funds) the Sharpe ratio should
be derived from the performance of the underlying assets rather than the fund returns.
"""


def sharpeRatio(array, n=252):
    ''' calculate sharpe ratio '''
    # precheck
    if (array is None or len(array) < 2 or n < 1):
        return -1

    returns = []
    pre = array[0]
    for post in array[1:]:
        returns.append((float(post) - float(pre)))
        pre = post

    return math.sqrt(n) * mean(returns) / stddev(returns)


# if __name__ == '__main__':
#     x = asarray([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
#     y = asarray([12.0, 34.0, 54.0, 35.0, 4325.0, 43.0, 89.0, 34.0, 11.0, 99.0, 542.0])
#     print "Gradient"
#     print gradient(x, y)
#     print gradient(asarray([0, 1, 2, 3]), asarray([0, 1, 2, 3]))
#     print gradient(asarray([0, 1, 2, 3]), asarray([3, 2, 1, 0]))
#     print gradient(asarray([0, 1, 2, 3]), asarray([3, 3, 3, 3]))