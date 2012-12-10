from .protocol import Packet
from .fields import Cmd, Str


class cmd:
    CONNECT = 1
    PING = 2
    PINGD = 3
    QUIT = 4
    FINISH = 5
    CONNECTED = 6
    PONG = 7
    PONGD = 8
    ACKQUIT = 9
    ACKFINISH = 10


class Connected(Packet):
    cmd = Cmd(cmd.CONNECTED)
    session = Str(maxsize=256)


class Pong(Packet):
    cmd = Cmd(cmd.PONG)


class PongD(Packet):
    cmd = Cmd(cmd.PONGD)
    data = Str(maxsize=256)


class AckQuit(Packet):
    cmd = Cmd(cmd.ACKQUIT)
    session = Str(maxsize=256)


class AckFinish(Packet):
    cmd = Cmd(cmd.ACKFINISH)


class Connect(Packet):
    cmd = Cmd(cmd.CONNECT)

    def reply(self, session):
        return Connected(session=session).pack()


class Ping(Packet):
    cmd = Cmd(cmd.PING)

    def reply(self):
        return Pong().pack()


class PingD(Packet):
    cmd = Cmd(cmd.PINGD)
    data = Str(maxsize=256)

    def reply(self):
        return PongD(data=self.data).pack()


class Quit(Packet):
    cmd = Cmd(cmd.QUIT)

    def reply(self, session):
        return AckQuit(session=session).pack()


class Finish(Packet):
    cmd = Cmd(cmd.FINISH)

    def reply(self):
        return AckFinish().pack()