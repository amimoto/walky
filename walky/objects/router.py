import weakref 

from walky.objects import *
from walky.utils import *

class Router(object):

    _map = None
    _context = None

    def __init__(self,context,*args,**kwargs):
        self.reset()
        self.context(context)
        self.init(*args,**kwargs)

    def init(self,*args,**kwargs):
        pass

    def reset(self):
        self._context = None
        self._map = []

    def mapper(self,groupname,source_class,mapped_class):
        self._map.append([
            groupname,
            source_class,
            mapped_class
        ])

    def context(self,context=None):
        """ Returns the current associated context object
            If a context is provided, load the context into 
            the object
        """
        if context is not None:
            self._context = weakref.ref(context)
        return self._context()

    def map(self,obj,*args,**kwargs):
        user = self.context().user()

        if is_wrapped(obj):
            return obj

        for m in self._map:
            group = m[TARGET_GROUP]
            if not user.in_group(group):
                continue
            src = m[SOURCE_CLASS]
            wrapper = m[MAPPED_CLASS]

            if is_function(src):
                if not src(obj): continue
                return wrapper(obj,*args,**kwargs)

            elif isinstance(obj,src):
                return wrapper(obj,*args,**kwargs)

        raise InvalidObject()




