import unittest
from tests.test_client01 import TestClient01

suite01 = unittest.TestSuite()
suite01.addTest(TestClient01('test_connect'))
suite01.addTest(TestClient01('test_ping'))
suite01.addTest(TestClient01('test_pingd'))
suite01.addTest(TestClient01('test_quit'))
suite01.addTest(TestClient01('test_finish'))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite01)
