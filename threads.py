from threading import Thread
from Queue import Queue

class ThreadPool(object):

    def __init__(self, size):
        self.size = size
        self.q = Queue()
        for _ in xrange(size):
            t = Thread(target=self._run)
            t.daemon = True
            t.start()
        #print 'started', size, 'threads'

    def _run(self):
        import threading
        while True:
            target = self.q.get()
            #print threading.current_thread(), 'go'
            target()
            self.q.task_done()
            #print threading.current_thread(), 'went'

    def execute(self, target):
        self.q.put(target)

    def join(self):
        self.q.join()
