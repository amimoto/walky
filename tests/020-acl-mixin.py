import unittest

from walky.constants import *
from walky.acl import *
from walky.user import *

from _common import *

class TestACLMixin(ACLMixin):
    _acls_ = [
        [
            'testgroup',
            ALLOW_ALL,
            DENY_UNDERSCORED,
            MODE_READ|MODE_WRITE|MODE_EXECUTE, # mode
        ],
    ]


class TestACLMixin2(ACLMixin):
    _acls_ = []

class Test(unittest.TestCase):

    def test_acl_mixin(self):
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

        tam = TestACLMixin()
        self.assertIsInstance(tam,TestACLMixin)
        self.assertTrue(tam._acl_allows(user,'a',MODE_READ))
        self.assertFalse(tam._acl_allows(user,'_a',MODE_READ))

        tam = TestACLMixin2()
        self.assertTrue(tam)
        self.assertFalse(tam._acl_allows(user,'a',MODE_READ))

        
        

if __name__ == '__main__':
    unittest.main()

