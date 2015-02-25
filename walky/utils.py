import types
from constants import *

def object_method_prevent_rpc(f):
    f._norpc = True
    return f

def is_function(o):
    """ Returns true if provided object is a fuctional type
    """
    return isinstance(o,types.UnboundMethodType) or \
           isinstance(o,types.FunctionType) or \
           isinstance(o,types.BuiltinFunctionType) or \
           isinstance(o,types.BuiltinMethodType)

