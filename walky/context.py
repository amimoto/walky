from walky.registry import *

class Context(object):
    _sys = None
    _conn = None
    _sess = None
    _user = None

    def __init__(self,**kwargs):
        for k,v in kwargs.iteritems():
            setattr(self,"_"+k,v)

    def reset(self):
        self._sys = None
        self._conn = None
        self._sess = None

    def _get_set_attribute(self,k,v=None):
        if not v is None:
            setattr(self,k,v)
        return getattr(self,k)

    def __getattr__(self,k):
        attr_name = "_" + k
        object.__getattribute__(self,attr_name)
        return lambda a=None: self._get_set_attribute(attr_name,a)



