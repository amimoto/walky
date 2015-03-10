from walky.registry import *

class Context(object):
    _sys = None
    _sess = None
    _conn = None
    _user = None
    _router = None
    _port = None
    _crew = None
    _dispatch = None
    _serializer = None
    _queue = None
    _messenger = None
    id = None

    def __init__(self,context_id,**kwargs):
        self.id = context_id
        for k,v in kwargs.iteritems():
            setattr(self,"_"+k,v)

    def registries(self,include_global=True):
        """ Returns a list of all registries that we should scan
        """
        reg_list = [self.sess(),self.conn()]
        if include_global:
            reg_list.insert(0,self.sys())
        return filter(None,reg_list)

    def object_get(self,reg_obj_id):
        """ Attempt to retreive the object via search through the 
            object registry.
        """
        for reg in self.registries():
            obj = reg.get(reg_obj_id)
            if obj: return obj
        return None

    def object_exec(self,reg_obj_id,method,*args,**kwargs):
        """ Execute an object's method
        """
        obj = self.object_get(reg_obj_id)
        result = getattr(obj,method)(*args,**kwargs)
        return result

    def object_delete(self,reg_obj_id,include_global=False):
        """ Removes an object from the registry. Note that
            the system will not comply with the request to remove
            an object from the global registry unless include_global
            is set to true
        """
        for reg in self.registries(include_global):
            reg.delete(reg_obj_id)

    def object_registered(self,obj):
        """ This will scan the registries to find out if the 
            object has already been registered. 
            If already registered, returns the object_id. 
            If not, returns None
        """
        reg_obj_id = reg_object_id(obj)
        for reg in self.registries():
            if reg.get(reg_obj_id): 
                return reg_obj_id
        return None

    def _get_set_attribute(self,k,v=None):
        if not v is None:
            setattr(self,k,v)
        return getattr(self,k)

    def __getattr__(self,k):
        attr_name = "_" + k
        object.__getattribute__(self,attr_name)
        return lambda a=None: self._get_set_attribute(attr_name,a)



