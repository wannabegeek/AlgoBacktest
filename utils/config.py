class Config(object):
    def __init__(self, filename):
        self.config = {}
        exec(open(filename).read(), self.config)

    def __getattr__(self, item):
        return self.config[item]

    def __str__(self):
        return str(self.config)

    __repr__ = __str__
