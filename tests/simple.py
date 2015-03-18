import time
import threading
import os
import logging
import datetime

import Queue

from walky.worker import *
from walky.engine import *

from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer
from tornado import websocket, web

_logger = logging.getLogger(__name__)

ports = []

class MyWorkerRequest(WorkerRequest):
    def __init__(self,port,line):
        self.port = port
        self.line = line

    def execute(self):
        self.port.sendline("REPLY:{}\r\n".format(self.line).encode('utf8'))

crew_obj = WorkerCrew()
crew_obj.start()

class Connection(object):
    def __init__(self, stream,address):
        self.stream = stream
        self.stream.set_close_callback(self.on_close)
        self.read_next()
        self.address = address

        self.send_queue = Queue.Queue()
        self.send_queue_thread = threading.Thread(target=self.send_queue_loop)
        self.send_queue_thread.start()

    def send_queue_loop(self):
        while 1:
            l = self.send_queue.get()
            self._sendline(l)

    def read_next(self):
        self.stream.read_until('\n', self.on_receiveline)

    def on_receiveline(self, line):
        line = line.decode('utf8').strip()
        print "LINE WAS:", line
        exec_obj = MyWorkerRequest(self,line)
        crew_obj.put(exec_obj)
        self.read_next()

    def on_send_complete(self):
        _logger.debug('wrote a line to %s', self.address)
        if self.stream.closed(): return
        if self.stream.reading(): return

    def sendline(self,line):
        self.send_queue.put(line)

    def _sendline(self,line):
        self.stream.write(line.encode('utf8'),self.on_send_complete)

    def on_close(self):
        _logger.debug('client quit %s', self.address)


class TornadoSocketServer(TCPServer):
    def handle_stream(self, stream, address):
        global ports
        conn = Connection(stream,address)
        print "INCOMING:", stream, address
        ports.append(conn)

    def run(self):
        IOLoop.instance().start()

settings = {}
settings.setdefault('data_path','walkydata')
settings.setdefault('ssl_cert_fpath','ssl.crt')
settings.setdefault('ssl_key_fpath','ssl.key')

data_dir = settings['data_path']
ssl_options = {
    "certfile": os.path.join(data_dir, settings['ssl_cert_fpath']),
    "keyfile": os.path.join(data_dir, settings['ssl_key_fpath']),
}
socket_server = TornadoSocketServer(ssl_options=ssl_options)
socket_server.listen(8663)

# Start the server
server_pool = threading.Thread(target=lambda *a: socket_server.run())  
server_pool.daemon = False
server_pool.start()
print "STARTED"

time.sleep(3600)

