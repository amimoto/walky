import walky.objects.common as c

class TestClass(object):
    def a(self):
        return 'yar'
    b = 'foo'
    _c = None

tc = TestClass()
ow = c.ObjectWrapper(tc,allow=['.*'])
print ow.b
print ow.a
print ow.a()
print dir(ow)


