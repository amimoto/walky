import weakref
import logging
import datetime

_logger = logging.getLogger(__name__)

class Port(object):

    _connection = None
    _active = True
    _active_timeout = False

    def __init__(self,id,*args,**kwargs):
        """ Note: Connection is attached afterwards
            TODO: Better documentation or layout that makes sense.
        """
        self.id = id # The ID should be a cryptographically secure identifier.
        if kwargs.get('connection'):
            self.connection(kwargs['connection'])
            del kwargs['connection']
        self.init(*args,**kwargs)

    def reset(self):
        pass

    def init(self,*args,**kwargs):
        """ Just to make subclassing easier
        """
        pass

    def connection(self,connection=None):
        """ Returns the current associated connection object
            If a connection is provided, load the connection into 
            the object
        """
        if connection is not None:
            self._connection = weakref.ref(connection)
        return self._connection()

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

    def on_receiveline(self,line):
        """ Invoked when a string is received.
        """
        line = line.decode("utf8").strip()
        self.connection().on_readline(line)

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



