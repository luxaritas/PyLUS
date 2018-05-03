from typing import overload, NamedTuple
from abc import ABCMeta
from pyraknet.bitstream import Serializable, c_uint8, c_uint16, c_uint32
from enums import PACKET_IDS, PACKET_NAMES

class GameVersion(Serializable):
    def __init__(self, major, current, minor):
        self.major = major
        self.current = current
        self.minor = minor

    def serialize(self, stream):
        stream.write(c_uint16(self.major))
        stream.write(c_uint16(self.current))
        stream.write(c_uint16(self.minor))

    @classmethod
    def deserialize(cls, stream):
        return cls(stream.read(c_uint16), stream.read(c_uint16), stream.read(c_uint16))

class CString(Serializable):
    def __init__(self, data, allocated_length=None, length_type=None):
        self.data = data
        self.allocated_length = allocated_length
        self.length_type = length_type

    def serialize(self, stream):
        stream.write(self.data if isinstance(self.data, bytes) else bytes(self.data, 'latin1'),
                     allocated_length=self.allocated_length, length_type=self.length_type)

    def deserialize(self, stream):
        return stream.read(bytes, allocated_length=self.allocated_length, length_type=self.length_type).decode('latin1')


class LUHeader(Serializable):
    @overload
    def __init__(self, packet_name: str):
        pass

    @overload
    def __init__(self, remote_conn_id: int, packet_id: int):
        pass

    def __init__(self, *args):
        if isinstance(args[0], str):
            self.packet_name = args[0]

        else:
            self.raw_ids = (args[0], args[1])

    @property
    def remote_conn_id(self):
        if getattr(self, 'packet_name', None) is not None:
            return PACKET_IDS[self.packet_name][0]
        return self.raw_ids[0]

    @property
    def packet_id(self):
        if getattr(self, 'packet_name', None) is not None:
            return PACKET_IDS[self.packet_name][1]
        return self.raw_ids[1]

    def serialize(self, stream):
        stream.write(c_uint8(0x53))
        stream.write(c_uint16(self.remote_conn_id))
        stream.write(c_uint32(self.packet_id))
        stream.write(c_uint8(0x00))

    @classmethod
    def deserialize(cls, stream):
        rntype = stream.read(c_uint8)
        remote_conn_id = stream.read(c_uint16)
        packet_id = stream.read(c_uint32)
        unknown = stream.read(c_uint8)

        packet_name = PACKET_NAMES.get(remote_conn_id, {}).get(packet_id, None)

        if packet_name is not None:
            return cls(packet_name)

        return cls(remote_conn_id, packet_id)
