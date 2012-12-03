import unittest


class BaseTestCase(unittest.TestCase):    
    
    def setUp(self):
        pass 
   
    def tearDown(self):
        pass

    def test_connect(self):
        self.assertEqual(1, 2)
       