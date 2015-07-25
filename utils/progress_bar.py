import sys
import time
import datetime


class ProgressBar(object):
    def __init__(self, max = 100, width=50, initial = 0, label='', estimated_time=True):
        self.max = float(max)
        self.width = width
        self.label = label
        self.estimated_time = estimated_time
        self.start_time = None
        self._display(initial)

    def set(self, value):
        if self.start_time is None:
            self.start_time = datetime.datetime.utcnow()
        if value < self.max:
            self._display(value)

    def complete(self):
        sys.stdout.write("\n")
        if self.estimated_time is True:
            sys.stdout.write("Completed in %s\n" % (datetime.datetime.utcnow() - self.start_time,))
        sys.stdout.flush()

    def _display(self, value):
        percent = float(value) / self.max
        hashes = '#' * int(round(percent * self.width))
        spaces = ' ' * (self.width - len(hashes))

        if self.estimated_time is True and self.start_time is not None and percent != 0.0:
            remaining = (datetime.datetime.utcnow() - self.start_time) / percent
            sys.stdout.write("\r{0}: [{1}] {2}% - remaining: {3}".format(self.label, hashes + spaces, int(round(percent * 100)), remaining))
            sys.stdout.flush()
        else:
            sys.stdout.write("\r{0}: [{1}] {2}%".format(self.label, hashes + spaces, int(round(percent * 100))))
            sys.stdout.flush()

if __name__ == '__main__':
    progress = ProgressBar(300)
    for i in range(0, 301):
        progress.set(i)
        time.sleep(0.1 )
    progress.complete()
