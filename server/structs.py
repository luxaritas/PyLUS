"""
Structs
"""

from typing import overload
from xml.etree import ElementTree

from pyraknet.bitstream import WriteStream, Serializable, c_uint8, c_uint16, c_uint32, c_int32, c_int64, c_float, c_bit, \
                               c_double, c_uint

from enums import PACKET_IDS, PACKET_NAMES


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

        packet_name = PACKET_NAMES.get(remote_conn_id, {}).get(packet_id)

        if packet_name:
            return cls(packet_name)

        return cls(remote_conn_id, packet_id)


class LegoDataKey(Serializable):
    """
    LDF key serializable
    """
    def __init__(self, key, data, data_type=None):
        self.key = key
        self.data = data
        self.data_type = data_type

    def serialize(self, stream):
        stream.write(c_uint8(len(self.key) * 2))

        for char in self.key:
            stream.write(char.encode('latin1'))
            stream.write(b'\0')

        if not self.data_type:
            if isinstance(self.data, str):
                stream.write(c_uint8(0))

                stream.write(c_uint(len(self.data) * 2))

                for char in self.data:
                    stream.write(char.encode('latin1'))
                    stream.write(b'\0')

            elif isinstance(self.data, c_int32):
                stream.write(c_uint8(1))
            elif isinstance(self.data, c_float):
                stream.write(c_uint8(3))
            elif isinstance(self.data, c_double):
                stream.write(c_uint8(4))
            elif isinstance(self.data, c_uint32):
                stream.write(c_uint8(5))
            elif isinstance(self.data, c_bit):
                stream.write(c_uint8(7))
            elif isinstance(self.data, c_int64):
                stream.write(c_uint8(8))
            elif isinstance(self.data, ElementTree.Element):
                stream.write(c_uint8(13))

                txt = '<?xml version="1.0"?>' + ElementTree.tostring(self.data).decode('latin1')

                stream.write(c_uint32(len(txt) * 2))

                for char in txt:
                    stream.write(char.encode('latin1'))
                    stream.write(b'\0')

            if not isinstance(self.data, str) and not isinstance(self.data, ElementTree.Element):
                stream.write(self.data)
        else:
            stream.write(c_uint8(self.data_type))
            stream.write(self.data)

    @classmethod
    def deserialize(cls, stream):
        pass


class LegoData(Serializable):
    """
    LDF serializable
    """
    def __init__(self):
        self.keys = []

    def write(self, key, data, data_type=None):
        ldf_key = LegoDataKey(key, data, data_type)

        self.keys.append(ldf_key)

    def serialize(self, stream):
        super().serialize(stream)

        stream.write(c_uint32(len(self.keys)))

        for key in self.keys:
            key.serialize(stream)

    @classmethod
    def deserialize(cls, stream):
        return cls()


class Packet(Serializable):
    """
    Packet class
    """
    allow_without_session = False

    @overload
    def __init__(self):
        pass

    def __init__(self, header: LUHeader = None, data: bytes = None, **kwargs):
        packet_name = getattr(self.__class__, 'packet_name', None)

        if packet_name:
            self.header = LUHeader(packet_name)
            for prop, val in kwargs.items():
                setattr(self, prop, val)
        elif header and data != None:
            self.header = header
            self.data = data
        else:
            raise KeyError('Packets must either be instantiated from a base class with a packet_name, Packet.deserialize(), or with a header and data argument')

    def __bytes__(self):
        stream = WriteStream()
        self.serialize(stream)
        return bytes(stream)

    def serialize(self, stream):
        """
        Serialize the packet
        """
        self.header.serialize(stream)
        if getattr(self, 'data', None) is not None:
            stream.write(self.data)

    @classmethod
    def deserialize(cls, stream, packet_types):
        """
        Deserialize the packet
        """
        header = LUHeader.deserialize(stream)
        packet = packet_types.get(getattr(header, 'packet_name', None))

        if packet:
            return packet.deserialize(stream)

        return cls(header=header, data=stream.read_remaining())


class GameMessage(Packet):
    """
    Game message packet
    """
    packet_name = 'server_game_message'

    def __init__(self, objid, message_id, data=None):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        super().serialize(stream)

        stream.write(c_int64(self.objid))
        stream.write(c_uint16(self.message_id))

        if getattr(self, 'data', None):
            if isinstance(self.data, bytes):
                stream.write(self.data)
            else:
                stream.write(bytes(self.data))
