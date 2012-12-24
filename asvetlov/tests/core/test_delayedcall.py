import unittest
from unittest.mock import Mock

from core.delayedcall import DelayedCall

class TestDelayedCall(unittest.TestCase):
    NOW = 1356192079.2029467
    EVLOOP = Mock()

    def test_ctor(self):
        def f(a, b):
            pass

        dc = DelayedCall(self.EVLOOP, self.NOW, f, (1, 2))
        self.assertEqual(self.EVLOOP, dc.eventloop)
        self.assertEqual(self.NOW, dc.when)
        self.assertEqual(f, dc.callback)
        self.assertEqual((1, 2), dc.args)
        self.assertFalse(dc.cancelled)

    def test_bad_args(self):
        def f(a, b):
            pass

        with self.assertRaises(AssertionError):
            DelayedCall(self.EVLOOP, self.NOW, 1, ())

        with self.assertRaises(TypeError):
            DelayedCall(self.EVLOOP, self.NOW, f, (1, 2, 3))

    def test_skip_args(self):
        def f(a, b):
            pass
        DelayedCall(self.EVLOOP, self.NOW, 1, (), check_args=False)
        DelayedCall(self.EVLOOP, self.NOW, f, (1, 2, 3), check_args=False)

    def test_ordering(self):
        def f():
            pass

        def g():
            pass

        now = self.NOW
        later = now + 1

        dc1 = DelayedCall(self.EVLOOP, now, f, ())
        dc2 = DelayedCall(self.EVLOOP, now, g, ())
        dc3 = DelayedCall(self.EVLOOP, later, f, ())
        dc4 = DelayedCall(self.EVLOOP, later, g, ())

        #compare objects
        self.assertEqual(dc1, dc1)
        self.assertNotEqual(dc1, dc2)
        self.assertNotEqual(dc1, dc3)
        self.assertNotEqual(dc1, dc4)

        self.assertLess(dc1, dc3)
        self.assertLess(dc1, dc4)
        self.assertLess(dc2, dc3)
        self.assertLess(dc2, dc4)

        self.assertLessEqual(dc1, dc1)
        self.assertLessEqual(dc1, dc3)
        self.assertLessEqual(dc1, dc4)

        self.assertGreater(dc3, dc1)
        self.assertGreater(dc3, dc2)
        self.assertGreater(dc4, dc1)
        self.assertGreater(dc4, dc2)

        self.assertGreaterEqual(dc3, dc1)
        self.assertGreaterEqual(dc3, dc2)
        self.assertGreaterEqual(dc3, dc3)
        self.assertGreaterEqual(dc3, dc4)

        # compare time
        self.assertEqual(now, dc1)
        self.assertEqual(now, dc2)
        self.assertNotEqual(now, dc3)
        self.assertNotEqual(now, dc4)

        self.assertLess(now, dc3)
        self.assertLess(now, dc4)

        self.assertLessEqual(now, dc1)
        self.assertLessEqual(now, dc2)
        self.assertLessEqual(now, dc3)
        self.assertLessEqual(now, dc4)
        self.assertLessEqual(later, dc3)
        self.assertLessEqual(later, dc4)

        self.assertGreater(later, dc1)
        self.assertGreater(later, dc2)

        self.assertGreaterEqual(later, dc1)
        self.assertGreaterEqual(later, dc2)
        self.assertGreaterEqual(later, dc3)
        self.assertGreaterEqual(later, dc4)

    def test___call__(self):
        callback = Mock()
        dc = DelayedCall(self.EVLOOP, self.NOW, callback, (1, 2, 3))
        dc()
        callback.assert_called_with(self.EVLOOP, 1, 2, 3)

    def test_cancel(self):
        dc = DelayedCall(self.EVLOOP, self.NOW, lambda:None, ())
        self.assertFalse(dc.cancelled)
        dc.cancel()
        self.assertTrue(dc.cancelled)


if __name__ == '__main__':
    unittest.main()
