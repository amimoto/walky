import weakref
import datetime

from walky.worker import *
from walky.registry import *

class ConnectionWorkerRequest(WorkerRequest):

    _connection = None
    _request = None
    message_id = None

    def __init__(self,start_time,connection,request,message_id):
        self.start_time = start_time
        self.connection(connection)
        self.request(request)
        self.message_id = message_id

    def execute(self):
        """ Execute the request
        """
        request = self.request()
        connection = self.connection()
        try:
            result = connection.object_exec(
                request.reg_obj_id,
                request.method,
                *request.args,
                **request.kwargs
            )
            result_line = connection.engine().serializer.dumps(
                              result,connection,self.message_id)
            connection.port().sendline(result_line)
        except Exception as ex:
            result_line = connection.engine().serializer.dumps(
                                            SystemError(str(ex)),
                                            connection,
                                            self.message_id
                                        )
            connection.port().sendline(result_line)

class Connection(object):
    _engine = None

    _sys = None
    _sess = None
    _conn = None
    _user = None
    _port = None
    _queue = None
    _message_id_last = None
    _messenger = None
    id = None

    ##################################################
    # Connection management
    ##################################################

    def __init__(self,connection_id,**kwargs):
        self.reset()
        self.id = connection_id
        for k,v in kwargs.iteritems():
            getattr(self,k)(v)
        self.init(**kwargs)

    def init(self,**kwargs):
        pass

    def reset(self):
        self._message_id_last = 0

    def port(self,port=None):
        """ Magic function that loads the port and updates the port to
            redirect requests back to us.
        """
        if port:
            self._port = port
            port.connection(self)
        return self._port

    def engine(self,engine=None):
        if engine:
            self._engine = weakref.ref(engine)
        return self._engine and self._engine()

    def registries(self,include_global=True):
        """ Returns a list of all registries that we should scan
        """
        reg_list = [self.sess(),self.conn()]
        if include_global:
            reg_list.insert(0,self.sys())
        return filter(None,reg_list)

    def message_id_next(self):
        self._message_id_last += 1
        return self._message_id_last

    def on_readline(self,line):
        """ Do an action when we receive an input
        """
        engine = self.engine()
        try:
            start = datetime.datetime.now()

            ( packet, message_id ) = engine.serializer.loads(line,self)
            self.messenger().put(packet,message_id)

            # In the case of an execution request, we send the job to
            # the execution pool for handling: We don't want to lock up
            # the processing of incoming messages.
            if isinstance(packet,Request):
                exec_request = ConnectionWorkerRequest(start,self,packet,message_id)
                engine.crew.put(exec_request)
        except Exception as ex:
            result_line = self.engine().serializer.dumps(
                                            SystemError(str(ex)),
                                            self,
                                            0
                                        )
            self.port().sendline(result_line)

    def sendline(self,line):
        """ Sends another packet to the remote
        """
        self.port().sendline(line)

    def _get_set_attribute(self,k,v=None):
        if not v is None:
            setattr(self,k,v)
        return getattr(self,k)

    def __getattr__(self,k):
        attr_name = "_" + k
        object.__getattribute__(self,attr_name)
        return lambda a=None: self._get_set_attribute(attr_name,a)


    ##################################################
    # Object Server Functions
    # These functions assume that the object being referenced
    # by reg_obj_id is LOCAL
    ##################################################

    def object_put(self,obj,reg_obj_id=None,registry=None):
        """ Attempt to store an object to a registry
            If no registry is chosen, the default registry is
            the connection level registry
        """
        # Is it already registered (and under the alias if requested)? 
        # If so, just return the reference
        reg_obj_id_old = self.object_registered(obj)
        if reg_obj_id_old and reg_obj_id_old == reg_obj_id: 
            return reg_obj_id

        # Setup the default registry if required
        if not registry: registry = self.conn()

        # If it hasn't been already registered, let's route it into
        # the proper wrapper then register it
        router = self.engine().router
        wrapped = router.map(obj,self)

        reg_obj_id = registry.put(wrapped,reg_obj_id)
        return reg_obj_id

    def object_get(self,reg_obj_id):
        """ Attempt to retreive the object via search through the 
            object registry.
        """
        for reg in self.registries():
            obj = reg.get(reg_obj_id)
            if obj: return obj
        return None

    def object_exec(self,reg_obj_id,method,*args,**kwargs):
        """ Execute an object's method
        """
        obj = self.object_get(reg_obj_id)
        result = getattr(obj,method)(*args,**kwargs)
        return result

    def object_delete(self,reg_obj_id,include_global=False):
        """ Removes an object from the registry. Note that
            the system will not comply with the request to remove
            an object from the global registry unless include_global
            is set to true
        """
        for reg in self.registries(include_global):
            reg.delete(reg_obj_id)

    def object_registered(self,obj):
        """ This will scan the registries to find out if the 
            object has already been registered. 
            If already registered, returns the object_id. 
            If not, returns None
        """
        reg_obj_id = reg_object_id(obj)
        for reg in self.registries():
            if reg.get(reg_obj_id): 
                return reg_obj_id
        return None

    ##################################################
    # Object Client Functions
    # These functions assume that the object being referenced
    # by reg_obj_id is REMOTE
    ##################################################

    def object_get_remote(self,reg_obj_id,object_class=ObjectStub):
        return object_class(self,reg_obj_id)

    def object_exec_request(self,reg_obj_id,method,*args,**kwargs):
        """ Dispatch a method execution request, then await
            a response.
        """
        req = Request(reg_obj_id,method,*args,**kwargs)
        message_id = self.message_id_next()
        line = self.engine().serializer.dumps(req,self,message_id)
        sub = self.messenger().subscribe_message_id(message_id)
        self.sendline(line)
        print "WAITING FOR:", message_id
        msg = sub.get_single_message()
        print "GOT:", message_id
        if isinstance(msg,Exception):
            raise msg
        return msg

    def object_exec_request_nowait(self,reg_obj_id,method,*args,**kwargs):
        """ Dispatch a method execution request, then await
            a response.
        """
        req = Request(reg_obj_id,method,*args,**kwargs)
        message_id = self.message_id_next()
        line = self.engine().serializer.dumps(req,self,message_id)
        sub = self.messenger().subscribe_message_id(message_id)
        self.sendline(line)

    def object_attr_request(self,reg_obj_id,attribute):
        """ Send an attribute query request to the object reflection system
        """
        return self.object_exec_request(
                    SYS_INTERROGATION_OBJ_ID,
                    SYS_INTERROGATION_ATTR_METHOD,
                    reg_obj_id,
                    attribute
                )

    def object_dir_request(self,reg_obj_id):
        """ Send a query that fetches all attributes from an obj to the object 
            reflection system
        """
        return self.object_exec_request(
                    SYS_INTERROGATION_OBJ_ID,
                    SYS_INTERROGATION_DIR_METHOD,
                    reg_obj_id
                )

    def object_attr_set_request(self,reg_obj_id,attribute,value):
        """ Send a query that fetches all attributes from an obj to the object 
            reflection system
        """
        return self.object_exec_request(
                    SYS_INTERROGATION_OBJ_ID,
                    SYS_INTERROGATION_SET_METHOD,
                    reg_obj_id,
                    attribute,
                    value
                )

    def object_del_request(self,reg_obj_id):
        """ Send a query that deletes an obj from the registries
        """
        return self.object_exec_request_nowait(
                    SYS_INTERROGATION_OBJ_ID,
                    SYS_INTERROGATION_DEL_METHOD,
                    reg_obj_id
                )




