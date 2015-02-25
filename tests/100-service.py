#!/usr/bin/python

import walky.service

class TestClass(object):
    def a(self):
        return 'yar'
    b = 'foo'
    _c = None

tc = TestClass()
s = walky.service.Service(
      id="TESTID",
      objects_global={ 'tc': tc, }
      )
print s.object_get('?')
print s.object_exec('?','tc.b','123')
print repr(s.json_request('["?","tc.b","123"]'))
print s.id


