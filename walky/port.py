import weakref
import logging
import datetime

_logger = logging.getLogger(__name__)

class Port(object):

    _service = None
    _controller = None
    _active = True
    _active_timeout = False

    def __init__(self,id,controller=None,service=None,*args,**kwargs):
        if controller: self.controller(controller)
        if service: self.service(service)

        # The ID should be a cryptographically secure identifier.
        self.id = id

        self.init(*args,**kwargs)

    def init(self,*args,**kwargs):
        """ Just to make subclassing easier
        """
        pass

    def active(self,active=None,active_timeout=None):
        """ Getter/Setter to describe the current state. The state is
            used by the automatic culling mechanism
        """
        if active is not None:
            self._active = active
        if active_timeout is not None:
            self._active_timeout = active_timeout
        if not self._active and self._active_timeout:
           if self._active_timeout > datetime.datetime.now():
              return True
        return self._active

    def service(self,service=False):
        """ Resolves the weakref to the service.
            If an argument is supplied, it is assumed to be 
            a service. Sets and returns the new service object.
        """
        if service is not False:
            self._service = service and weakref.ref(service)
        return self._service and self._service()

    def controller(self,controller=False):
        """ Resolves the weakref to the controller.
            If an argument is supplied, it is assumed to be 
            a controller. Sets and returns the new controller object.
        """
        if controller is not False:
            self._controller = controller and weakref.ref(controller)
        return self._controller and self._controller()

    def receiveline(self):
        """ Override to receive a line over the wire. The end
            result should be to invoke on_receiveline.
        """ 
        line = self._receiveline().decode("utf8").strip()
        self.on_receiveline(line)
        return line

    def _receiveline(self):
        """ This may be easier to override than the actual
            receiveline function. 
        """
        return ""

    def on_receiveline(self,line):
        """ Invoked when a string is received.
        """
        response_line = self.service().json_request(line)
        self.sendline(response_line)
        return line

    def sendline(self,line):
        """ Should send a message over the wire. This function
            will also append the newline for the user.
            After the message has been put on the wire (or perhaps
            the buffer), ensure on_sendline is invoked.
        """ 
        line += "\r\n"
        self._sendline(line.encode('utf8'))
        self.on_sendline(line)

    def _sendline(self,line):
        """ This might be easier to override than handling the actual
            sendline function
        """
        pass

    def on_sendline(self,line):
        """ After the line has been sent, this event should be fired
        """
        pass



