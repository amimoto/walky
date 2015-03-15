import weakref
import asyncore
import socket

from common import *

class ClientSocketPort(asyncore.dispatcher):
    _connection = None

    def __init__(self,host,port,connection=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, port) )

        self.queue_send = []

        self.buffer_receive = ''

        self.connection(connection)

    def connection(self,connection=None):
        if connection:
            self._connection = weakref.ref(connection)
        return self._connection()

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        data = self.recv(8192)
        self.buffer_receive += data
        if not data.find('\n'): return
        en = data.split('\n')
        self.buffer_receive = en[-1]
        connection = self.connection()
        for line in map(lambda a:a+"\n", en[:-1]):
            connection.on_readline(line)

    def writable(self):
        return self.queue_send

    def handle_write(self):
        sent = self.send(self.queue_send.pop())



class SocketClient(object):

    socket_host = None
    socket_port = 8662

    port_class = ClientPort

    def __init__(self,**kwargs):
        super(SocketClient,self).__init__(**kwargs)
        settings.setdefault('socket_host',self.socket_host)
        settings.setdefault('socket_port',self.socket_port)

    def connect(self,*args,**kwargs):
        port = self.settings['port_class'](
                    self.settings['socket_host']
                    +":"+self.settings['socket_port']
                    ,
                )
        # FIXME: Do we need to do something special with the port?
        self.port = port

