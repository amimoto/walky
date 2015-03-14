import weakref

from walky.port import *

class ClientPort(Port):
    pass

class Client(object):

    engine = None
    settings = None

    socket_host = None
    socket_port = 8662
    engine_class = Engine
    port_class = ClientPort
    object_class = ClientObject  # FIXME: Should be stub

    def __init__( self,
                  **settings
                  ):
        
        settings.setdefault('socket_host',self.socket_host)
        settings.setdefault('socket_port',self.socket_port)

        settings.setdefault('engine_class',self.engine_class)
        settings.setdefault('port_class',self.port_class)
        settings.setdefault('object_class',self.object_class)

        self.port = kwargs.get('port')
        self.settings = settings

    def connect(self,*args,**kwargs):
        port = self.settings['port_class'](
                    self.settings['socket_host']
                    +":"+self.settings[]
                    ,
                )


    def reset(self):
        if self.engine: self.engine.shutdown()
        self.engine = self.settings['engine_class']()

    def on_readline(self,line):
        try:
            pass
        except Exception as ex:
            pass

    def sendline(self,line):
        self.port().sendline(line)

    def object_get(self,reg_obj_id):
        return self.object_class(self,reg_obj_id)

    def interrogate_attribute(self,k):
        """ Craft a request that interrogates the remote
            server
        """
        pass

    def shutdown(self):
        self.engine.shutdown()





