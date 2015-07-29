import sys
import pickle
from pylab import *
from numpy import NaN, Inf, arange, isscalar, asarray, array

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

if __name__=="__main__":
    from matplotlib.pyplot import plot, scatter, show
    # series = [0,0,0,2,0,0,0,-2,0,0,0,2,0,0,0,-2,0]
    # x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,20,21]

    x = arange(0.0, 2.0, 0.01)
    series = sin(2*pi*x)

    quotes = []
    file_handle = open('/Users/tom/Downloads/market_data_d1.pkl', 'rb')
    while 1:
        try:
            obj = pickle.load(file_handle)
            quotes.append(obj)
        except EOFError:
            break

    x = [x.start_time for x in quotes]
    series = [x.close for x in quotes]

    maxtab, mintab = peakdet(series, 2000, x=x)
    plot(x, series)
    scatter(array(maxtab)[:, 0], array(maxtab)[:, 1], color='blue')
    scatter(array(mintab)[:, 0], array(mintab)[:, 1], color='red')
    show()