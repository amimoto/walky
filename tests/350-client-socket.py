import time
import unittest

from walky.objects import *
from walky.client import *

class DummyConnection(Connection):
    def sendline(self,line):
        pass

    def object_exec_request(self,reg_obj_id,method,*args,**kwargs):
        return 'RESULT'

class TestClient(Client):
    port_class = TestPort

class Test(unittest.TestCase):
    def test_client_socket(self):
        client = TestClient()
        client.connect(connection_class=DummyConnection)
        self.assertIsInstance(client,TestClient)

        obj = client.object_get('?')
        self.assertIsInstance(obj,ObjectStub)

        try:
            v = obj.hello
            self.assertEqual(v,'RESULT')
            client.close()
        except Exception as ex:
            client.close()
            raise

if __name__ == '__main__':
    unittest.main()

