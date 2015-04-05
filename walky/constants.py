import types
import httplib
import datetime

##############################
# Protocol
##############################

WALKY_SOCKET_PORT = 8663
WALKY_WEBSOCK_PORT = 8662

REQ_OBJID = 0
REQ_METHOD = 1
REQ_ARGS = 2
REQ_KWARGS = 3
REQ_MESSAGE_ID = -1

TYPE = 0
PAYLOAD = 1

PAYLOAD_ERROR = -1

PAYLOAD_METHOD_EXECUTE = 0
PAYLOAD_DATA = 1
PAYLOAD_OBJECT_DELETED = 8
PAYLOAD_ATTRIBUTE_METHOD = 9

PAYLOAD_EVENT = 11
PAYLOAD_SYSTEM = 12

REQUEST_OBJECT = 1
REQUEST_METHOD = 2
REQUEST_ARGS   = 3
REQUEST_KWARGS = 4

SYS_INTERROGATION_OBJ_ID = '?'
SYS_INTERROGATION_ATTR_METHOD = '?'
SYS_INTERROGATION_SET_METHOD = '='
SYS_INTERROGATION_DIR_METHOD = 'dir'
SYS_INTERROGATION_DEL_METHOD = 'del'

##############################
# Mapper
##############################
TARGET_GROUP = 0
SOURCE_CLASS = 1
MAPPED_CLASS = 2

##############################
# Normalization
##############################
STRING_TYPES = (
              types.StringType,
              types.UnicodeType,
            )
DATETIME_TYPES = (
                datetime.datetime,
            )
DATE_TYPES = (
                datetime.date,
            )
PRIMITIVE_TYPES = (
              types.StringType,
              types.UnicodeType,
              types.IntType,
              types.FloatType,
              types.LongType,
              types.NoneType,
              types.BooleanType
            )

##############################
# ACL 
##############################
ALLOW_ALL = ['.*']
DENY_ALL = ['.*']
DENY_NONE = []
DENY_UNDERSCORED = ['_.*']

MODE_READ = 0x04
MODE_WRITE = 0x02
MODE_EXECUTE = 0x01

##############################
# Exceptions
##############################
class WalkyException(Exception): 
      error_code = httplib.INTERNAL_SERVER_ERROR

class InvalidServiceID(WalkyException):
      error_code = httplib.INTERNAL_SERVER_ERROR

class InvalidPortID(WalkyException):
      error_code = httplib.INTERNAL_SERVER_ERROR

class InvalidObjectID(WalkyException):
      error_code = httplib.INTERNAL_SERVER_ERROR

class InvalidObject(WalkyException):
      error_code = httplib.INTERNAL_SERVER_ERROR

class InvalidObjectMethod(WalkyException):
      error_code = httplib.METHOD_NOT_ALLOWED

class InvalidRequest(WalkyException):
      error_code = httplib.BAD_REQUEST

class InvalidStruct(WalkyException):
      error_code = httplib.BAD_REQUEST

class InvalidDictKeyType(WalkyException):
      error_code = httplib.UNSUPPORTED_MEDIA_TYPE

class Forbidden(WalkyException):
      error_code = httplib.FORBIDDEN


