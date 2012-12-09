from collections import OrderedDict, defaultdict

from .exceptions import FieldDeclarationException, ValidationException


class cmd:
    CONNECT = 1
    PING = 2
    PINGD = 3
    QUIT = 4
    FINISH = 5


class Field:

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value.__class__ != self._type:
            raise ValidationException()
        if hasattr(self, 'validate'):
            self.validate(value)
        instance.__dict__[self.name] = value


class Cmd(Field):
    _type = int
    serialize = staticmethod(lambda x: x.to_bytes(1, 'little'))
    deserialize = staticmethod(lambda data: (data[0], data[1:]))

    def __init__(self, _id):
        self.id = _id


class Str(Field):
    _type = str

    def __init__(self, maxsize):
        self.maxsize = maxsize

    def validate(self, value):
        if len(value) > self.maxsize:
            raise ValidationException()

    @staticmethod
    def serialize(value):
        return bytes(value, 'utf-8')

    @staticmethod
    def deserialize(value):
        return (value.decode('utf-8'), None)


class Int(Field):
    _type = int

    @staticmethod
    def serialize(value):
        return value.to_bytes(4, 'little')

    @staticmethod
    def deserialize(value):
        return int.from_bytes(value, 'little')


class MetaPacket(type):

    packets = {}

    def __prepare__(name, bases):
        return OrderedDict()

    def __init__(self, name, bases, dct):
        if name == 'Packet':
            return
        cmd = dct.get('cmd')
        if not cmd:
            raise FieldDeclarationException()
        self.__class__.packets[cmd.id] = self
        self.fields = OrderedDict()
        for attr, value in dct.items():
            if isinstance(value, Field):
                value.name = attr
                self.fields[attr] = value


class Packet(metaclass=MetaPacket):

    def __init__(self, **kwargs):
        names = list(self.fields.keys())
        cmd = self.fields[names[0]].id
        setattr(self, names[0], cmd)
        for attr in names[1:]:
            value = kwargs.get(attr)
            if value is None:
                raise ValidationException()
            setattr(self, attr, value)

    def pack(self):
        result = bytes()
        for attr, _type in self.fields.items():
            result += _type.serialize(getattr(self, attr))

        return Int.serialize(len(result)) + result

    @classmethod
    def unpack(cls, data: bytes):
        kwargs = {}
        pack_cls = cls.__class__.packets.get(data[0])
        if pack_cls is None:
            raise ValidationException()

        tail = data
        for attr, _type in pack_cls.fields.items():
            value, tail = _type.deserialize(tail)
            kwargs[attr] = value

        return pack_cls(**kwargs)


class Ping(Packet):
    cmd = Cmd(cmd.PING)


class PingD(Packet):
    cmd = Cmd(cmd.PINGD)
    data = Str(maxsize=256)