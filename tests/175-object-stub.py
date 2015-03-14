import unittest
import threading
import Queue
import time

from walky.connection import *
from walky.objects import *
from walky.serializer import *
from walky.messenger import *

from _common import *

class Test(unittest.TestCase):
    def test_stub(self):

        user = TestUser()
        self.assertIsInstance(user,User)

        class DummyEngine(object): pass
        engine = DummyEngine()
        engine.serializer = Serializer()

        port = TestPort(u"TESTID")

        c = TestConnection( 
                      1, 
                      user=user,
                      engine=engine,
                      messenger=Messenger(),
                      port=port,
                  )
        self.assertIsInstance(c,Connection)

        reg_obj_id = '123'
        obj = ObjectStub(c,reg_obj_id)
        self.assertIsInstance(obj,ObjectStub)

        queue = Queue.Queue()
        def request(*a):
            queue.put(obj.foo)
        request_thread = threading.Thread(target=request)
        request_thread.daemon = True

        # Ensure the message was sent out okay
        c._next_id = 10
        request_thread.start()
        sent_line = port.queue_send.get(True,1)
        self.assertEqual(sent_line,'[0, "?", "?", [1, ["123", "foo"]], [1, {}], 10]\r\n')

        # Now, fake a reply
        c.on_readline(u'[1,"somedata",10]\r\n')

        result = queue.get(True,1)
        self.assertEqual(result,"somedata")

        # Okay, so let's see how well functions work
        def request(*a):
            r = obj.beep()
            queue.put(r)
        request_thread = threading.Thread(target=request)
        request_thread.daemon = True

        # Ensure the message was sent out okay
        c._next_id = 11
        request_thread.start()
        sent_line = port.queue_send.get(True,1)
        self.assertEqual(sent_line,'[0, "?", "?", [1, ["123", "beep"]], [1, {}], 11]\r\n')

        # Respond with a message that the object is a function
        c._next_id = 12
        c.on_readline(u'[9,[1,"{}","beep"],11]\r\n'.format(obj.reg_obj_id))

        # This should cause a response to request a function to be executed
        sent_line = port.queue_send.get(True,1)
        self.assertEqual(sent_line,'[0, "123", "beep", 12]\r\n')

        # Then acknlowedge that request for execution
        c.on_readline(u'[1,"HOWDY THERE",12]\r\n'.format(obj.reg_obj_id))

        result = queue.get(True,1)
        self.assertEqual(result,"HOWDY THERE")


if __name__ == '__main__':
    unittest.main()


