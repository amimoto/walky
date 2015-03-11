import unittest
import Queue
import time

from walky.worker import *

from _common import *

class MyWorkerRequest(WorkerRequest):
    def __init__(self):
        self.q = []

    def execute(self):
        self.q.append("TEST")

class Test(unittest.TestCase):

    def test_execute(self):

        # Execute our test object
        worker_obj = MyWorkerRequest()
        self.assertIsInstance(worker_obj,MyWorkerRequest)
        self.assertFalse(worker_obj.q)
        worker_obj.execute()
        self.assertTrue(worker_obj.q)

        # Have our test object executed via queue injection
        queue = Queue.Queue()
        worker_obj = MyWorkerRequest()
        workthread_obj = WorkerThread(queue)
        self.assertIsInstance(workthread_obj,WorkerThread)
        workthread_obj.start()
        queue.put(worker_obj)
        self.assertFalse(worker_obj.q)
        time.sleep(0.2)

        self.assertTrue(worker_obj.q)
        workthread_obj.shutdown()

        # Have our test object executed via the exec pool handler
        crew_obj = WorkerCrew()
        self.assertIsInstance(crew_obj,WorkerCrew)
        crew_obj.start()
        worker_obj = MyWorkerRequest()
        self.assertFalse(worker_obj.q)
        crew_obj.put(worker_obj)
        time.sleep(0.2)
        self.assertTrue(worker_obj.q)
        crew_obj.shutdown()

        # Way cool.
    


if __name__ == '__main__':
    unittest.main()


