import unittest

from walky.messenger import *

from _common import *

class Test(unittest.TestCase):

    def test_messenger(self):
        msg = Messenger()

        q = msg.subscribe_all()
        q2 = msg.subscribe_message_id(22)
        q3 = msg.subscribe_message_id(123)

        msg.put('msg',123)

        (data,msg_id) = q.get()

        self.assertIsInstance(q,MessengerSubscriber)
        self.assertEqual(data,'msg')
        self.assertEqual(msg_id,123)

        self.assertTrue(q2.empty())
        self.assertFalse(q3.empty())

        msg.put('msg2',22)
        self.assertFalse(q2.empty())
        (data2,msg_id2) = q2.get()

        self.assertEqual(data2,'msg2')
        self.assertEqual(msg_id2,22)

        self.assertFalse(q3.empty())
        q3.flush()
        self.assertTrue(q3.empty())

        msg.put('msg3',123)
        self.assertFalse(q3.empty())
        data3 = q3.get_single_message()
        self.assertEqual(data3,'msg3')


if __name__ == '__main__':
    unittest.main()

