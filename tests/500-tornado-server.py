import time
import unittest
import threading

from walky.server.tornado import *
from walky.client.socket import *

from _common import *

class MyEngine(Engine):
    def connection_new(self,connection_class=Connection,*args,**kwargs):
        sys_reg = Registry()
        tc = TestClass()
        sys_reg.put(tc,'@')
        conn = super(MyEngine,self).connection_new(
                                      connection_class=Connection,
                                      sys_reg=sys_reg,
                                      *args,
                                      **kwargs)
        return conn

    def reset(self):
        super(MyEngine,self).reset()
        router = self.router
        router.mapper('anonymous',TestClass,TestWrapper)

class Test(unittest.TestCase):

    def test_server(self):

        # Make the server...
        server = TornadoServer(engine_class=MyEngine)
        self.assertIsInstance(server,TornadoServer)

        # Start the server
        server_pool = threading.Thread(target=lambda *a: server.run())  
        server_pool.start()

        # Allow server to start up
        time.sleep(0.1)

        # Make the client
        client = SocketClient()
        self.assertIsInstance(client,Client)

        # Start the client
        client.connect('localhost')

        print  "ABOUT TO SEND:"
        obj = client.object_get('@')
        print "SENT and waiting"

        print obj.foo
        print "RECEIVED"

        time.sleep(1)

        server.shutdown()


if __name__ == '__main__':
    unittest.main()

