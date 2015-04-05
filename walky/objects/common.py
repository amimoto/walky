import types
import re
import weakref

from walky.constants import *
from walky.acl import *
from walky.utils import *

def object_id(obj):
    """ Returns the id of the underlying object if wrapped.
        If not wrapped, returns the object's id.
    """
    if isinstance(obj,ObjectWrapper):
        return obj.id()
    else:
        return id(obj)

def is_wrapped(obj):
    return isinstance(obj,ObjectWrapper)

class ObjectWrapper(ACLMixin):
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


    """
    _obj = None
    _connection = None
    _acls_ = []

    def __init__(self,obj,connection,*args,**kwargs):
        """ Take the object to be wrapped so allow for 
            some access security on the functions.
        """
        self._setobj_(obj)
        self.connection(connection)
        self._init_(*args,**kwargs)

    @object_method_prevent_rpc
    def id(self):
        """ Return the id of the underlying object
        """
        return id(self._getobj_())

    @object_method_prevent_rpc
    def connection(self,connection=None):
        """ Returns the current associated connection object
            If a connection is provided, load the connection into 
            the object
        """
        if connection is not None:
            self._connection = weakref.ref(connection)
        return self._connection()

    @object_method_prevent_rpc
    def fqn(self):
        """ Returns the fully qualified name of the module
        """
        obj = self._getobj_()
        return obj.__module__+"."+obj.__class__.__name__

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
    def _is_norpc(self,obj_attr):
        return hasattr(obj_attr,'_norpc')

    @object_method_prevent_rpc
    def _getattr_(self,k):
        """ Determine if an attribute may be called
            or invoked.
        """

        # Then validate based upon the attributes
        obj_attr = getattr(self._getobj_(),k)
        if self._is_norpc(obj_attr):
            raise InvalidObjectMethod(k)

        if not self._acl_allows(self.connection().user(),k,MODE_READ):
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
        if is_function(obj_attr):
            if not self._acl_allows(
                        self.connection().user(),
                        k,
                        MODE_EXECUTE
                      ):
                raise InvalidObjectMethod(k)
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
        self._obj = weakref.ref(obj)

    @object_method_prevent_rpc
    def _getobj_(self):
        """ Returns the object being wrapped
        """
        return self._obj()


##################################################
# Object Stubs:
# These are used by the client.
##################################################

class ObjectStub(object):
    """ When an object reference gets sent over the wire to 
        a remote system, this class is a handle to the server's object.
        Heavily overloaded, the object will proxy requests through
        the connection to make the process seem somewhat transparent.

        Note the weird naming, we're trying to prevent collisions between
        our functions and potential objects.

        FIXME: It's probably better to use __getattribute__ for real 
        transparency
    """

    _walky_connection_weakref = None
    reg_obj_id = None

    def __init__(self,connection,reg_obj_id):
        self._walky_connection(connection)
        self.reg_obj_id = reg_obj_id

    def _walky_connection(self,connection=None):
        if connection:
            self._walky_connection_weakref = weakref.ref(connection)
        return self._walky_connection_weakref and self._walky_connection_weakref()

    def __getattr__(self,k):
        return self._walky_connection().object_attr_request(self.reg_obj_id,k)

    def __setattr__(self,k,v):
        if hasattr(self,k):
            object.__setattr__(self,k,v)
        else:
            return self._walky_connection().object_attr_set_request(self.reg_obj_id,k,v)

    def __dir__(self):
        return self._walky_connection().object_dir_request(self.reg_obj_id)

    def __del__(self):
        return self._walky_connection().object_del_request(self.reg_obj_id)


