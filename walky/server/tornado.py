from __future__ import absolute_import

import os
import logging
import threading
import Queue

from tornado import websocket, web
from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer
from tornado.web import FallbackHandler
from walky.engine import *

_logger = logging.getLogger(__name__)

cl = []
class TornadoWebsocketPort(Port):
    def __init__(self,id,handler,*args,**kwargs):
        super(TornadoWebsocketPort,self).__init__(id,*args,**kwargs)
        self._handler = weakref.ref(handler)
        self.send_queue = Queue.Queue()

    def send_queued(self):
        line = ''
        while not self.send_queue.empty():
            line += self.send_queue.get()
        if line: 
            _logger.debug(u'sent %s', line)
            self._handler().write_message(line.encode('utf8'))

    def _sendline(self,line):
        self.send_queue.put(line)
        IOLoop.instance().add_callback(self.send_queued)

class TornadoWebsockHandler(websocket.WebSocketHandler):

    def __init__(self,*args,**kwargs):
        engine = kwargs['engine']
        del kwargs['engine']

        super(TornadoWebsockHandler,self).__init__(*args,**kwargs)

        self._port = engine.port_new(TornadoWebsocketPort,self)
        self._conn = engine.connection_new(port=self._port)

    def check_origin(self, origin):
        """ We don't worry where the requests come from 
            (at the moment)
        """
        return True

    def open(self):
        # FIXME
        if self not in cl:
            cl.append(self)

    def on_close(self):
        # FIXME
        _logger.debug(u'Client Disconnect')
        if self in cl:
            cl.remove(self)

    def on_message(self,message):
        """ FIXME: Assumes on_message is a readline
        """
        _logger.debug(u'received %s', message)
        self._port.on_receiveline(message)

class TornadoSocketServerPort(Port):
    def init(self,stream,address,*args,**kwargs):
        self.stream = stream
        self.address = address

        _logger.debug(u'Client Connect from: %s', address)

        self.read_next()
        self.stream.set_close_callback(self.on_close)

        self.socket_open = True
        self.send_queue = Queue.Queue()

    def send_queued(self):
        line = ''
        while not self.send_queue.empty():
            line += self.send_queue.get()
        if line: 
            _logger.debug(u'sent %s', line)
            self.stream.write(line.encode('utf8'))

    def read_next(self):
        self.stream.read_until('\n', self.on_receiveline)

    def on_receiveline(self, line):
        super(TornadoSocketServerPort,self).on_receiveline(line)
        self.read_next()

    def _sendline(self,line):
        self.send_queue.put(line)
        IOLoop.instance().add_callback(self.send_queued)

    def on_close(self):
        self.socket_open = False
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

    websock_port = WALKY_WEBSOCK_PORT
    websock_route = r'/walky'
    socket_port = WALKY_SOCKET_PORT
    socket_server_class = TornadoSocketServer
    websock_handler_class = TornadoWebsockHandler
    engine_class = Engine

    websock_enable = True
    socket_enable = True

    def __init__(self,**settings):
        settings.setdefault('websock_port',self.websock_port)
        settings.setdefault('websock_route',self.websock_route)
        settings.setdefault('socket_port',self.socket_port)

        settings.setdefault('websock_enable',self.websock_enable)
        settings.setdefault('socket_enable',self.socket_enable)

        settings.setdefault('ssl_options',None)
        settings.setdefault('data_path','walkydata')
        settings.setdefault('wsgi_fallback_handler',None)

        settings.setdefault('socket_server_class',self.socket_server_class)
        settings.setdefault('websock_handler_class',self.websock_handler_class)
        settings.setdefault('engine_class',self.engine_class)

        self.settings = settings

        self.reset()

    def reset(self):
        if self.engine: self.engine.shutdown()
        self.engine = self.settings['engine_class']()

    def run(self):
        settings = self.settings
        data_dir = settings['data_path']

        self.engine.start()

        if settings.get('websock_enable'):
            web_routes = [(settings['websock_route'], 
                           settings['websock_handler_class'],
                           {'engine':self.engine})]
            if settings['wsgi_fallback_handler']:
                web_routes.append((
                          r'.*',
                          FallbackHandler,
                          {'fallback':settings['wsgi_fallback_handler']}))

            self.websock_server = web.Application(web_routes)
            self.websock_server.listen(
                                          settings['websock_port'],
                                          ssl_options=settings['ssl_options']
                                      )

        if settings.get('socket_enable'):
            self.socket_server = settings['socket_server_class'](
                                          self,ssl_options=settings['ssl_options']
                                      )
            self.socket_server.listen(settings['socket_port'])

        if not ( settings.get('socket_enable') or settings.get('websock_enable') ):
            raise Exception('Please enable at least one of websock_enable or socket_enable')

        try:
            IOLoop.instance().start()
        except KeyboardInterrupt:
            self.shutdown()
            raise

    def shutdown(self):
        self.engine.shutdown()
        IOLoop.instance().stop()




