import Queue

from walky.port import *
from walky.objects import *
from walky.user import *
from walky.connection import *

class TestClass(object):
    def a(self):
        return 'yar'
    def somefunc(self):
        return "RESULT!"
    b = 'foo'
    _c = None

class TestWrapper(ObjectWrapper):
    _acls_ = [ [
        'testgroup',
        ALLOW_ALL,
        DENY_UNDERSCORED,
        MODE_READ|MODE_WRITE|MODE_EXECUTE, # mode
    ] ]

class TestPort(Port):

    def init(self):
        self.buffer_recv = []
        self.buffer_send = []
        self.queue_recv = Queue.Queue()
        self.queue_send = Queue.Queue()

    def _receiveline(self):
        return self.buffer_recv.pop()

    def on_receiveline(self,line): pass

    def _sendline(self,line):
        self.buffer_send.append(line)
        self.queue_send.put(line)

class TestUser(User):
    def __init__(self):
        groups = ['testgroup','group2']
        attrs = {
            'name': 'Potato',
            'url': 'http://www.potatos.com',
        }
        super(TestUser,self).__init__(groups,attrs)

class TestConnection(Connection):

    _next_id = 0

    def message_id_next(self):
        if self._next_id:
            return self._next_id
        return super(TestConnection,self).message_id_next()
