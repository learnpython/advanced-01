# coding=utf-8

import unittest

from work.utils import prepare_data_for_sending, parse_recieved_bytes


class UtilsTestCase(unittest.TestCase):

    def test_prepare_data_for_sending(self):
        self.assertEqual(
            b'\x00\x05HELLO', prepare_data_for_sending("HELLO")
        )
        self.assertEqual(
            b'\x00\x0eHELLO WORLD!!!',
            prepare_data_for_sending("HELLO WORLD!!!")
        )

    def test_parse_recieved_bytes(self):
        self.assertEqual(
            ('ping', None),
            parse_recieved_bytes(b'ping')
        )
        self.assertEqual(
            ('pingd', 'HELLO'),
            parse_recieved_bytes(b'pingd HELLO')
        )
