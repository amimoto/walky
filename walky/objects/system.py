import common

class Interrogation(common.WeakrefObjectWrapper):

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

