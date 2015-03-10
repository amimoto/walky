import unittest
import time

from walky.service import *

from _common import *

class TestPort(Port):

    def init(self):
        self.buffer_recv = []
        self.buffer_send = []

    def _receiveline(self):
        return self.buffer_recv.pop()

    def on_receiveline(self,line): 
        pass

    def _sendline(self,line):
        self.buffer_send.append(line)

class TestService(Service):
    pass

class Test(unittest.TestCase):

    def test_service(self):

        service = TestService(u"TESTID")
        service.start()

        context = service.connection_new()
        port = TestPort(u"NEWIDENT",context)

        service.shutdown()

if __name__ == '__main__':
    unittest.main()

