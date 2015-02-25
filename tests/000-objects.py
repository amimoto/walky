#!/usr/bin/python

import walky.objects.common as common

class TestClass(object):
    def a(self):
        return 'yar'
    b = 'foo'
    _c = None

tc = TestClass()
ow = common.ObjectWrapper(tc,allow=['.*'])
print ow.b
print ow.a
print ow.a()
print dir(ow)
ow._c


