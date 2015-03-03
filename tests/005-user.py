import unittest

from walky.constants import *
from walky.user import *

class Test(unittest.TestCase):

    def test_user(self):
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
        self.assertTrue(user.in_group('group2'))
        self.assertFalse(user.in_group('potato_heaven'))
        self.assertEqual(user.groups(),set(groups))
        self.assertEqual(user.name,'Potato')
        user.name = 'Hot Potato'
        self.assertEqual(user.name,'Hot Potato')

        # Locking should prevent updating of fields
        user.lock()
        with self.assertRaises(Exception) as cm:
            user.name = 'Nuclear Potato'



if __name__ == '__main__':
    unittest.main()

