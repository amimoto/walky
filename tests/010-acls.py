import unittest

from walky.constants import *
from walky.acl import *
from walky.user import *

class Test(unittest.TestCase):

    def test_single(self):

        groups = ['testgroup','group2']
        attrs = {
            'name': 'Potato',
            'url': 'http://www.potatos.com',
        }
        user = User(
                    groups,
                    attrs
                )
        self.assertTrue(user)

        acl = ACL(
                  'testgroup',
                  ALLOW_ALL,
                  DENY_UNDERSCORED,
                  MODE_READ|MODE_WRITE|MODE_EXECUTE, # mode
              )

        self.assertTrue(acl)

        self.assertTrue(acl._acl_allows(
                              user,
                              'te_st',
                              MODE_EXECUTE,
                              None
                          ))

        self.assertFalse(acl._acl_allows(
                              user,
                              '_test',
                              MODE_EXECUTE,
                              None
                          ))

    def test_multiple(self):


        groups = ['testgroup','group2']
        attrs = {
            'name': 'Potato',
            'url': 'http://www.potatos.com',
        }
        user = User(
                    groups,
                    attrs
                )
        self.assertTrue(user)
        class TestClass(ACLMixin):
            _acls_ = [
              ['testgroup',ALLOW_ALL,DENY_UNDERSCORED,MODE_READ|MODE_WRITE|MODE_EXECUTE],
            ]
        
        tc = TestClass()

        self.assertTrue(tc._acl_allows(
                              user,
                              'te_st',
                              MODE_EXECUTE
                          ))

        self.assertFalse(tc._acl_allows(
                              user,
                              '_test',
                              MODE_EXECUTE
                          ))


if __name__ == '__main__':
    unittest.main()

