
import os
import base64
import json
import weakref

from walky.constants import *
from walky.objects.system import *
from walky.serializer import *

class Registry(object):
    """ This should contain information required at the 
        connection level to allow it to operate independantly
    """
    _objects_registry = None

    def __init__(self):
        self.reset()

    def reset(self):
        self._objects_registry = {}

    def get(self,obj_id):
        return self._objects_registry.get(obj_id)

    def put(self,obj):
        obj_id = hex(id(obj))[2:]
        self._objects_registry[obj_id] = obj
        return obj_id
        


