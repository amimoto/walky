import signal
import logging
import sys

from walky.server.tornado import *

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

class TestWrapper(ObjectWrapper):
    _acls_ = [ [
        'anonymous',
        ALLOW_ALL,
        DENY_UNDERSCORED,
        MODE_READ|MODE_WRITE|MODE_EXECUTE, # mode
    ] ]

class TestClass(object):
    def myfunc(self):
        return 'func called'
    some_param = 'param value'
    _c = 'should not be accessible due to wrapper rules'

class MyEngine(Engine):
    def connection_new(self,connection_class=Connection,*args,**kwargs):
        sys_reg = Registry()
        tc = TestClass()
        conn = super(MyEngine,self).connection_new(
                                      connection_class=Connection,
                                      *args,
                                      **kwargs)
        conn.object_put(tc,'@')
        return conn

    def reset(self):
        super(MyEngine,self).reset()
        router = self.router
        router.mapper('anonymous',TestClass,TestWrapper)


# Make the server...
server = TornadoServer(engine_class=MyEngine)

# Just so we can exit cleanly
def handle_signal(sig, frame):
    IOLoop.instance().add_callback(IOLoop.instance().stop)
    server.shutdown()

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# Start the server
server.run()


