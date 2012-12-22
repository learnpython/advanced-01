class Eventloop:
    def __init__(self):
        pass

    def run_once(self, timeout):
        pass

    def run(self):
        pass

    def stop(self):
        pass

    def call_soon(self, cb, *args):
        pass

    def call_later(self, delay, cb, *args):
        pass

    def call_soon_threadsafe(self, cb, *args):
        pass
