import unittest
import time

from walky.server import *
from walky.router import *

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


class TestWrapper(ObjectWrapper):
    _acls_ = [ [
        'testgroup',
        ALLOW_ALL,
        DENY_UNDERSCORED,
        MODE_READ|MODE_WRITE|MODE_EXECUTE, # mode
    ] ]

class Test(unittest.TestCase):

    def test_server(self):

        server = Server()
        self.assertIsInstance(server,Server)

        router = server.router
        router.mapper('testgroup',TestClass,TestWrapper)
        self.assertIsInstance(router,Router)

        conn = server.connection_new()
        self.assertIsInstance(conn,Connection)

        server.shutdown()

if __name__ == '__main__':
    unittest.main()

