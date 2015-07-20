import sys
import time

class ProgressBar(object):
    def __init__(self, max = 100, width=50, initial = 0):
        self.max = float(max)
        self.width = width
        self._display(initial)

    def set(self, value):
        self._display(value)

    def _display(self, value):
        percent = float(value) / self.max
        hashes = '#' * int(round(percent * self.width))
        spaces = ' ' * (self.width - len(hashes))
        sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
        sys.stdout.flush()

if __name__ == '__main__':
    progress = ProgressBar(300)
    for i in range(0, 301):
        progress.set(i)
        time.sleep(0.1 )
    print("")
