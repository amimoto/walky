import weakref
import Queue
from walky.serializer import SystemMessage

ms_count = 0

def id_next():
    global ms_count
    ms_count += 1
    return ms_count

class MessengerSubscriber(object):
    _messenger = None

    def __init__(self,messenger,filter_op):
        self.messenger(messenger)
        self.queue = Queue.Queue()
        self.filter_op = filter_op
        self.id = id_next()

    def messenger(self,messenger=None):
        if messenger:
            self._messenger = weakref.ref(messenger)
        return self._messenger()

    def flush(self):
        """ Clears all messages from the queue
        """
        while not self.queue.empty():
            self.queue.get()

    def get_single_message(self):
        (msg,msg_id) = self.queue.get(True)
        self.messenger().unsubscribe(self.id)
        return msg

    def __getattr__(self,k):
        return getattr(self.queue,k)

class Messenger(object):
    _subscribers = None

    def __init__(self,*args,**kwargs):
        self.reset()
        self.init(*args,**kwargs)

    def init(self,*args,**kwargs):
        pass

    def reset(self):
        self._subscribers = {}

    def put(self,payload,message_id):
        for subscriber in self._subscribers.values():
            if subscriber.filter_op(payload,message_id):
                subscriber.put((payload,message_id))

    def subscribe_filtered(self,filter_op):
        subscriber = MessengerSubscriber(self,filter_op)
        self._subscribers[subscriber.id] = subscriber
        return subscriber

    def subscribe_all(self):
        return self.subscribe_filtered(
                    lambda *a:True)

    def subscribe_events(self):
        return self.subscribe_filtered(
                    lambda p,m:isinstance(p,SystemMessage))

    def subscribe_message_id(self,message_id):
        return self.subscribe_filtered(
                    lambda p,m:m==message_id)


    def unsubscribe(self,subscriber_id):
        del self._subscribers[subscriber_id]




