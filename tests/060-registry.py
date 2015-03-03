import unittest

from walky.utils import *
from walky.objects import *
from walky.context import *
from walky.registry import *

from _common import *

class Test(unittest.TestCase):

    def test_registry(self):
        reg = Registry()
        context = Context()
        tc = TestClass()
        wrapped = ObjectWrapper(tc)
        obj_id = context.conn(reg).put(wrapped)

if __name__ == '__main__':
    unittest.main()

