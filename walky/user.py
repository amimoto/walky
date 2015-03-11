
class User(object):
    """ Simple object to hold key-value permission information 
        Includes support for auditing and locking down values
    """
    _attributes = None
    _groups = None
    _lock = False
    authenticated = False

    def __init__(self,groups=None,attributes=None):
        self._attributes = attributes or {}
        self._groups = set(groups or [])

    def lock(self):
        self._lock = True

    def in_group(self,group):
        return group in self._groups

    def groups(self):
        return self._groups

    def __getattr__(self,k):
        return self._attributes.get(k)

    def __setattr__(self,k,v):
        if self._lock:
            raise Exception("Cannot alter locked Permissions %s = %s" % (k,repr(v)))
        if k in('_attributes','_lock','_groups'):
            object.__setattr__(self,k,v)
        else:
            self._attributes[k] = v

