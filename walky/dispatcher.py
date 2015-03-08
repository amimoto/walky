import weakref
import Queue

from walky.serializer import *
from walky.worker import *

class DispatcherWorkerRequest(WorkerRequest):

    _context = None
    _request = None
    message_id = None

    def __init__(self,context,request,message_id):
        self.context(context)
        self.request(request)
        self.message_id = message_id

    def execute(self):
        """ Execute the request
        """
        request = self.request()
        context = self.context()
        try:
            result = context.object_exec(
                request.reg_obj_id,
                request.method,
                *request.args,
                **request.kwargs
            )
            result_line = context.serializer().dumps(result,self.message_id)
            context.port().sendline(result_line)
        except Exception as ex:
            result_line = context.serializer().dumps(
                                            SystemError(str(ex)),
                                            self.message_id
                                        )
            context.port().sendline(result_line)

class Dispatcher(object):

    _context = None
    _messenger = None
    _message_id_last = None

    def __init__(self,context):
        self.reset()
        self.context(context)

    def reset(self):
        self._message_id_last = 0

    def message_id_next(self):
        self._message_id_last += 1
        return self._message_id_last

    def context(self,context=None):
        """ Returns the current associated context object
            If a context is provided, load the context into 
            the object
        """
        if context is not None:
            self._context = weakref.ref(context)
        return self._context()

    def port(self,port=None):
        """ Fetches the current port object
        """
        return self.context().port(port)

    def on_readline(self,line):
        """ Do an action when we receive an input
        """
        context = self.context()
        serializer = context.serializer()
        ( packet, message_id ) = serializer.loads(line)
        context.messenger().put(packet,message_id)

        # In the case of an execution request, we send the job to
        # the execution pool for handling: We don't want to lock up
        # the processing of incoming messages.
        if isinstance(packet,Request):
            exec_request = DispatcherWorkerRequest(context,packet,message_id)
            context.crew().put(exec_request)

    def sendline(self,line):
        """ Sends another packet to the remote
        """
        self.port().sendline(line)

    def object_exec(self,reg_obj_id,method,*args,**kwargs):
        """ Dispatch a method execution request, then await
            a response.
        """
        req = Request(reg_obj_id,method,*args,**kwargs)
        context = self.context()
        serializer = context.serializer()
        message_id = self.message_id_next()
        line = serializer.dumps(req,message_id)
        sub = context.messenger().subscribe_message_id(message_id)
        self.sendline(line)
        msg = sub.get_single_message()
        return msg

    def object_getattr(self,reg_obj_id,attr):
        """ Request the attribute from a distributed object
        """

    def object_setattr(self,reg_obj_id,attr,value):
        """ Sets an attribute on a distributed object
        """

