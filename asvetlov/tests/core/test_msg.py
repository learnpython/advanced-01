import inspect
import unittest
import uuid

from core.msg import BaseMsg, SignedNumber, String, UUID, ConnectMsg, feeder


class Object:
    pass


class TestSignedNumber(unittest.TestCase):
    def test_type(self):
        sn = SignedNumber(1)
        sn.name = 'x'
        self.assertEqual(127, sn.max_val)
        self.assertEqual(-128, sn.min_val)
        with self.assertRaises(TypeError):
            sn.type_check('123')
        with self.assertRaises(ValueError):
            sn.type_check(200)

    def test_type2(self):
        sn = SignedNumber(4)
        sn.name = 'x'
        self.assertEqual(2147483647, sn.max_val)
        self.assertEqual(-2147483648, sn.min_val)
        with self.assertRaises(ValueError):
            sn.type_check(2147483648)

    def test_load(self):
        sn = SignedNumber(8)
        sn.name = 'x'
        o = Object()
        buf = b'\xff\xff\xff\xff\xff\xff\xff\x85'
        self.assertEqual(8, sn.load(o, buf))
        self.assertEqual(-123, o.x)

    def test_store(self):
        sn = SignedNumber(2)
        sn.name = 'x'
        o = Object()
        o.x = 123
        buf = sn.store(o)
        self.assertEqual(b'\x00\x7b', buf)


class TestString(unittest.TestCase):
    def test_type(self):
        s = String()
        s.name = 'x'
        with self.assertRaises(TypeError):
            s.type_check(123)

    def test_store(self):
        s = String()
        s.name = 'x'
        o = Object()
        o.x = 'abc'
        buf = s.store(o)
        self.assertEqual(b'\x00\x00\x00\x03abc', buf)

    def test_load(self):
        s = String()
        s.name = 'x'
        o = Object()
        buf = b'\x00\x00\x00\x02ef'
        self.assertEqual(6, s.load(o, buf))
        self.assertEqual('ef', o.x)


class TestUUID(unittest.TestCase):
    uuid = uuid.UUID('{12345678-1234-5678-1234-567812345678}')

    def test_type(self):
        s = UUID()
        s.name = 'x'
        with self.assertRaises(TypeError):
            s.type_check(123)

    def test_store(self):
        s = UUID()
        s.name = 'x'
        o = Object()
        o.x = self.uuid
        buf = s.store(o)
        self.assertEqual(self.uuid.bytes, buf)

    def test_load(self):
        s = UUID()
        s.name = 'x'
        o = Object()
        buf = self.uuid.bytes
        self.assertEqual(16, s.load(o, buf))
        self.assertEqual(self.uuid, o.x)


class TestMetaMsg(unittest.TestCase):
    uuid = uuid.UUID('{12345678-1234-5678-1234-567812345678}')

    def test_autokind(self):
        self.assertEqual(1, ConnectMsg.KIND)
        self.assertEqual(ConnectMsg, BaseMsg.KIND_MAP[ConnectMsg.KIND])
        self.assertEqual(1, BaseMsg.KIND_NAMES['ConnectMsg'])

    def test_ctor(self):
        msg = ConnectMsg(self.uuid)
        self.assertEqual(self.uuid, msg.clientid)

    def test_ctor_missing_arg(self):
        with self.assertRaisesRegex(TypeError,
                                    'parameter lacking default value'):
            ConnectMsg()

    def test_ctor_extra_arg(self):
        with self.assertRaisesRegex(TypeError,
                                    'too many positional arguments'):
            ConnectMsg(1, 2)

    def test_ctor_invalid_arg_name(self):
        with self.assertRaisesRegex(TypeError,
                                    'parameter lacking default value'):
            ConnectMsg(uuid=self.uuid)

    def test_ctor_invalid_arg_type(self):
        with self.assertRaisesRegex(TypeError,
                                    'invalid value type'):
            ConnectMsg(1)

    def test_dumps(self):
        msg = ConnectMsg(self.uuid)
        self.assertEqual(b'\x00\x00\x00\x15\x01'+self.uuid.bytes, msg.dumps())

    def test_loads(self):
        msg = ConnectMsg.loads(b'\x00\x00\x00\x15\x01'+self.uuid.bytes)
        self.assertEqual(self.uuid, msg.clientid)

    def test_loads_unknown_kind(self):
        with self.assertRaisesRegex(ValueError, 'Unknown msg kind 254'):
            ConnectMsg.loads(b'\x00\x00\x00\x11\xfe'+self.uuid.bytes)


class TestFeeder(unittest.TestCase):
    uuid = uuid.UUID('{12345678-1234-5678-1234-567812345678}')

    def test_feed(self):
        f = feeder()
        p1 = b'\x00\x00'
        p2 = b'\x00\x15\x01\x12'
        p3 = b'4Vx\x124V'
        p4 = b'x\x124Vx\x12'
        p5 = b'4Vx' + p1
        self.assertIsNone(f.send(None))
        self.assertIsNone(f.send(p1))
        self.assertIsNone(f.send(p2))
        self.assertIsNone(f.send(p3))
        self.assertIsNone(f.send(p4))
        msg = f.send(p5)
        self.assertIsInstance(msg, ConnectMsg)
        self.assertEqual(self.uuid, msg.clientid)
        self.assertIsNone(f.send(p2))
        self.assertIsNone(f.send(p3))
        self.assertIsNone(f.send(p4))
        msg = f.send(p5)
        self.assertEqual(self.uuid, msg.clientid)


if __name__ == '__main__':
    unittest.main()
