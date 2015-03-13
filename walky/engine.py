import unittest
import time
import os
import base64

from walky.user import *
from walky.constants import *
from walky.connection import *
from walky.router import *
from walky.serializer import *
from walky.port import *
from walky.messenger import *

from _common import *

class Engine(object):

    connections = {}
    crew = None
    router = None
    serializer = None

    anon_user = None

    def __init__(self,*args,**kwargs):
        self.reset()
        self.init(*args,**kwargs)

    def reset(self):
        self.shutdown()
        self.crew = WorkerCrew()
        self.router = Router()
        self.serializer = Serializer()

        user = User(['anonymous'])
        user.lock()
        self.anon_user = user

    def start(self):
        self.crew.start()

    def init(self,*args,**kwargs):
        pass

    def shutdown(self):
        if self.crew:
            self.crew.shutdown()

    def port_new(self,port_class=Port,*args,**kwargs):
        port_id = self.id_generate()
        port = port_class(
                    port_id,
                    *args,
                    **kwargs
                )
        return port


    def connection_new(self,
                        connection_class=Connection,
                        sys_reg=None,
                        sess_reg=None,
                        conn_reg=None,
                        *args,
                        **kwargs):
        """ Creates a new connection by instantiating a new connection
        """
        connection_id = self.id_generate()
        user = self.anon_user
        messenger = Messenger()
        connection = connection_class(
                        connection_id,
                        *args,
                        engine=self,
                        user=user,
                        sys=sys_reg or Registry(),
                        sess=sess_reg or Registry(),
                        conn=conn_reg or Registry(),
                        messenger=messenger,
                        **kwargs
                    )

        # Register the newly minted connection!
        self.connections[connection_id] = connection

        return connection

    def id_generate(self):
        """ Returns a cryptographically secure 64 bit unique key in 
            base64 format. This method ensures that the ID will not 
            collide with any sensitive object in the system.
        """
        while True:
            id = base64.b64encode(os.urandom(8))[:-1]
            if id in self.connections: continue
            #if id in self._services: continue
            #if id in self._ports: continue
            break
        return id

