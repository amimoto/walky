import os
import base64

class Controller(object):
    _services = None
    _ports = None

    def __init__(self):
        self.reset()

    def reset(self):
        self._services = {}
        self._ports = {}

    def id_generate(self):
        """ Returns a cryptographically secure 64 bit unique key in 
            base64 format. This method ensures that the ID will not 
            collide with any sensitive object in the system.
        """
        while True:
            id = base64.b64encode(os.urandom(8))[:-1]
            if id in self._services: continue
            if id in self._ports: continue
            break
        return id

    def service_add(self,service):
        self._services[service.id] = service

    def service_delete(self,service_id):
        del self._services[service_id]

    def service_get(self,service_id):
        return self._services[service_id]

    def service_new(self,service_class,*args,**kwargs):
        """ Helper to create, register a new service object
        """
        service = service_class(
                      self.id_generate(),
                      controller=self,
                      *args, **kwargs)
        self.service_add(service)
        return service

    def port_add(self,port):
        self._ports[port.id] = port

    def port_new(self,port_class,*args,**kwargs):
        """ Helper to create, register a new port object
        """
        port = port_class(
                      self.id_generate(),
                      controller=self,
                      *args, **kwargs)
        self.port_add(port)
        return port

    def broadcast(self,channel_id,message):
        """ Sends a message to all listeners on a channel
        """
        pass

    def connect(self,port_id,service_id):
        """ Takes a port_id as well as a service_id and
            connects the two of them together
        """
        if port_id not in self._ports: raise InvalidPortID()
        if service_id not in self._services: raise InvalidPortID()

        port = self._ports[port_id]
        service = self._services[service_id]

        # We're going to unhook the original service and 
        # port
        old_service = port.service()
        if old_service: old_service.port(None)
        old_port = service.port()
        if old_port: old_port.service(None)

        # Alice meet Bob, Bob meet Alice. 
        # Everyone be friends.
        port.service(service)
        service.port(port)
