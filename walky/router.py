import weakref 

from walky.objects import *
from walky.utils import *

class Router(object):

    _map = None

    def __init__(self,*args,**kwargs):
        self.reset()
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

    def map(self,obj,context,*args,**kwargs):
        user = context.user()

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
                return wrapper(obj,context,*args,**kwargs)

            elif isinstance(obj,src):
                return wrapper(obj,context,*args,**kwargs)

        raise InvalidObject()




