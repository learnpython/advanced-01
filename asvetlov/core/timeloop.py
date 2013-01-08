import contextlib
import heapq
import os
import threading
import time

from core.delayedcall import DelayedCall


class Timeloop:
    def __init__(self, *, check_args=True):
        self._check_args = check_args
        fdin, fdout = os.pipe2(os.O_NONBLOCK|os.O_CLOEXEC)
        self._wakeupfd = os.fdopen(fdin, 'rb')
        self._signalfd = os.fdopen(fdout, 'wb')
        self._soon_lock = threading.RLock()
        self._soon = []
        self._later = []
        self._timer = time.monotonic

    def call_soon(self, cb, *args):
        dc = DelayedCall(self, 0, cb, args, check_args=self._check_args)
        self._soon.append(dc)
        return dc

    def call_later(self, delay, cb, *args):
        if not delay:
            return self.call_soon(cb, *args)
        now = self._timer()
        when = now + delay
        dc = DelayedCall(self, when, cb, args, check_args=self._check_args)
        heapq.heappush(self._later, dc)
        return dc

    def call_soon_threadsafe(self, cb, *args):
        with self._soon_lock:
            ret = self.call_soon(cb, *args)
            self._signal(b'T')
            return ret

    def _signal(self, char):
        sent = 0
        while not sent:
            try:
                sent = self._signalfd.write(char)
            except BlockingIOError:
                pass

    def _process_timers(self):
        delay = 3600
        with self._soon_lock:
            soon = self._soon
            self._soon = []
        q = self._later
        now = self._timer()
        while q:
            dc = q[0]
            if dc.cancelled:
                heapq.heappop(q)
            elif dc.when <= now:
                soon.append(dc)
                heapq.heappop(q)
            else:
                delay = min(delay, dc.when - now)
                break
        for dc in soon:
            dc()
        if self._soon:
            delay = 0
        return delay

    def close(self):
        self._signalfd.close()
        self._wakeupfd.close()
