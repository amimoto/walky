#!/usr/bin/python

import walky.port

class TestPort(walky.port.Port):
    def _receiveline(self):
        return "GOT A MESSAGE!\r\n"

    def on_receiveline(self,line):
        """ Test fixture, do nothing
        """
        pass

    def _sendline(self,line):
        raise Exception(line)
        return

p = TestPort(
      id="TESTID"
      )

print p
print p.receiveline()
print p.sendline("TESTTESTTEST")




