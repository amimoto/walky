import unittest

from walky.connection import *

from _common import *


class Test(unittest.TestCase):

    def test_connection(self):
        tc = TestClass()
        s = Connection(
                        id="TESTID",
                        objects_global={ 'tc': tc, }
                    )
        print s.object_get('?')
        print s.object_exec('?','tc.b','123')
        print repr(s.json_request('["?","tc.b","123"]'))
        print s.id

if __name__ == '__main__':
    unittest.main()

