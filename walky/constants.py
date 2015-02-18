import types
import httplib

REQ_OBJID = 0
REQ_METHOD = 1
REQ_ARGS = 2
REQ_KWARGS = 3
REQ_MESSAGE_ID = -1

TYPE = 0
PAYLOAD = 1

PAYLOAD_ERROR = -1

PAYLOAD_PRIMITIVE = 0
PAYLOAD_CONTAINS_DISTRIBUTED = 1
PAYLOAD_DISTRIBUTED_OBJECT = 2
PAYLOAD_OBJECT_DELETED = 8
PAYLOAD_ATTRIBUTE_METHOD = 9

PAYLOAD_EVENT = 11
PAYLOAD_SYSTEM = 12

PRIMITIVE_TYPES = (
              types.StringType,
              types.UnicodeType,
              types.IntType,
              types.FloatType,
              types.LongType,
              types.NoneType,
              types.BooleanType
            )

class JSONDOException(Exception): 
      error_code = httplib.INTERNAL_SERVER_ERROR

class InvalidObjectID(JSONDOException):
      error_code = httplib.INTERNAL_SERVER_ERROR

class InvalidObject(JSONDOException):
      error_code = httplib.INTERNAL_SERVER_ERROR

class InvalidObjectMethod(JSONDOException):
      error_code = httplib.METHOD_NOT_ALLOWED

class InvalidStruct(JSONDOException):
      error_code = httplib.BAD_REQUEST

class InvalidDictKeyType(JSONDOException):
      error_code = httplib.UNSUPPORTED_MEDIA_TYPE

class Forbidden(JSONDOException):
      error_code = httplib.FORBIDDEN


