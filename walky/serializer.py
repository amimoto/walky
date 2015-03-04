import json

from constants import *
from walky.registry import *
from utils import *

class NormalizedData(object):
    def __init__(self,data):
        self.data = data

class Serializer(object):
    """ This allows objects and structures to be encoded in JSON format

        Some Lingo:

        A denormalized struct is data that hasn't been converted into
        a format that's not amenable for Walky serialization. In other
        words, the "original" object.

        A normalized struct is a structure that's encoded in a format
        that's ready for Walky serialization (which is really just 
        JSON with certain rules)
    """

    def dumps(self,denormalized_struct):
        """ Converts the data provided into a serialized format
            ready for transport
        """

        normalized_struct = self.struct_normalize(denormalized_struct)
        return json.dumps(normalized_struct)

    def loads(self,s):
        """ Converts the received json serialized Walky object into
            a denormalized structure
        """
        normalized_struct = json.loads(s)
        return self.struct_denormalize(normalized_struct)

    def object_put(self,obj):
        """ Replace the object with a lookup reference
        """
        raise NotImplemented('object_put')

    def object_get(self,obj_id):
        """ Fetch the object based upon the lookup reference
        """
        raise NotImplemented('object_get')

    def object_del(self,obj_id):
        """ Remove the object from the registry (allowing
            the garbage collector to reap it)
        """
        raise NotImplemented('object_del')

    def struct_normalize(self,denormalized_struct):
        """ Normalize a structure. Turn it into the structure
            format expected for serialization.
        """

        if isinstance(denormalized_struct,NormalizedData):
            return denormalized_struct.data

        if type(denormalized_struct) in PRIMITIVE_TYPES:
            return [PAYLOAD_PRIMITIVE, denormalized_struct]

        if type(denormalized_struct) == types.DictType\
          or isinstance(denormalized_struct,dict):
            normalized_struct = {}
            is_simple = True
            for k, v in denormalized_struct.iteritems():
                if type(k) not in PRIMITIVE_TYPES:
                    raise InvalidDictKeyType(k)
                nv = self.struct_normalize(v)
                normalized_struct[k] = nv
                if nv[TYPE] != PAYLOAD_PRIMITIVE:
                    is_simple =False
            if is_simple:
                for k, v in normalized_struct.iteritems():
                    normalized_struct[k] = v[PAYLOAD]
                return [PAYLOAD_PRIMITIVE,normalized_struct]
            return [PAYLOAD_CONTAINS_DISTRIBUTED,normalized_struct]

        if type(denormalized_struct) in(types.ListType,types.TupleType)\
          or isinstance(denormalized_struct,list):

            normalized_struct = []
            is_simple = True
            for v in denormalized_struct:
                nv = self.struct_normalize(v)
                normalized_struct.append(nv)
                if nv[TYPE] != PAYLOAD_PRIMITIVE:
                    is_simple =False
            if is_simple:
                normalized_struct = [
                    v[PAYLOAD] for v in normalized_struct
                ]
                return [PAYLOAD_PRIMITIVE,normalized_struct]
            return [PAYLOAD_CONTAINS_DISTRIBUTED,normalized_struct]

        if isinstance(denormalized_struct,types.ObjectType):
            obj_id = self.object_put(denormalized_struct)
            return [
                PAYLOAD_DISTRIBUTED_OBJECT,
                obj_id
            ]

        raise InvalidStruct("Cannot Encode this Struct")

    def struct_denormalize(self,normalized_struct):
        payload_type = normalized_struct[TYPE]
        payload = normalized_struct[PAYLOAD]

        if payload_type < 0:
            raise Exception(payload)

        if payload_type == PAYLOAD_PRIMITIVE:
            return payload

        if payload_type == PAYLOAD_DISTRIBUTED_OBJECT:
            return self.object_get(payload)

        if payload_type != PAYLOAD_CONTAINS_DISTRIBUTED:
            # FIXME: Give a better error message?
            raise InvalidStruct('Not sure what to do')

        if isinstance(payload,types.ListType):
            data = [
                self.struct_denormalize(v) \
                    for v in payload
            ]
            return data

        if isinstance(payload,types.DictType):
            data = {}
            for k, v in payload.iteritems():
                data[k] = self.struct_denormalize(v)
            return data

class HandlerSerializer(Serializer):
    """ This class is used by the server to encode data into
        a useful format.

        By default, this puts all the new objects into
        the "connection" object registry if the default
        registry is not chosen.
    """
    _context = None
    _registry = None

    def __init__(self,context,registry=None):
        self.context(context)
        if not registry:
            registry = context.conn()
        self.registry(registry)

    def context(self,context=None):
        if context is not None:
            self._context = weakref.ref(context)
        return self._context()

    def registry(self,registry=None):
        if registry is not None:
            self._registry = weakref.ref(registry)
        return self._registry()

    def object_put(self,obj):
        """ Replace the object with a lookup reference
        """
        context = self.context()

        # Is it already registered? If so, just return the reference
        reg_obj_id = context.object_registered(obj)
        if reg_obj_id: return reg_obj_id

        # If it hasn't been already registered, let's route it into
        # the proper wrapper then register it
        router = context.router()
        wrapped = router.map(obj,context)

        return self.registry().put(wrapped)

    def object_get(self,reg_obj_id):
        """ Fetch the object based upon the lookup reference
        """
        return self.context().object_get(reg_obj_id)

    def object_delete(self,reg_obj_id):
        """ Remove the object from the registry (allowing
            the garbage collector to reap it)
        """
        return self.context().object_delete(reg_obj_id)


class SerializerClient(object):
    pass

