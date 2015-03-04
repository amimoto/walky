import unittest

from walky.constants import *
from walky.utils import *
from walky.objects.router import *
from walky.objects import *
from walky.context import *
from walky.registry import *

from _common import *

class Test(unittest.TestCase):

    def test_router(self):
        context = Context()
        router = Router(context)
        self.assertIsInstance(router,Router)
        router.mapper(TestClass, ObjectWrapper)
        tc = TestClass()
        reg = Registry()
        wrapped = router.map(tc,context)
        self.assertIsInstance(wrapped,ObjectWrapper)
        obj_id = context.conn(reg).put(wrapped)

if __name__ == '__main__':
    unittest.main()

