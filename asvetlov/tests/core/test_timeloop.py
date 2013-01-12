import collections
import heapq
import unittest

from unittest.mock import Mock


from core.timeloop import Timeloop


class TestTimeLoop(unittest.TestCase):
    def create_timeloop(self, **kwargs):
        tl = Timeloop(**kwargs)
        self.addCleanup(tl.close)
        return tl

    def test_ctor(self):
        tl = self.create_timeloop()
        self.assertTrue(tl._check_args)
        self.assertEqual(collections.deque(), tl._soon)
        self.assertEqual(0, len(tl._later))

    def test_call_soon(self):
        tl = self.create_timeloop()
        cb = Mock()
        dc = tl.call_soon(cb, 'a', 2)
        self.assertEqual(tl, dc.eventloop)
        self.assertEqual(0, dc.when)
        self.assertEqual(cb, dc.callback)
        self.assertEqual(('a', 2), dc.args)
        self.assertEqual(collections.deque([dc]), tl._soon)
        self.assertEqual(0, len(tl._later))
        dc2 = tl.call_soon(cb, 'b', 3)
        self.assertEqual(collections.deque([dc, dc2]), tl._soon)

    def test_call_later_zero_delay(self):
        tl = self.create_timeloop()
        cb = Mock()
        dc = tl.call_later(0, cb, 'a')
        self.assertEqual(tl, dc.eventloop)
        self.assertEqual(0, dc.when)
        self.assertEqual(cb, dc.callback)
        self.assertEqual(('a',), dc.args)
        self.assertEqual(collections.deque([dc]), tl._soon)
        self.assertEqual(0, len(tl._later))

    def test_call_later(self):
        tl = self.create_timeloop()
        cb = Mock()
        tl._timer = Mock(return_value=123)
        dc = tl.call_later(1, cb, 'a')
        self.assertEqual(tl, dc.eventloop)
        self.assertEqual(124, dc.when)
        self.assertEqual(cb, dc.callback)
        self.assertEqual(('a',), dc.args)
        self.assertEqual(collections.deque(), tl._soon)
        self.assertEqual(1, len(tl._later))
        self.assertEqual(dc, tl._later[0])
        dc2 = tl.call_later(0.5, cb, 'b')
        dc3 = tl.call_later(2, cb, 'c')
        order = []
        q = list(tl._later)
        while q:
            order.append(heapq.heappop(q))
        self.assertEqual([dc2, dc, dc3], order)

    def test_call_soon_threadsafe(self):
        tl = self.create_timeloop()
        cb = Mock()
        tl._signalfd.close()
        tl._signalfd = Mock()
        dc = tl.call_soon_threadsafe(cb)
        self.assertEqual(tl, dc.eventloop)
        self.assertEqual(0, dc.when)
        self.assertEqual(cb, dc.callback)
        self.assertEqual((), dc.args)
        self.assertEqual(collections.deque([dc]), tl._soon)
        self.assertEqual([], tl._later)
        tl._signalfd.write.assert_called_with(b'T')

    def test__process_timers(self):
        tl = self.create_timeloop()
        tl._timer = Mock(return_value=100)
        dc1 = tl.call_soon(Mock())
        dc2 = tl.call_soon(Mock())
        dc3 = tl.call_later(1, Mock())
        dc4 = tl.call_later(10, Mock())
        tl._timer = Mock(return_value=105)
        self.assertEqual(5, tl._process_timers())
        dc1.callback.assert_called_with(tl)
        dc2.callback.assert_called_with(tl)
        self.assertEqual(collections.deque([]), tl._soon)
        dc3.callback.assert_called_with(tl)
        self.assertEqual([dc4], tl._later)


if __name__ == '__main__':
    unitest.main()
