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
        'anon',
        ALLOW_ALL,
        DENY_UNDERSCORED,
        MODE_READ|MODE_WRITE|MODE_EXECUTE, # mode
    ] ]

class Test(unittest.TestCase):

    def test_server(self):

        server = Server()
        self.assertIsInstance(server,Server)

        server.start()

        router = server.router
        router.mapper('anon',TestClass,TestWrapper)
        self.assertIsInstance(router,Router)

        connection = server.connection_new()
        self.assertIsInstance(connection,Connection)

        port = TestPort(u'TESTID',connection)
        connection.port(port)
        self.assertIsInstance(connection,Connection)

        # Need to load at least one object into the connection
        tc = TestClass()
        reg_obj_id = connection.conn().put(tc)

        # Okay, finall can start testing the dispatcher
        connection.on_readline(u'[0,"{}","somefunc",123]'.format(reg_obj_id))
        time.sleep(0.1)

        self.assertTrue(port.buffer_send)
        self.assertEqual(port.buffer_send,['[1, "RESULT!", 123]\r\n'])

        server.shutdown()

if __name__ == '__main__':
    unittest.main()

