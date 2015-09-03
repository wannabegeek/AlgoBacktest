import logging
import sys
import pickle
from pylab import *
from numpy import NaN, Inf, arange, isscalar, asarray, array

class Zone(object):
    def __init__(self, min, max, count, points):
        self.min = min
        self.max = max
        self.points = points

    @property
    def height(self):
        return self.max - self.min

    @property
    def count(self):
        return len(self.points)

    def __str__(self):
        return "%s -> %s [%s]" % (self.min, self.max, self.count)

    __repr__ = __str__

class SupportResistanceZones(object):
    def __init__(self):
        self.maxtab = []
        self.mintab = []

    def _peakdet(self, v, delta, x = None):
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

    def _find_cluster(self, iterable, tollerance):
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

    def _find_zones(self, turning_points, cluster_max_separation, cluster_max_span):
        zones = []

        sr = self._find_cluster(sort(turning_points), cluster_max_separation)
        for i in sr:
            if len(i) > 2:
                if max(i) - min(i) > cluster_max_span:
                    for z in self._find_zones(sort(i), cluster_max_separation / 2.0, cluster_max_span/ 2.0):
                        zones.append(z)
                else:
                    zones.append(Zone(min(i), max(i), len(i), i))

        return zones

    def locate(self, quotes):
        average_range = mean([q.high - q.low for q in quotes])
        logging.debug("ATR: %s" % (average_range, ))

        timestamps = [x.start_time for x in quotes]
        closing_prices = [x.close for x in quotes]
        self.maxtab, self.mintab = self._peakdet(closing_prices, average_range / 2.0, x=timestamps)

        turning_points = np.concatenate((array(self.maxtab)[:, 1], array(self.mintab)[:, 1]))

        return self._find_zones(turning_points, average_range / 4.0, average_range / 1.6)

    def peaks(self):
        return self.mintab, self.maxtab

if __name__=="__main__":
    from matplotlib.pyplot import plot, scatter, show
    from matplotlib import patches

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    quotes = []
    file_handle = open('/Users/tom/Downloads/market_data_d1.pkl', 'rb')
    count = 0
    while 1:
        try:
            obj = pickle.load(file_handle)
            if count > 0:
                quotes.append(obj)
            count += 1
        except EOFError:
            break

    timestamps = [x.start_time for x in quotes]
    closing_prices = [x.close for x in quotes]

    ax.plot(timestamps, closing_prices)

    sr = SupportResistanceZones()
    zones = sr.locate(quotes)
    logging.debug("Zones: %s" % (zones,))
    maxtab, mintab = sr.peaks()
    ax.scatter(array(maxtab)[:, 0], array(maxtab)[:, 1], color='blue')
    ax.scatter(array(mintab)[:, 0], array(mintab)[:, 1], color='red')

    for zone in zones:
        alpha = zone.count / 10
        r = patches.Rectangle((min(timestamps), zone.min), width=max(timestamps), height=zone.height, alpha=alpha, color='green')
        ax.add_patch(r)



    plt.show()