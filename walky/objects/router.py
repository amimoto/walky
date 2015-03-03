import weakref 

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
        self._map = []

    def context(self,context=None):
        if context is not None:
            self._context = weakref.ref(context)
        return self._context()

    def mapper(self,source_class,mapped_class):
        self._map.append([
            source_class,
            mapped_class
        ])

    def map(self,obj,*args,**kwargs):
        for m in self._map:
            src = m[SOURCE_CLASS]
            wrapper = m[MAPPED_CLASS]

            if is_function(src):
                if not src(obj): continue
                return wrapper(obj,self.context(),*args,**kwargs)

            elif isinstance(obj,src):
                return wrapper(obj,self.context(),*args,**kwargs)

        raise InvalidObject()




