from constants import *
from utils import *
import types
import re
import weakref

class ObjectWrapper(object):
    """ Helper class to wrap an object for controlling
        what a user can perform. The way the system determines
        what attributes are accessible is controlled via
        the "allow" and "deny" properties.

        By default, the system will deny all attributes.

        If an attribute has the property '_norpc', the system
        will immediately disallow the method regardless of 
        what the allow and deny properties hold.

        Then, the allow filter will be used to determine 
        what attributes are available.

        Finally the deny filter will trim out from that
        pool what a user can see. 

        It's kind of a DENY->allow->deny scheme.

        The allow and deny properties are arrays. If the array
        is empty, it is treated as to mean match nothing.

        Entries in the allow and deny properties must be regular
        expressions.

        To allow full access, do

        allow = ['.*']
        deny = []

        To allow everything except for entries starting with '_', do

        allow = ['.*']
        deny = ['_.*']

    """
    _obj = None
    _allow = []
    _deny = ['_.*']

    def __init__(self,obj,allow=None,deny=None,*args,**kwargs):
        """ Take the object to be wrapped so allow for 
            some access security on the functions.
        """
        self._setobj_(obj)
        if allow != None: self._allow = allow
        if deny != None: self._deny = deny
        self._init_(*args,**kwargs)

    @object_method_prevent_rpc
    def _init_(self,*args,**kwargs):
        """ To make the process of initialization easier
            Subclass this function and you don't need to 
            call super! ;)
        """
        pass

    @object_method_prevent_rpc
    def _setobj_(self,obj):
        """ Stores the object to be wrapped
        """
        self._obj = obj

    @object_method_prevent_rpc
    def _getobj_(self):
        """ Returns the object being wrapped
        """
        return self._obj

    @object_method_prevent_rpc
    def _getattr_(self,k):
        """ Determine if an attribute may be called
            or invoked.
        """

        # Then validate based upon the attributes
        obj_attr = getattr(self._getobj_(),k)
        if hasattr(obj_attr,'_norpc'):
            raise InvalidObjectMethod(k)

        # First the allow
        if not self._allow: 
            raise InvalidObjectMethod(k)
        for allow_regex in self._allow:
            if re.search(allow_regex,k):
                break
        else: raise InvalidObjectMethod(k)

        # Then the deny
        for deny_regex in self._deny:
            if re.search(deny_regex,k):
                raise InvalidObjectMethod(k)

        # Made it through the gauntlet, it's okay
        return obj_attr

    def __getattr__(self,k):
        """ Any attribute that doesn't belong to us we'll 
            proxy it through to the associated object. Before
            we do that, however, we'll ensure that some basic
            checks are performed to determine if a user's allowed
            to access that attribute.
        """
        obj_attr = self._getattr_(k)
        if isinstance(obj_attr,types.UnboundMethodType) or \
           isinstance(obj_attr,types.FunctionType) or \
           isinstance(obj_attr,types.BuiltinFunctionType) or \
           isinstance(obj_attr,types.BuiltinMethodType) \
           : 
            return lambda *a,**kw: obj_attr(*a,**kw)
        return obj_attr

    def __dir__(self):
        obj = self._getobj_()
        dir_data = []
        for k in dir(obj):
            try:
                self._getattr_(k)
                dir_data.append(k)
            except:
                pass
        return dir_data


class WeakrefObjectWrapper(ObjectWrapper):
    """ Used when you don't want to have the reference
        counter notice you're using an object
    """

    @object_method_prevent_rpc
    def _setobj_(self,obj):
        """ Stores the object to be wrapped as a weakerf
        """
        self._obj = weakref(obj)

    @object_method_prevent_rpc
    def _getobj_(self):
        """ Returns the object being wrapped
        """
        return self._obj()



