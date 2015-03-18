import time
import os
import logging
import datetime
import sys

from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

ports = []

class Connection(object):
    def __init__(self, stream,address):
        self.stream = stream
        self.address = address
        self.read_next()

    def read_next(self):
        self.stream.read_until('\n', self.on_receiveline)

    def on_receiveline(self, line):
        line = line.decode('utf8').strip()
        self.read_next()
        print "LINE WAS:", line
        for i in range(10):
            self.sendline(line.encode('utf8'))

    def sendline(self,line):
        self.stream.write(line)


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

