"""
Structs
"""

from typing import overload

from pyraknet.bitstream import Serializable, c_uint8, c_uint16, c_uint32
from enums import PACKET_IDS, PACKET_NAMES


class WString(Serializable):
    """
    wstring serializable
    """
    def __init__(self, data='', length=33):
        self.data = data
        self.length = length

    def serialize(self, stream):
        if len(self.data) < self.length:
            self.data += '\0' * (self.length - len(self.data))

        for i in range(self.length):
            stream.write(c_uint8(ord(self.data[i])))
            stream.write(c_uint8(0))

    @classmethod
    def deserialize(cls, stream):
        data = ''

        for _ in range(33):
            data += chr(stream.read(c_uint8))
            stream.read(c_uint8)

        return cls(data)


class CString(Serializable):
    """
    C string serializable
    """
    def __init__(self, data='', allocated_length=None, length_type=None):
        self.data = data
        self.allocated_length = allocated_length
        self.length_type = length_type

    def serialize(self, stream):
        stream.write(self.data if isinstance(self.data, bytes) else bytes(self.data, 'latin1'),
                     allocated_length=self.allocated_length, length_type=self.length_type)

    def deserialize(self, stream):
        return stream.read(bytes, allocated_length=self.allocated_length, length_type=self.length_type).decode('latin1')


class LUHeader(Serializable):
    """
    LEGO Universe header serializable
    """
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
        """
        Returns the remote connection ID
        """
        if getattr(self, 'packet_name', None):
            return PACKET_IDS[self.packet_name][0]
        return self.raw_ids[0]

    @property
    def packet_id(self):
        """
        Returns the packet ID
        """
        if getattr(self, 'packet_name', None):
            return PACKET_IDS[self.packet_name][1]
        return self.raw_ids[1]

    def serialize(self, stream):
        stream.write(c_uint8(0x53))
        stream.write(c_uint16(self.remote_conn_id))
        stream.write(c_uint32(self.packet_id))
        stream.write(c_uint8(0x00))

    @classmethod
    def deserialize(cls, stream):
        stream.read(c_uint8)  # rntype
        remote_conn_id = stream.read(c_uint16)
        packet_id = stream.read(c_uint32)
        stream.read(c_uint8)  # unknown

        packet_name = PACKET_NAMES.get(remote_conn_id, {}).get(packet_id, None)

        if packet_name:
            return cls(packet_name)

        return cls(remote_conn_id, packet_id)
