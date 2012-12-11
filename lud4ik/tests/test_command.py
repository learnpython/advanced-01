import unittest

from work.protocol import Packet
from work.models import (cmd, Connected, Pong, PongD, AckQuit, AckFinish,
                         Connect, Ping, PingD, Quit, Finish)
from work.fields import Cmd, Str
from work.exceptions import FieldDeclarationError


class CommandTestCase(unittest.TestCase):

    LENGTH = 4

    def test_connect(self):
        packet = Connect()
        self.assertIsInstance(Packet.unpack(packet.pack()[self.LENGTH:]),
                              Connect)

    def test_ping(self):
        packet = Ping()
        self.assertIsInstance(Packet.unpack(packet.pack()[self.LENGTH:]), Ping)

    def test_pingd(self):
        packet = PingD(data='test_data')
        unpacked = Packet.unpack(packet.pack()[self.LENGTH:])
        self.assertEqual(packet.data, unpacked.data)
        self.assertIsInstance(unpacked, PingD)

    def test_quit(self):
        packet = Quit()
        self.assertIsInstance(Packet.unpack(packet.pack()[self.LENGTH:]), Quit)

    def test_finish(self):
        packet = Finish()
        self.assertIsInstance(Packet.unpack(packet.pack()[self.LENGTH:]),
                              Finish)

    def test_connected(self):
        packet = Connected(session='test_session')
        unpacked = Packet.unpack(packet.pack()[self.LENGTH:])
        self.assertEqual(packet.session, unpacked.session)
        self.assertIsInstance(unpacked, Connected)

    def test_pong(self):
        packet = Pong()
        self.assertIsInstance(Packet.unpack(packet.pack()[self.LENGTH:]), Pong)

    def test_pongd(self):
        packet = PongD(data='test_data')
        unpacked = Packet.unpack(packet.pack()[self.LENGTH:])
        self.assertEqual(packet.data, unpacked.data)
        self.assertIsInstance(unpacked, PongD)

    def test_ackquit(self):
        packet = AckQuit(session='test_session')
        unpacked = Packet.unpack(packet.pack()[self.LENGTH:])
        self.assertEqual(packet.session, unpacked.session)
        self.assertIsInstance(unpacked, AckQuit)

    def test_ackfinish(self):
        packet = AckFinish()
        self.assertIsInstance(Packet.unpack(packet.pack()[self.LENGTH:]),
                              AckFinish)

    def test_without_cmd(self):
        with self.assertRaises(FieldDeclarationError):
            class ErrorClass(Packet):
                data = Str(maxsize=256)

    def test_dublicate(self):
        with self.assertRaises(FieldDeclarationError):
            class ErrorClass(Packet):
                cmd = Cmd(cmd.CONNECTED)
                data = Str(maxsize=256)
