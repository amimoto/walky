import time
import unittest

from walky.objects import *
from walky.client import *

class TestClient(Client):
    port_class = TestPort

    def sendline(self,line):
        pass

class Test(unittest.TestCase):
    def test_client_socket(self):

        # Setup a dummy server
        client = TestClient()
        client.connect()
        self.assertIsInstance(client,TestClient)

        obj = client.object_get('?')
        self.assertIsInstance(obj,ObjectStub)

        obj.hello("asdf")

if __name__ == '__main__':
    unittest.main()

