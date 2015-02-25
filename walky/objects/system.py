import common

class ObjectService(common.WeakrefObjectWrapper):
    """ Base class for most system oriented commands. 
        This allows for accessing of the parent service object
        and its object respository
    """

class Interrogation(common.WeakrefObjectWrapper):
    """ Provide the ability to query objects in the repository
    """

    def dir(self,obj_id):
        """ Return the current list of attributes for
            an object
        """
        attributes = dir(self._getobj_())
        return 

    def delete(self,obj_id):
        """ Free the object resource
        """
        return RPCNormalizedStruct([
            self._getobj_().object_del(obj_id)
        ])

    def __getattr__(self,k):
        try:
            (obj_id,method) = k.split('.')
            service = self._getobj_()
            obj = service.object_get(obj_id)
            return lambda *a,**kw: getattr(obj,method)
        except ValueError:
            raise KeyError


