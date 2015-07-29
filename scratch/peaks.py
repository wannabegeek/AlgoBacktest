import sys
import pickle
from pylab import *
from numpy import NaN, Inf, arange, isscalar, asarray, array
from scipy.stats import kde

def peakdet(v, delta, x = None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html

    Returns two arrays

    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.

    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.

    """
    maxtab = []
    mintab = []

    if x is None:
        x = arange(len(v))

    v = asarray(v)

    if len(v) != len(x):
        sys.exit('Input vectors v and x must have same length')

    if not isscalar(delta):
        sys.exit('Input argument delta must be a scalar')

    if delta <= 0:
        sys.exit('Input argument delta must be positive')

    mn, mx = Inf, -Inf
    mnpos, mxpos = NaN, NaN

    lookformax = True

    for i in arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]

        if lookformax:
            if this < mx-delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True

    return array(maxtab), array(mintab)

def find_cluster(turning_points, limit):

    v = sort(turning_points)
    result = []

    prev = None
    current_zone = []

    for point in v:
        if prev is not None:
            if point - prev < limit:
                current_zone.append(prev)
            else:
                current_zone.append(point)
                if len(current_zone) > 2:
                    result.append(current_zone)
                current_zone = []

        prev = point

    if len(current_zone) > 1:
        result.append(current_zone)

    return result

def find_cluster2(iterable, tollerance):
    prev = None
    group = []
    for item in iterable:
        if not prev or item - prev <= tollerance:
            group.append(item)
        else:
            yield group
            group = [item]
        prev = item
    if group:
        yield group

if __name__=="__main__":
    from matplotlib.pyplot import plot, scatter, show
    from matplotlib import patches

    fig = plt.figure()
    ax = fig.add_subplot(111)

    quotes = []
    file_handle = open('/Users/tom/Downloads/market_data_d1.pkl', 'rb')
    while 1:
        try:
            obj = pickle.load(file_handle)
            quotes.append(obj)
        except EOFError:
            break

    timestamps = [x.start_time for x in quotes]
    closing_prices = [x.close for x in quotes]

    maxtab, mintab = peakdet(closing_prices, 0.005, x=timestamps)
    ax.plot(timestamps, closing_prices)
    ax.scatter(array(maxtab)[:, 0], array(maxtab)[:, 1], color='blue')
    ax.scatter(array(mintab)[:, 0], array(mintab)[:, 1], color='red')


    turning_points = np.concatenate((array(maxtab)[:, 1], array(mintab)[:, 1]))
    sr = find_cluster2(sort(turning_points), 0.002)
    for i in sr:
        if len(i) > 2:
            r = patches.Rectangle((min(timestamps), min(i)), width=max(timestamps), height=max(i) - min(i), alpha=0.5, color='green')
            ax.add_patch(r)

    plt.show()