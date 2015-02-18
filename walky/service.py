import os
import base64

from constants import *
from objects import *
import serializer

class Service(object):
    """ Represent a single session.

        This object holds the data associated with the
        entire session such as associated object and 
        even the metadata (things such as the session key)

    """

    def __init__(self,objects_global=None,*args,**kwargs):
        self.reset()

        # 2048bit random value as session id
        id = base64.b64encode(os.urandom(256))
        self.id = id
        self.objects_global = objects_global or {}

        # Some important global objects
        self.objects_global['?'] = RPCInterrogation(self)

    def reset(self):
        self.object_registry = {}

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
            raise InvalidObjectMethod(obj_attr)

    def object_exec(self,obj_id,method,args=[],kwargs={}):
        """ Fetch the object associated with the obj_id
            then retreive and invoke the method with provided
            arguments. 
        """
        obj_attr = self.object_getattr(obj_id,method)
        if hasattr(obj_attr,'_norpc'):
            raise InvalidObjectMethod(obj_attr)
        result = obj_attr(*args,**kwargs)
        return result

