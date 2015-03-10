import unittest
import time
import os
import base64

from walky.user import *
from walky.constants import *
from walky.context import *
from walky.router import *
from walky.serializer import *
from walky.dispatcher import *
from walky.port import *
from walky.messenger import *

from _common import *

class Service(object):

    contexts = {}
    crew = None

    def __init__(self,*args,**kwargs):
        self.reset()
        self.init(*args,**kwargs)

    def reset(self):
        self.shutdown()
        self.crew = WorkerCrew()
        self.router = Router()
        self.serializer = Serializer()

    def start(self):
        self.crew.start()

    def init(self,*args,**kwargs):
        pass

    def shutdown(self):
        if self.crew:
            self.crew.shutdown()

    def connection_new(self):
        """ Creates a new connection by instantiating a new context
        """
        context_id = self.id_generate()
        sys_reg = Registry()
        sess_reg = Registry()
        conn_reg = Registry()
        user = User(['anon'])
        messenger = Messenger()
        context = Context(
                      context_id,
                      user=user,
                      sys=sys_reg,
                      sess=sess_reg,
                      conn=conn_reg,
                      router=self.router,
                      crew=self.crew,
                      serializer=self.serializer,
                      messenger=messenger,
                  )

        return context

    def id_generate(self):
        """ Returns a cryptographically secure 64 bit unique key in 
            base64 format. This method ensures that the ID will not 
            collide with any sensitive object in the system.
        """
        while True:
            id = base64.b64encode(os.urandom(8))[:-1]
            if id in self.contexts: continue
            #if id in self._services: continue
            #if id in self._ports: continue
            break
        return id

