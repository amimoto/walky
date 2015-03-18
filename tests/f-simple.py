import time
import threading
import Queue

from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer

from walky.engine import *
from walky.worker import *

ports = []

"""
class MyWorkerRequest(WorkerRequest):
    def __init__(self,port,line):
        self.port = port
        self.line = line

    def execute(self):
        f = self.port.sendline("REPLY:{}\r\n".format(self.line))

crew_obj = WorkerCrew(1)
crew_obj.start()
"""

handler_queue = Queue.Queue()
handler_pool = []
def handler():
    while 1:
        (conn,line) = handler_queue.get()
        conn.sendline("SENDING BACK: {}\r\n".format(line))
    
for i in range(1):
    thread = threading.Thread(target=handler)
    thread.start()
    handler_pool.append(thread)

class Connection(object):
    def __init__(self,stream):
        self.stream = stream

        self.queue = Queue.Queue()
        self.queue_loop = threading.Thread(target=self.queue_loop_thread)
        self.queue_loop.start()

        self.read_next()
        self.lock = threading.Lock()

    def queue_loop_thread(self):
        while 1:
            l = self.queue.get()
            self.lock.acquire(True)
            self.stream.write(l.encode('utf8'),self.lock.release)

    def read_next(self):
        self.stream.read_until('\n', self.on_receiveline)

    def on_receiveline(self, line):
        line = line.decode('utf8').strip()
        self.read_next()
        print "RECEIVED",line
        handler_queue.put((self,line))

    def sendline(self,line):
        self.queue.put(line)


class TornadoSocketServer(TCPServer):
    def handle_stream(self, stream, address):
        global ports
        conn = Connection(stream)
        ports.append(conn)

    def run(self):
        IOLoop.instance().start()


data_dir = 'walkydata'
ssl_options = {
    "certfile": os.path.join(data_dir, 'ssl.crt'),
    "keyfile": os.path.join(data_dir, 'ssl.key'),
}
socket_server = TornadoSocketServer(ssl_options=ssl_options)
socket_server.listen(8663)
socket_server.run()

time.sleep(3600)

