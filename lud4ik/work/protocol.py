from collections import OrderedDict

from .fields import Field, Int, Cmd
from .exceptions import FieldDeclarationError, ValidationError


class MetaPacket(type):

    packets = {}

    def __prepare__(name, bases):
        return OrderedDict()

    def __init__(self, name, bases, dct):
        if name == 'Packet':
            return

        for value in dct.values():
            if isinstance(value, Cmd):
                cmd = value
                break
        else:
            raise FieldDeclarationError()

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
                raise ValidationError()
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
            raise ValidationError()

        tail = data
        for attr, _type in pack_cls.fields.items():
            value, tail = _type.deserialize(tail)
            kwargs[attr] = value

        return pack_cls(**kwargs)


class Feeder:

    LENGTH = 4

    def __init__(self):
        self._len = None

    def feed(self, buffer):
        if self._len is None:
            if len(buffer) < self.LENGTH:
                return None, buffer
            self._len = Int.deserialize(buffer[:self.LENGTH])
            buffer = buffer[self.LENGTH:]

        if len(buffer) < self._len:
            return None, buffer
        else:
            _len = self._len
            self._len = None
            return Packet.unpack(buffer[:_len]), buffer[_len:]