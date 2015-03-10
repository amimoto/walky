import weakref
import logging
import datetime

_logger = logging.getLogger(__name__)

class Port(object):

    _context = None
    _active = True
    _active_timeout = False

    def __init__(self,id,context,*args,**kwargs):
        self.id = id # The ID should be a cryptographically secure identifier.
        self.context(context)
        context.port(self)
        self.init(*args,**kwargs)

    def reset(self):
        pass

    def init(self,*args,**kwargs):
        """ Just to make subclassing easier
        """
        pass

    def context(self,context=None):
        """ Returns the current associated context object
            If a context is provided, load the context into 
            the object
        """
        if context is not None:
            self._context = weakref.ref(context)
        return self._context()

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
        self.context().dispatch().on_readline(line)

    def sendline(self,line):
        """ Should send a message over the wire. This function
            will also append the newline for the user.
            After the message has been put on the wire (or perhaps
            the buffer), ensure on_sendline is invoked.
            
            FIXME: This requires some sort of locking
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



