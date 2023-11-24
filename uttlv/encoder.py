from __future__ import annotations

from binascii import hexlify
import struct

class DefaultEncoder(object):
    def __init__(self, endian:str = "big"):
        self.endian=endian

    def default(self, obj):
        try:
            return obj.to_byte_array()
        except AttributeError:
            raise TypeError("Invalid type")

    def to_string(self, obj, offset=0, use_names=False):
        try:
            return obj.tree(offset + obj.indent, use_names)
        except AttributeError:
            pass
        return str(obj)

    def parse(self, obj, cls):
        try:
            cls.parse_array(obj)
            return cls
        except AttributeError:
            pass
        return obj


class IntEncoder(DefaultEncoder):
    def __init__(self, endian="big"):
        super().__init__(endian)

    def default(self, obj):
        if isinstance(obj, int):
            return obj.to_bytes(4, byteorder=self.endian)
        if isinstance(obj, list) and isinstance(obj[0], int):
            count = len(obj)
            if (self.endian=="big"):
                fmt = f'>{count}i'
            elif (self.endian=="little"):
                fmt = f'<{count}i'
            return struct.pack(fmt, *obj)

        return super().default(obj)

    def parse(self, obj, _cls):
        count = len(obj) // 4
        if (self.endian=="big"):
            fmt = f'>{count}i'
        elif (self.endian=="little"):
            fmt = f'<{count}i'

        ret = list(struct.unpack(fmt, obj))
        if len(ret) == 1:
            return ret[0]
        return ret

class FloatEncoder(DefaultEncoder):
    def __init__(self, endian="big"):
        super().__init__(endian)

    def default(self, obj):
        if isinstance(obj, float):
            if (self.endian=="big"):
                return bytearray(struct.pack(">f", obj))
            elif (self.endian=="little"):
                return bytearray(struct.pack("<f", obj))
        return super().default(obj)

    def parse(self, obj, _cls):
        if (self.endian=="big"):
            return struct.unpack(">f", obj)[0]
        elif (self.endian=="little"):
            return struct.unpack("<f", obj)[0]

class AsciiEncoder(DefaultEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            return obj.encode("ascii")
        return super().default(obj)

    def parse(self, obj, _cls):
        return obj.decode("ascii")


class BytesEncoder(DefaultEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj
        return super().default(obj)

    def to_string(self, obj, offset=0, use_names=False):
        return str(hexlify(obj), "ascii")

    def parse(self, obj, _cls):
        return obj


class Utf8Encoder(DefaultEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            return obj.encode("utf8")
        return super().default(obj)

    def parse(self, obj, _cls):
        return obj.decode("utf8")


class Utf16Encoder(DefaultEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            return obj.encode("utf16")
        return super().default(obj)

    def parse(self, obj, _cls):
        return obj.decode("utf16")


class Utf32Encoder(DefaultEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            return obj.encode("utf32")
        return super().default(obj)

    def parse(self, obj, _cls):
        return obj.decode("utf32")


class NestedEncoder(DefaultEncoder):
    def __init__(self, tag_map):
        self.tag_map = tag_map

    def parse(self, obj, cls):
        cls.set_local_tag_map(self.tag_map)

        return super().parse(obj, cls)
