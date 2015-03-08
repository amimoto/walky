import os
import base64
import json
import weakref

from walky.constants import *
from walky.objects.system import *
from walky.serializer import *

class Handler(HandlerSerializer):
    """ Represent a single session.

        This object holds the data associated with the
        entire session such as associated object and 
        even the metadata (things such as the session key)

    """

    _controller = None
    _port = None
    _active = True
    _active_timeout = False

    def __init__(self,
                  id,
                  controller=None,
                  port=None,
                  objects_global=None,
                  *args,
                  **kwargs):

        self.reset()

        # Presets
        if controller: self.controller(controller)
        if port: self.port(port)

        # The ID should be a cryptographically secure
        # identifier. It's used as a secret to identify and
        # reconnect users to disconnected sessions
        self.id = id
        self.objects_global = objects_global or {}

        # Some important global objects
        self.objects_global['?'] = Interrogation(self)

    def active(self,active=None,active_timeout=None):
        """ Getter/Setter to describe the current state. The state is
            used by the automatic culling mechanism
        """
        if active is not None:
            self._active = active
        if active_timeout is not None:
            self._active_timeout = active_timeout
        if not self._active and self._active_timeout:
           if self._active_timeout > datetime.datetime.now():
              return True
        return self._active

    def controller(self,controller=False):
        """ Resolves the weakref to the controller.
            If an argument is supplied, it is assumed to be 
            a controller. Sets and returns the new controller object.
        """
        if controller is not False:
            self._controller = controller and weakref.ref(controller)
        return self._controller and self._controller()

    def port(self,port=False):
        """ Resolves the weakref to the port.
            If an argument is supplied, it is assumed to be 
            a port. Sets and returns the new port object.
        """
        if port is not False:
            self._port = port and weakref.ref(port)
        return self._port and self._port()

    def reset(self):
        """ Takes the handler and try and take it back to
            factory fresh settings
        """
        self.object_registry = {}
        self.controller(None)
        self.port(None)

    def object_get(self,obj_id):
        if obj_id in self.objects_global:
            return self.objects_global[obj_id]
        if obj_id not in self.object_registry:
            raise InvalidObjectID(obj_id)
        return self.object_registry[obj_id]

    def object_getattr(self,obj_id,method):
        obj = self.object_get(obj_id)
        try:
            obj_attr = getattr(obj,method)
            return obj_attr
        except:
            raise InvalidObjectMethod(method)

    def object_exec(self,obj_id,method,message_id,args=[],kwargs={}):
        """ Fetch the object associated with the obj_id
            then retreive and invoke the method with provided
            arguments. 
        """
        obj_attr = self.object_getattr(obj_id,method)
        if hasattr(obj_attr,'_norpc'):
            raise InvalidObjectMethod(obj_attr)
        result = obj_attr(*args,**kwargs)
        return result

    def json_request(self,json_request):
        """ The primary interface that most folks
            will be using. This will take the serialized
            JSON request, execute, and return the result

            The format of the request should be:

            [
                ObjectID:String,
                Method:String,
                MessageID:String,
                args:List (optional),
                kwargs:Object (optional)
            ]
        """
        request = json.loads(json_request)
        if len(request) < 3 and len(request) > 6:
            raise InvalidRequest()
        response = self.object_exec(*request)
        return self.dumps(response)



