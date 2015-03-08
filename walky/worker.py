import threading
import Queue

class WorkerRequest(object):

    def execute(self):
        pass

    def _get_set_attribute(self,k,v=None):
        if not v is None:
            setattr(self,k,v)
        return getattr(self,k)

    def __getattr__(self,k):
        attr_name = "_" + k
        object.__getattribute__(self,attr_name)
        return lambda a=None: self._get_set_attribute(attr_name,a)

class WorkerThread(threading.Thread):
    """
    """
    _poll_timeout = 0.1
    _active = True
    _queue = None

    def __init__(self,queue):
        super(WorkerThread,self).__init__()
        self._queue = queue

    def _get_set_attribute(self,k,v=None):
        if not v is None:
            setattr(self,k,v)
        return getattr(self,k)

    def __getattr__(self,k):
        attr_name = "_" + k
        object.__getattribute__(self,attr_name)
        return lambda a=None: self._get_set_attribute(attr_name,a)

    def run(self):
        while self._active:
            try:
                job = self._queue.get(True,self._poll_timeout)
                if job:
                    job.execute()
            except Queue.Empty:
                pass

    def shutdown(self):
        self._active = False

class WorkerCrew(object):
    """ Async execution pool. Jobs requested are queued and
        submitted to a pool of _queue_threads. Requests are
        responsible for doing self cleanup
    """
    _queue_threads = None
    _queue = None
    _work_threads = None

    def __init__(self,threads=10):
        self._queue_threads = threads
        self.reset()

    def reset(self):
        self._queue = Queue.Queue()
        self._work_threads = []

    def pool_launch(self):
        for i in range(self._queue_threads):
            work_thread = WorkerThread(self._queue)
            self._work_threads.append(work_thread)
            work_thread.start()

    def put(self,work_request):
        """ Submit an execution request into the pool
        """
        self._queue.put(work_request)

    def start(self):
        self.pool_launch()

    def shutdown(self):
        for i in range(self._queue_threads):
            self._work_threads[i].shutdown()
        self._work_threads = []
            

    

