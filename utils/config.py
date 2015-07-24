class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# class Config(metaclass=Singleton):
class Config(object):
    def __init__(self, filename):
        self.config = {}
        exec(open(filename).read(), self.config)

    def __getattr__(self, item):
        return self.config[item]

    def __str__(self):
        return str(self.config)

    __repr__ = __str__
