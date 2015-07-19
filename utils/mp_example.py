from abc import ABC, abstractmethod
import logging
import os
import random
from multiprocessing import Process
import multiprocessing
import uuid


class BroadcastValue(object):
    def __init__(self, initialValue = None):
        ctx = multiprocessing.get_context()
        self.mgr = multiprocessing.Manager()
        self.data = self.mgr.dict()

        self.data["value"] = initialValue
        self.condition = ctx.Condition()

    def set(self, value):
        self.data["value"] = value
        with self.condition:
            self.condition.notify_all()

    def get(self):
        with self.condition:
            self.condition.wait()
        return self.data["value"]

class ShutdownNotifier(object):
    def __init__(self, consumer=None):
        self.consumer = consumer

class WorkerThread(ABC):
    def do_run(self, condition, *args, **kwargs):
        condition.set()
        self.run(*args, **kwargs)

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

class BroadcastWorker(WorkerThread):
    def __init__(self, broadcast, queue, consumer):
        self.broadcast = broadcast
        self.queue = queue
        if not isinstance(consumer, Consumer):
            raise TypeError("expected Consumer type for argument")
        self.consumer = consumer

    def run(self):
        logging.debug("Starting %s" % (multiprocessing.current_process().name,))
        while True:
            value = self.broadcast.get()
            if isinstance(value, ShutdownNotifier):
                if value.consumer == None or value.consumer == self.consumer:
                    logging.debug("Received shutdown notification %s" % (os.getpid(),))
                    break
            else:
                self.consumer.consume_data(value)
                self.queue.put("%s" % (os.getpid(),))


class Consumer(ABC):
    def __init__(self):
        self.identifier = uuid.uuid4()

    def __eq__(self, other):
        if isinstance(other, Consumer):
            return self.identifier == other.identifier
        return False

    def __hash__(self):
        return hash(self.identifier)

    @abstractmethod
    def consume_data(self, data):
        pass

class ConsumerManager(object):
    def __init__(self):
        self.ctx = multiprocessing.get_context()
        self.consumers = {}
        self.queue = self.ctx.Queue()
        self.broadcast = BroadcastValue()
        self.threads = []
        self.object = None

    def addConsumer(self, consumer):
        start_event = self.ctx.Event()
        worker = BroadcastWorker(self.broadcast, self.queue, consumer)
        p = Process(target=worker.do_run, args=(start_event,))
        start_event.clear()
        p.start()
        if not start_event.wait(5.0):
            logging.error("Failed to start consumer thread")
        else:
            logging.debug("[%s] Started thread" % (multiprocessing.current_process().name, ))
            self.threads.append(p)
            self.consumers[consumer] = p

    def removeConsumer(self, consumer):
        p = self.consumers[consumer]
        self.broadcast.set(ShutdownNotifier(consumer))
        self.threads.remove(p)
        p.join()
        del(self.consumers[consumer])

    def broadcastObject(self, obj):
        self.broadcast.set(obj)
        j = 0
        while j < len(self.threads):
            done = self.queue.get(True)
            logging.debug("%s is complete" % (done, ))
            j += 1
        logging.debug("All threads processed")

    def destroy(self):
        self.broadcast.set(ShutdownNotifier())
        for p in self.threads:
            p.join()

##################################

class Worker(Consumer):
    def __init__(self, index):
        Consumer.__init__(self)
        pass

    def consume_data(self, data):
        logging.debug("[%s] received: %s" % (os.getpid(), data))

class Boom(object):
    def __init__(self):

        logging.debug("We have %s CPUs" % multiprocessing.cpu_count())
        manager = ConsumerManager()

        numConsumers = 5
        workers = [Worker(i) for i in range(0, numConsumers)]
        for worker in workers:
            manager.addConsumer(worker)
        logging.debug("All started...")

        for i in range(0, 10):
            logging.debug("Broadcast....")
            manager.broadcastObject("%s" % random.random())

        manager.destroy()
        logging.debug("Shutting down")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    test = Boom()
