import unittest

from walky.constants import *
from walky.utils import *
from walky.user import *
from walky.objects import *
from walky.router import *
from walky.connection import *
from walky.registry import *

from _common import *

class Test(unittest.TestCase):

    def test_router(self):
        connection = Connection(1)

        # Initial Prep
        groups = ['testgroup','group2']
        attrs = {
            'name': 'Potato',
            'url': 'http://www.potatos.com',
        }
        user = User(
                    groups,
                    attrs
                )
        self.assertIsInstance(user,User)
        connection.user(user)

        # Now start playing with the router

        router = Router()
        self.assertIsInstance(router,Router)

        router.mapper('testgroup', TestClass, ObjectWrapper)

        tc = TestClass()
        reg = Registry()
        wrapped = router.map(tc,connection)
        self.assertIsInstance(wrapped,ObjectWrapper)
        obj_id = connection.conn(reg).put(wrapped)

if __name__ == '__main__':
    unittest.main()

