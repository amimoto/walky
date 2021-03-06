from __future__ import absolute_import

import weakref
import threading
import asyncore
import socket

from walky.objects import *
from walky.port import *
from walky.engine import *

class Client(object):

    engine = None
    settings = None
    connection = None
    port = None

    engine_class = Engine
    object_class = ObjectStub

    def __init__( self,
                  **settings ):
        settings.setdefault('engine_class',self.engine_class)
        settings.setdefault('port_class',self.port_class)
        settings.setdefault('object_class',self.object_class)

        self.port = settings.get('port')
        self.settings = settings

        self.reset()

    def reset(self):
        if self.engine: self.engine.shutdown()
        self.engine = self.settings['engine_class']()

    def connect(self,*args,**kwargs):
        """ Start the engine and the asyncore
        """
        self.engine.start()
        self.connection = self.engine.connection_new(*args,**kwargs)

    def run(self):
        pass

    def on_readline(self,line):
        try:
            pass
        except Exception as ex:
            pass

    def sendline(self,line):
        self.port().sendline(line)

    def object_get(self,reg_obj_id):
        return self.object_class(self.connection,reg_obj_id)

    def close(self):
        self.engine.shutdown()





