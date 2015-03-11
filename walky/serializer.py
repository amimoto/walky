import json

from constants import *
from walky.registry import *
from utils import *

class NormalizedData(object):
    def __init__(self,data=None):
        self.data = data

    def struct_normalize(self,serializer,connection):
        return self.data

class SystemNormalized(NormalizedData):
    payload_type = PAYLOAD_SYSTEM

class Request(SystemNormalized):
    """ When a object method invocation (PayloadType=0) comes in,
        it's easier to manage it with its own 
    """
    payload_type = PAYLOAD_METHOD_EXECUTE

    def __init__(self,reg_obj_id,method,*args,**kwargs):
        self.reg_obj_id = reg_obj_id
        self.method = method
        self.args = args
        self.kwargs = kwargs
        super(Request,self).__init__()
    
    def struct_normalize(self,serializer,connection):
        data = [
            self.payload_type,
            self.reg_obj_id,
            self.method,
        ]
        if self.args or self.kwargs:
            data.append(serializer.struct_normalize(self.args,connection))
            data.append(serializer.struct_normalize(self.kwargs,connection))
        return data

class SystemMessage(SystemNormalized):
    payload_type = PAYLOAD_SYSTEM

    def struct_normalize(self,serializer,connection):
        data = [
            self.payload_type,
            serializer.struct_normalize(self.data,connection),
        ]
        return data

class SystemEvent(SystemMessage):
    payload_type = PAYLOAD_EVENT

class SystemError(SystemMessage):
    payload_type = PAYLOAD_ERROR

class Serializer(object):
    """ This allows objects and structures to be encoded in JSON format

        Some Lingo:

        A denormalized struct is data that hasn't been converted into
        a format that's not amenable for Walky serialization. In other
        words, the "original" object.

        A normalized struct is a structure that's encoded in a format
        that's ready for Walky serialization (which is really just 
        JSON with certain rules)

        Notes:

        While we use JSON by default, it's quite easy to replace the
        underlying serialization format by updating the protocol
        attribute. Due to the port constraints, however, it's eaiser
        to change the protocol if it's CRLF terminated rather than
        binary. Binary formats such as ASN.1 are possible, but require
        updates to how the port handles chunks (currently readline).

    """

    protocol = json

    def dumps(self,denormalized_struct,message_id,connection):
        """ Converts the data provided into a serialized format
            ready for transport
        """
        normalized_struct = self.struct_normalize(denormalized_struct,connection)
        normalized_struct.append(message_id)
        return self.protocol.dumps(normalized_struct)

    def loads(self,s,connection):
        """ Converts the received serialized Walky object into a 
            denormalized structure and the associated message id.
        """
        normalized_struct = self.protocol.loads(s)
        message_id = normalized_struct[-1]
        denormalized_struct = self.struct_denormalize(normalized_struct,connection)
        return denormalized_struct, message_id

    def object_put(self,obj,connection):
        """ Replace the object with a lookup reference
        """
        # Is it already registered? If so, just return the reference
        reg_obj_id = connection.object_registered(obj)
        if reg_obj_id: return reg_obj_id

        # If it hasn't been already registered, let's route it into
        # the proper wrapper then register it
        router = connection.engine().router
        wrapped = router.map(obj,connection)

        return connection.conn().put(wrapped)

    def object_get(self,reg_obj_id,connection):
        """ Fetch the object based upon the lookup reference
        """
        return connection.object_get(reg_obj_id)

    def object_delete(self,reg_obj_id,connection):
        """ Remove the object from the registry (allowing
            the garbage collector to reap it)
        """
        return connection.object_delete(reg_obj_id)

    def struct_normalize(self,denormalized_struct,connection):
        """ Normalize a structure. Turn it into the structure
            format expected for serialization.
        """

        if isinstance(denormalized_struct,NormalizedData):
            return denormalized_struct.struct_normalize(self,connection)

        if type(denormalized_struct) in PRIMITIVE_TYPES:
            return [PAYLOAD_PRIMITIVE, denormalized_struct]

        if type(denormalized_struct) == types.DictType\
          or isinstance(denormalized_struct,dict):
            normalized_struct = {}
            is_simple = True
            for k, v in denormalized_struct.iteritems():
                if type(k) not in PRIMITIVE_TYPES:
                    raise InvalidDictKeyType(k)
                nv = self.struct_normalize(v,connection)
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
                nv = self.struct_normalize(v,connection)
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
            obj_id = self.object_put(denormalized_struct,connection)
            return [
                PAYLOAD_DISTRIBUTED_OBJECT,
                obj_id
            ]

        raise InvalidStruct("Cannot Encode this Struct")

    def struct_denormalize(self,normalized_struct,connection):
        payload_type = normalized_struct[TYPE]
        payload = normalized_struct[PAYLOAD]

        # The most basic possibility. No additional parsing required:
        if payload_type == PAYLOAD_PRIMITIVE:
            return payload

        # System messages
        if payload_type < 0:
            raise Exception(payload)

        if payload_type == PAYLOAD_METHOD_EXECUTE:
            reg_obj_id = normalized_struct[REQUEST_OBJECT]
            method = normalized_struct[REQUEST_METHOD]
            args = []; kwargs = {}
            if len(normalized_struct)>(REQUEST_ARGS+1):
                args = self.struct_denormalize(normalized_struct[REQUEST_ARGS],connection)
            if len(normalized_struct)>(REQUEST_KWARGS+1):
                kwargs = self.struct_denormalize(normalized_struct[REQUEST_KWARGS],connection)

            return Request(reg_obj_id,method,*args,**kwargs)

        if payload_type == PAYLOAD_EVENT:
            return SystemEvent(self.struct_denormalize(payload,connection))

        if payload_type == PAYLOAD_SYSTEM:
            return SystemMessage(self.struct_denormalize(payload,connection))

        # Now, to handle the denormalization of most of the strutures...
        if payload_type == PAYLOAD_DISTRIBUTED_OBJECT:
            return self.object_get(payload,connection)

        if payload_type != PAYLOAD_CONTAINS_DISTRIBUTED:
            # FIXME: Give a better error message?
            raise InvalidStruct('Not sure what to do')

        if isinstance(payload,types.ListType):
            data = [
                self.struct_denormalize(v,connection) \
                    for v in payload
            ]
            return data

        if isinstance(payload,types.DictType):
            data = {}
            for k, v in payload.iteritems():
                data[k] = self.struct_denormalize(v,connection)
            return data

