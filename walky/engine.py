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
from walky.objects.system import *

class Engine(object):

    connections = {}
    crew = None
    router = None
    serializer = None

    anon_user = None

    reap_last = None
    reap_interval = 1

    def __init__(self,*args,**kwargs):
        self.reset()
        self.init(*args,**kwargs)

    def reset(self):
        self.shutdown()
        self.crew = WorkerCrew()
        self.router = Router()
        self.serializer = Serializer()
        self.last_reap = time.time()

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

    def registry_system_new(self,reg_class=Registry,*args,**kwargs):
        return reg_class(*args,**kwargs)

    def connection_reaper(self):
        """ Go through and reap the expired children
        """
        connections = dict(self.connections)
        for connection_id,connection in connections.iteritems():
            if connection.stale():
                self.connection_del(connection_id)

    def connection_del(self, connection_id):
        """ Remove the connection from the pool
        """
        if connection_id in self.connections:
            self.connections[connection_id].close()
            del self.connections[connection_id]

    def connection_new(self,
                        connection_class=Connection,
                        sys_reg=None,
                        sess_reg=None,
                        conn_reg=None,
                        *args,
                        **kwargs):
        """ Creates a new connection by instantiating a new connection
        """
        if self.reap_last <= time.time() + self.reap_interval:
            self.connection_reaper()
            self.reap_last = time.time()

        connection_id = self.id_generate()
        user = self.anon_user
        messenger = Messenger()
        connection = connection_class(
                        connection_id,
                        *args,
                        engine=self,
                        user=user,
                        sys=sys_reg or self.registry_system_new(),
                        sess=sess_reg or Registry(),
                        conn=conn_reg or Registry(),
                        messenger=messenger,
                        **kwargs
                    )

        # Add some system objects
        interrogation = Interrogation(connection)
        connection.sys().put(interrogation,'?')

        # Register the newly minted connection!
        self.connections[connection_id] = connection

        return connection

    def connection_close(self,connection_id):
        """ Force close a connection.
        """
        # TODO

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

