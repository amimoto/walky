import unittest

from walky.server.tornado import *
from _common import *


class TestWrapper(ObjectWrapper):
    _acls_ = [ [
        'testgroup',
        ALLOW_ALL,
        DENY_UNDERSCORED,
        MODE_READ|MODE_WRITE|MODE_EXECUTE, # mode
    ] ]

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

class MyTornadoSocketServer(TornadoSocketServer):
    pass

class Test(unittest.TestCase):

    def test_server(self):
        server = TornadoServer(
                      socket_server_class=MyTornadoSocketServer,
                      engine_class=MyEngine,
                  )

        self.assertIsInstance(server,TornadoServer)
        server.run()

if __name__ == '__main__':
    unittest.main()

