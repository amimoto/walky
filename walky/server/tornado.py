from __future__ import absolute_import

import os
import logging

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado.tcpserver import TCPServer
from tornado import websocket, web

from walky.engine import *

_logger = logging.getLogger(__name__)

class TornadoWebsockServer(websocket.WebSocketHandler):
    def check_origin(self, origin):
        """ We don't worry where the requests come from 
            (at the moment)
        """
        return True

class TornadoSocketServerPort(Port):
    def init(self,stream,address,*args,**kwargs):
        self.stream = stream
        self.address = address
        self.read_next()
        self.stream.set_close_callback(self.on_close)

    def read_next(self):
        self.stream.read_until('\n', self.on_receiveline)

    def on_receiveline(self, line):
        line = line.decode('utf8').strip()
        super(TornadoSocketServerPort,self).on_receiveline(line)

    def on_send_complete(self):
        _logger.debug('wrote a line to %s', self.address)
        if self.stream.closed(): return
        if self.stream.reading(): return
        self.read_next()

    def _sendline(self,line):
        self.stream.write(line,self.on_send_complete)

    def on_close(self):
        _logger.debug('client quit %s', self.address)


class TornadoSocketServer(TCPServer):
    def __init__(self,server,*args,**kwargs):
        self.server = server
        super(TornadoSocketServer,self).__init__(*args,**kwargs)

    def handle_stream(self, stream, address):
        port = self.server.engine.port_new(
                                      TornadoSocketServerPort,
                                      stream, address
                                  )
        conn = self.server.engine.connection_new(port=port)

class TornadoServer(object):
    engine = None
    settings = None

    def __init__(self,**settings):
        settings.setdefault('websock_port',8662)
        settings.setdefault('socket_port',8663)
        settings.setdefault('data_path','walkydata')
        settings.setdefault('ssl_cert_fpath','ssl.crt')
        settings.setdefault('ssl_key_fpath','ssl.key')
        settings.setdefault('wsgi_fallback_handler',None)

        settings.setdefault('socket_server_class',TornadoSocketServer)
        settings.setdefault('websocket_server_class',TornadoWebsockServer)
        settings.setdefault('engine_class',Engine)

        self.settings = settings

        self.reset()

    def reset(self):
        if self.engine: self.engine.shutdown()
        self.engine = self.settings['engine_class']()

    def run(self):
        settings = self.settings
        data_dir = settings['data_path']

        self.engine.start()

        web_routes = [(r'/websocket', settings['websocket_server_class'])]
        if settings['wsgi_fallback_handler']:
            web_routes.append((r'.*',settings['wsgi_fallback_handler']))

        ssl_options = {
            "certfile": os.path.join(data_dir, settings['ssl_cert_fpath']),
            "keyfile": os.path.join(data_dir, settings['ssl_key_fpath']),
        }

        self.websock_server = web.Application(web_routes)
        self.websock_server.listen(settings['websock_port'],ssl_options=ssl_options)

        self.socket_server = settings['socket_server_class'](self,ssl_options=ssl_options)
        self.socket_server.listen(settings['socket_port'])

        try:
            IOLoop.instance().start()
        except KeyboardInterrupt:
            IOLoop.instance().stop()
            self.engine.shutdown()




