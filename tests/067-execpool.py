import unittest
import Queue
import time

from walky.execpool import *

from _common import *

class MyExecutionRequest(ExecutionRequest):
    def __init__(self):
        self.q = []

    def execute(self):
        self.q.append("TEST")

class Test(unittest.TestCase):

    def test_execute(self):

        # Execute our test object
        exr_obj = MyExecutionRequest()
        self.assertIsInstance(exr_obj,MyExecutionRequest)
        self.assertFalse(exr_obj.q)
        exr_obj.execute()
        self.assertTrue(exr_obj.q)

        # Have our test object executed via queue injection
        queue = Queue.Queue()
        exr_obj = MyExecutionRequest()
        ext_obj = ExecutionThread(queue)
        self.assertIsInstance(ext_obj,ExecutionThread)
        ext_obj.start()
        queue.put(exr_obj)
        self.assertFalse(exr_obj.q)
        time.sleep(0.2)

        self.assertTrue(exr_obj.q)
        ext_obj.shutdown()

        # Have our test object executed via the exec pool handler
        exp_obj = ExecutionPool()
        self.assertIsInstance(exp_obj,ExecutionPool)
        exp_obj.start()
        exr_obj = MyExecutionRequest()
        self.assertFalse(exr_obj.q)
        exp_obj.put(exr_obj)
        time.sleep(0.2)
        self.assertTrue(exr_obj.q)
        exp_obj.shutdown()

        # Way cool.
    


if __name__ == '__main__':
    unittest.main()


