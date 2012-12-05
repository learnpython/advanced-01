import unittest
from tests.test_client01 import TestClient01

suite = unittest.TestSuite()
suite.addTest(TestClient01('test_connect'))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite)
