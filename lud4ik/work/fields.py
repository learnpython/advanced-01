from .exceptions import ValidationError


class Field:

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value.__class__ != self._type:
            raise ValidationError()
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
            raise ValidationError()

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