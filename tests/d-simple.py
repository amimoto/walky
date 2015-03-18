from __future__ import absolute_import

import time
import os
import logging
import datetime
import sys
import Queue

from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer


from walky.engine import *
from walky.worker import *

ports = []

class MyWorkerRequest(WorkerRequest):
    def __init__(self,port,line):
        self.port = port
        self.line = line

    def execute(self):
        f = self.port.sendline("REPLY:{}\r\n".format(self.line))

crew_obj = WorkerCrew(1)
crew_obj.start()

class Connection(object):
    def __init__(self, stream,address):
        self.stream = stream
        self.address = address
        self.read_next()

        self.queue = Queue.Queue()
        self.queue_loop = threading.Thread(target=self.queue_loop_thread)
        self.queue_loop.start()

    def queue_loop_thread(self):
        while 1:
            l = self.queue.get()
            self.stream.write(l.encode('utf8'))

    def read_next(self):
        self.stream.read_until('\n', self.on_receiveline)

    def on_receiveline(self, line):
        line = line.decode('utf8').strip()
        self.read_next()
        self.sendline("REPLY:{}\r\n".format(line))

    def sendline(self,line):
        self.queue.put(line)


class TornadoSocketServer(TCPServer):
    def handle_stream(self, stream, address):
        global ports
        print "INCOMING:", stream, address
        conn = Connection(stream,address)
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
socket_server.run()

time.sleep(3600)

