#!/usr/bin/python

import walky.controller
import walky.service
import walky.port

class SendOK(Exception):
    pass

class TestClass(object):
    def a(self):
        return 'yar'
    b = 'foo'
    _c = None

class TestPort(walky.port.Port):
    def _receiveline(self):
        return "GOT A MESSAGE!\r\n"

    def _sendline(self,line):
        raise SendOK(line)
        return

c = walky.controller.Controller()

# Create/Register the service
tc = TestClass()
s = c.service_new( walky.service.Service,
          objects_global={ 'tc': tc }
      )

# Create/Register the port
p = c.port_new(TestPort)

print c._services
print c._ports

# Connect the port and service up
c.connect(p.id,s.id)
print p.service().id, s.id
print s.port().id, p.id

# Send a message to the service via the port
try:
    p.on_receiveline('["?","tc.b","123"]')
except SendOK as ok:
    print ok

# Connect the service to a new port
np = c.port_new(TestPort)
c.connect(np.id,s.id)

# Ensure that the old port is no longer connected
print p.service() is None

# And can we send data to the service via the new port?
try:
    np.on_receiveline('["?","tc.b","123"]')
except SendOK as ok:
    print ok


