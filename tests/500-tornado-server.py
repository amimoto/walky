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
        conn = super(MyEngine,self).connection_new(
                                      connection_class=Connection,
                                      *args,
                                      **kwargs)
        conn.sys().put(tc,'@')
        return conn

    def reset(self):
        super(MyEngine,self).reset()
        router = self.router
        router.mapper('anonymous',TestClass,TestWrapper)

class Test(unittest.TestCase):

    def test_server(self):

        # Make the server...
        data_dir = 'walkydata'
        server = TornadoServer(engine_class=MyEngine)
        self.assertIsInstance(server,TornadoServer)

        # Start the server
        server_pool = threading.Thread(target=lambda *a: server.run())  
        server_pool.daemon = False
        server_pool.start()

        # Allow server to start up
        time.sleep(0.2)

        # Make the client
        client = SocketClient()
        self.assertIsInstance(client,Client)

        # Start the client
        client.connect('localhost')

        obj = client.object_get('@')
        with self.assertRaises(Exception) as cm:
            obj.foo

        self.assertEqual(obj.b,'foo')

        client.close()
        server.shutdown()


if __name__ == '__main__':
    unittest.main()

