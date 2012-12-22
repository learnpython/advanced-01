from functools import total_ordering
from inspect import signature
from numbers import Number
from textwrap import dedent


@total_ordering
class DelayedCall:
    def __init__(self, eventloop, when, callback, args, *, check_args=True):
        if check_args:
            assert callable(callback), ('callback should be any callable, '
                                        'got {!r}'.format(callback))
            sig = signature(callback)
            sig.bind(*args)  # may raise TypeError
                             # if args is not compatible with cb
        self.eventloop = eventloop
        self.when = when
        self.callback = callback
        self.args = args
        self.cancelled = False

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.when == other
        if not isinstance(other, DelayedCall):
            return NotImplemented
        return (self.when==other.when and
                self.callback == other.callback and
                self.args == other.args)

    def __lt__(self, other):
        if isinstance(other, Number):
            return self.when < other
        if not isinstance(other, DelayedCall):
            return NotImplemented
        return self.when < other.when

    def __call__(self):
        self.callback(self.eventloop, *self.args)

    def cancel(self):
        self.cancelled = True

    def __repr__(self):
        return dedent("""
                      <DelayedCall:
                                    eventloop={eventloop!r}
                                    when={when}
                                    callback={callback!r}
                                    args={args!r}
                                    cancelled={cancelled}
                      >""".format_map(vars(self)))
