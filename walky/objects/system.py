from walky.utils import *
from walky.objects.common import *
from walky.serializer import *

class ObjectService(WeakrefObjectWrapper):
    """ Base class for most system oriented commands. 
        This allows for accessing of the parent service object
        and its object respository
    """

class Interrogation(WeakrefObjectWrapper):
    """ Provide the ability to query objects in the repository
    """

    mappings = {
        '?': 'object_attr_request',
        '=': 'object_attr_set_request',
        'dir': 'object_dir_request',
    }

    # FIXME: want directly accessible objects too
    def __init__(self,connection,*args,**kwargs):
        super(Interrogation,self).__init__(None,connection)

    def _setobj_(self,*a,**kw):
        pass

    def _getobj_(self,*a,**kw):
        pass

    def __getattr__(self,k):
        if k in self.mappings:
            return lambda *a,**kw: getattr(self,self.mappings[k])(*a,**kw)
        raise KeyError

    def object_attr_request(self,reg_obj_id,attribute):
        obj = self.connection().object_get(reg_obj_id)
        attr = getattr(obj,attribute)
        if is_function(attr):
            return ObjectMethod
        return attr

    def object_attr_set_request(self,reg_obj_id,attribute,value):
        obj = self.connection().object_get(reg_obj_id)
        setattr(obj,attribute,value)
        return True

    def object_dir_request(self,reg_obj_id):
        obj = self.connection().object_get(reg_obj_id)
        return dir(obj)
