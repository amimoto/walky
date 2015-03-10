
import os
import base64
import json
import weakref

from walky.constants import *
from walky.objects import *
from walky.objects.system import *
from walky.serializer import *

def reg_object_id(obj):
    """ Returns the registry encoded version of an object's id
        Uses walky.objects.common.object_id so it will dig down to the
        underlying object's id if required.
    """
    obj_id = object_id(obj)
    return hex(obj_id)[2:]


class Registry(object):
    """ This should contain information required at the 
        connection level to allow it to operate independantly
    """
    _objects_registry = None

    def __init__(self):
        self.reset()

    def reset(self):
        self._objects_registry = {}

    def get(self,reg_obj_id):
        return self._objects_registry.get(reg_obj_id)

    def put(self,obj,reg_obj_id=None):
        """ Register an object. If reg_obj_id is provided, force
            the reg_obj_id to be a certain key
        """
        if not reg_obj_id:
            reg_obj_id = reg_object_id(obj)
        self._objects_registry[reg_obj_id] = obj
        return reg_obj_id
        
    def delete(self,reg_obj_id):
        if reg_obj_id in self._objects_registry:
            del self._objects_registry[reg_obj_id]

