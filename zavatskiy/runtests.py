import unittest
from tests.test_client01 import TestClient01

suite = unittest.TestSuite()
suite.addTest(TestClient01('test_connect'))
suite.addTest(TestClient01('test_ping'))
suite.addTest(TestClient01('test_pingd'))
suite.addTest(TestClient01('test_quit'))
suite.addTest(TestClient01('test_finish'))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite)
