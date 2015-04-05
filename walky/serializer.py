import json
import pytz
import pytz.reference
import tzlocal

from constants import *
from walky.registry import *
from walky.objects import *
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

class ObjectMethod(SystemMessage):
    payload_type = PAYLOAD_ATTRIBUTE_METHOD 

    def __init__(self,reg_obj_id,method):
        self.data = [reg_obj_id,method]

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

    def dumps(self,denormalized_struct,connection,message_id):
        """ Converts the data provided into a serialized format
            ready for transport
        """
        enveloped_struct = self.envelope_wrap(
                                    denormalized_struct,
                                    connection,
                                    message_id
                                )
        return self.protocol.dumps(enveloped_struct)

    def envelope_wrap(self,denormalized_struct,connection,message_id):
        if isinstance(denormalized_struct,NormalizedData):
            enveloped_struct = denormalized_struct.struct_normalize(
                                                              self,
                                                              connection
                                                          )
            enveloped_struct.append(message_id)
            return enveloped_struct

        normalized_struct = self.struct_normalize(
                                        denormalized_struct,
                                        connection
                                    )
        enveloped_struct = [PAYLOAD_DATA,normalized_struct,message_id]
        return enveloped_struct
        

    def loads(self,s,connection):
        """ Converts the received serialized Walky object into a 
            denormalized structure and the associated message id.
        """
        enveloped_struct = self.protocol.loads(s)
        message_id = enveloped_struct[-1]
        denormalized_struct = self.envelop_unwrap(enveloped_struct,connection)
        return denormalized_struct, message_id

    def object_put(self,obj,connection):
        """ Replace the object with a lookup reference
            Use the "conn" registry
        """
        return connection.object_put(obj,registry=connection.conn())

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

            This recurisvely traverses a structure to ensure that
            all elements match the required formatting.
        """

        denormalized_type = type(denormalized_struct)

        # Strings are primitives but we need to deal with them
        # a bit carefully to escape the "!" at the begining of the
        # string.
        if denormalized_type in STRING_TYPES:
            if denormalized_struct and denormalized_struct[0] == u'!':
                return u'!'+denormalized_struct 
            return denormalized_struct 

        # If it's not a string and it's a simple type, we can just
        # send the data over verbatum. Yay!
        if denormalized_type in PRIMITIVE_TYPES:
            return denormalized_struct

        # If the data is a datetime.date, we will convert it to a string
        if denormalized_type in DATE_TYPES:
            return u"!d" + denormalized_struct.isoformat()

        # If the data is a datetime.datetime, we will convert it to a string
        # with a caveat that if it's a naive datetime, the system will attach
        # the current timezone to the stamp. It's really better to explicitly
        # use a datetime with a tzinfo
        if denormalized_type in DATE_TYPES:
            if not denormalized_type.tzinfo:
                return u"!D" + tzlocal.get_localzone()\
                                  .localize(denormalized_struct)\
                                  .isoformat()
            return u"!D" + denormalized_struct.isoformat()

        # Descend into a dict
        if denormalized_type == types.DictType\
          or isinstance(denormalized_struct,dict):
            normalized_struct = {}
            is_simple = True
            for k, v in denormalized_struct.iteritems():
                # We don't allow for complex types in the keys of
                # dicts (other language support)
                if type(k) not in PRIMITIVE_TYPES:
                    raise InvalidDictKeyType(k)

                # Descend into the dict!
                normalized_struct[k] = self.struct_normalize(v,connection)
            return normalized_struct

        # Descend into a list
        if denormalized_type in(types.ListType,types.TupleType)\
          or isinstance(denormalized_struct,list):
            normalized_struct = []
            is_simple = True
            for v in denormalized_struct:
                nv = self.struct_normalize(v,connection)
                normalized_struct.append(nv)
            return normalized_struct

        # If this is an object, need to encode it
        if isinstance(denormalized_struct,types.ObjectType):
            reg_obj_id = self.object_put(denormalized_struct,connection)
            return u"!O"+reg_obj_id

        raise InvalidStruct("Cannot Encode this Struct")

    def envelop_unwrap(self,enveloped_struct,connection):
        payload_type = enveloped_struct[TYPE]
        payload = enveloped_struct[PAYLOAD]

        if payload_type == PAYLOAD_METHOD_EXECUTE:
            reg_obj_id = enveloped_struct[REQUEST_OBJECT]
            method = enveloped_struct[REQUEST_METHOD]
            args = []; kwargs = {}
            if len(enveloped_struct)>(REQUEST_ARGS+1):
                args = self.struct_denormalize(enveloped_struct[REQUEST_ARGS],connection)
            if len(enveloped_struct)>(REQUEST_KWARGS+1):
                kwargs = self.struct_denormalize(enveloped_struct[REQUEST_KWARGS],connection)
            return Request(reg_obj_id,method,*args,**kwargs)

        if payload_type == PAYLOAD_EVENT:
            return SystemEvent(self.struct_denormalize(payload,connection))

        if payload_type == PAYLOAD_SYSTEM:
            return SystemMessage(self.struct_denormalize(payload,connection))

        if payload_type == PAYLOAD_DATA:
            return self.struct_denormalize(payload,connection)

        if payload_type == PAYLOAD_ATTRIBUTE_METHOD:
            def object_function(*args,**kwargs):
                params = self.struct_denormalize(payload,connection)
                return connection.object_exec_request(
                            params[0],
                            params[1],
                            *args,
                            **kwargs
                        )                        
            return object_function

        # System messages
        # FIXME: Need to handle all types of error messages
        if payload_type <= PAYLOAD_ERROR:
            return Exception(self.struct_denormalize(payload,connection))

        raise InvalidStruct("Unknown Payload Type '{}'".format(payload_type))

    def struct_denormalize(self,normalized_struct,connection):
        normalized_type = type(normalized_struct)

        if normalized_type in STRING_TYPES:
            if not normalized_struct: return normalized_struct
            if normalized_struct[0] != '!': return normalized_struct
            if len(normalized_struct) < 2:
                raise InvalidStruct("Encoded data missing key!")

            encode_type = normalized_struct[1]

            # Denormalize String escape
            if encode_type == '!':
                return normalized_struct[1:]

            normalized_data = normalized_struct[2:]

            # Denormalize Date
            if encode_type == 'd':
                return datetime.datetime.strptime(normalized_data,'%Y-%m-%d').date()

            # Denormalize Datetime
            if encode_type == 'D':
                return dateutil.parser.parse(normalized_data)

            # Denormalize Object Reference
            if encode_type == 'O':
                # FIXME: Handle metadata
                return ObjectStub(connection,normalized_data)

            raise InvalidStruct("Unknown encoding for '{}'!".format(normalized_struct))

        if normalized_type in PRIMITIVE_TYPES:
            return normalized_struct

        if isinstance(normalized_struct,types.ListType):
            data = [
                self.struct_denormalize(v,connection) \
                    for v in normalized_struct
            ]
            return data

        if isinstance(normalized_struct,types.DictType):
            data = {}
            for k, v in normalized_struct.iteritems():
                data[k] = self.struct_denormalize(v,connection)
            return data

        """
        # Now, to handle the denormalization of most of the strutures...
        if payload_type == PAYLOAD_DISTRIBUTED_OBJECT:
            # FIXME: need th reg_obj_id to identify local vs remote
            try:
                return self.object_get(payload,connection) \
                        or ObjectStub(connection,payload)
            except:
                return ObjectStub(connection,payload)

        # Is this a function to an object?
        if payload_type == PAYLOAD_ATTRIBUTE_METHOD:
            def object_function(*args,**kwargs):
                params = self.struct_denormalize(payload,connection)
                return connection.object_exec_request(
                            params[0],
                            params[1],
                            *args,
                            **kwargs
                        )                        
            return object_function

        if payload_type != PAYLOAD_CONTAINS_DISTRIBUTED:
            # FIXME: Give a better error message?
            raise InvalidStruct('Not sure what to do')

        # FIXME: Give a better error message?
        raise InvalidStruct('Not sure what to do')
        """
