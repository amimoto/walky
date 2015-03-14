import time
import unittest

from walky.client import *


class TestClient(Client):
    port_class = TestPort

    def sendline(self,line):
        pass

class Test(unittest.TestCase):
    def test_client_socket(self):

        # Setup a dummy server
        client = TestClient()
        self.assertIsInstance(client,Client)

        obj = client.object_get('@')
        self.assertIsInstance(obj,ClientObject)

if __name__ == '__main__':
    unittest.main()

