import abc, collections
import inspect
import uuid


class BaseField(metaclass=abc.ABCMeta):
    name = NotImplemented

    def __get__(self, instance, owner):
        assert self.name is not NotImplemented
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        assert self.name is not NotImplemented
        self.type_check(value)
        instance.__dict__[self.name] = value

    @abc.abstractmethod
    def type_check(self, value):
        return False

    @abc.abstractmethod
    def load(self, instance, from_data, start=0):
        pass

    @abc.abstractmethod
    def store(self, instance):
        pass


class SignedNumber(BaseField):
    def __init__(self, bytes_len):
        assert bytes_len in (1, 2, 4, 8)
        self.bytes_len = bytes_len
        self.max_val = 2**(bytes_len*8 - 1) - 1
        self.min_val = -2**(bytes_len*8 - 1)

    def type_check(self, value):
        if not isinstance(value, int):
            raise TypeError("{!r}: invalid value type {!r}"
                            .format(self.name, type(value)))
        if not self.min_val <= value <= self.max_val:
            raise ValueError("{!r}: {} not in range [{}, {}]"
                             .format(self.name, value,
                                     self.min_val, self.max_val))

    def load(self, instance, from_data, start=0):
        bval = from_data[start: start+self.bytes_len]
        val = int.from_bytes(bval, 'big', signed=True)
        setattr(instance, self.name, val)
        return start + self.bytes_len

    def store(self, instance):
        val = getattr(instance, self.name)
        bval = val.to_bytes(self.bytes_len, 'big', signed=True)
        return bval

    def __repr__(self):
        return '<SignedNumber({})>'.format(self.bytes_len)


class String(BaseField):
    def type_check(self, value):
        if not isinstance(value, str):
            raise TypeError("{!r}: invalid value type {!r}"
                            .format(self.name, type(value)))

    def load(self, instance, from_data, start=0):
        bval_len = from_data[start: start+4]
        val_len = int.from_bytes(bval_len, 'big')
        bval = from_data[start+4: start+val_len+4]
        val = bval.decode('utf8')
        setattr(instance, self.name, val)
        return start + val_len + 4

    def store(self, instance):
        val = getattr(instance, self.name)
        bval = val.encode('utf8')
        val_len = len(bval)
        return val_len.to_bytes(4, 'big') + bval

    def __repr__(self):
        return '<String>'


class UUID(BaseField):
    LEN = 16

    def type_check(self, value):
        if not isinstance(value, uuid.UUID):
            raise TypeError("{!r}: invalid value type {!r}"
                            .format(self.name, type(value)))

    def load(self, instance, from_data, start=0):
        bval = from_data[start: start+self.LEN]
        # TODO: allow to construct UUID from bytearray and any buffer object
        val = uuid.UUID(bytes=bytes(bval))
        setattr(instance, self.name, val)
        return start + self.LEN

    def store(self, instance):
        val = getattr(instance, self.name)
        bval = val.bytes
        return bval

    def __repr__(self):
        return '<UUID>'


class Namespace(collections.OrderedDict):
    def __init__(self):
        super().__init__()
        self.fields = []

    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        if isinstance(val, BaseField):
            val.name = key
            self.fields.append(val)


class MetaMsg(type):

    @classmethod
    def __prepare__(cls, name, bases, *, root=False):
        return Namespace()

    def __new__(cls, name, bases, dct, *, root=False):
        return super().__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct, *, root=False):
        super().__init__(name, bases, dct)
        if root:
            return
        used_kinds = cls.KIND_MAP.values()
        if not used_kinds:
            kind = 1
        else:
            kind = max(used_kinds) + 1
            assert kind < 255
        cls.KIND = kind
        cls.KIND_MAP[kind] = cls
        cls.KIND_NAMES[name] = kind
        cls.FIELDS = dct.fields
        sig = inspect.signature(cls.__init__)
        params = [inspect.Parameter('self',
                                  inspect.Parameter.POSITIONAL_ONLY)]
        for f in dct.fields:
            param = inspect.Parameter(f.name,
                                      inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                      annotation=f)
            params.append(param)
        cls.SIG = sig.replace(parameters=params)


class BaseMsg(metaclass=MetaMsg, root=True):
    KIND = NotImplemented
    KIND_MAP = {}
    KIND_NAMES = {}
    FIELDS = NotImplemented
    SIG = NotImplemented

    def __init__(self, *args, **kwargs):
        params = self.SIG.parameters
        bound = self.SIG.bind(self, *args, **kwargs)
        for k, v in bound.arguments.items():
            if k != 'self':
                params[k].annotation.type_check(v)
                setattr(self, k, v)

    def dumps(self):
        ret = [bytes([self.KIND])]
        for f in self.FIELDS:
            ret.append(f.store(self))
        rb = b''.join(ret)
        return (len(rb) + 4).to_bytes(4, 'big') + rb

    @classmethod
    def loads(cls, from_data):
        # TODO: replace assertions with raising exceptions, add tests
        assert len(from_data) >= 5, len(from_data)
        msg_len = int.from_bytes(from_data[:4], 'big')
        assert len(from_data) >= msg_len, "{} != {}".format(
            len(from_data), msg_len)
        kind = from_data[4]
        try:
            real_type = cls.KIND_MAP[kind]
        except KeyError:
            raise ValueError("Unknown msg kind {}".format(kind))
        start = 5
        self = real_type.__new__(real_type)
        for f in self.FIELDS:
            start = f.load(self, from_data, start)
        assert msg_len == start, "{} != {}".format(msg_len, start)
        return self


def feeder():
    buf = bytearray()
    while True:
        while len(buf) < 5:
            inp = yield None
            buf.extend(inp)
        msg_len = int.from_bytes(buf[:4], 'big')
        while len(buf) < msg_len:
            inp = yield None
            buf.extend(inp)
        msg = BaseMsg.loads(buf)
        del buf[:msg_len]
        inp = yield msg
        buf.extend(inp)


class ConnectMsg(BaseMsg):
    clientid = UUID()
