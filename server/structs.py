from typing import overload, NamedTuple
from abc import ABCMeta
from pyraknet.bitstream import Serializable, c_uint8, c_uint16, c_uint32, c_uint64, c_int8, c_int16, c_int32, c_int64, c_bool
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

class Character(Serializable):
    def __init__(self, character_id, unknown1, character_name, character_unapproved_name, is_name_rejected, free_to_play,
                 unknown2, shirt_color, shirt_style, pants_color, hair_style, hair_color, lh, rh, eyebrows, eyes, mouth,
                 unknown3, last_zone, last_instance, last_clone, last_login, items
                ):
        self.character_id = character_id
        self.unknown1 = unknown1
        self.character_name = character_name
        self.character_unapproved_name = character_unapproved_name
        self.is_name_rejected = is_name_rejected
        self.free_to_play = free_to_play
        self.unknown2 = unknown2
        self.shirt_color = shirt_color
        self.shirt_style = shirt_style
        self.pants_color = pants_color
        self.hair_style = hair_style
        self.hair_color = hair_color
        self.lh = lh
        self.rh = rh
        self.eyebrows = eyebrows
        self.eyes = eyes
        self.mouth = mouth
        self.unknown3 = unknown3
        self.last_zone = last_zone
        self.last_instance = last_instance
        self.last_clone = last_clone
        self.last_login = last_login
        self.items = items


    def serialize(self, stream):
        stream.write(c_int64(character_id))
        stream.write(c_uint32(unknown1))
        stream.write(character_name)
        stream.write(character_unapproved_name)
        stream.write(is_name_rejected)
        stream.write(free_to_play)
        stream.write(unknown2, allocated_length=10)
        stream.write(c_uint32(shirt_color))
        stream.write(c_uint32(shirt_style))
        stream.write(c_uint32(pants_color))
        stream.write(c_uint32(hair_style))
        stream.write(c_uint32(hair_color))
        stream.write(c_uint32(lh))
        stream.write(c_uint32(rh))
        stream.write(c_uint32(eyebrows))
        stream.write(c_uint32(eyes))
        stream.write(c_uint32(mouth))
        stream.write(c_uint32(unknown3))
        stream.write(c_uint16(last_zone))
        stream.write(c_uint16(last_instance))
        stream.write(c_uint32(last_clone))
        stream.write(c_uint64(last_login))
        stream.write(c_uint16(len(items)))
        for item in items:
            stream.write(c_uint32(item))

    @classmethod
    def deserialize(cls, stream):
        character_id = stream.read(c_int64)
        unknown1 = stream.read(c_uint32)
        character_name = stream.read(CString(self.unknown, allocated_length=66))
        character_unapproved_name = stream.read(CString(self.unknown, allocated_length=66))
        is_name_rejected = stream.read(c_bool)
        free_to_play = stream.read(c_bool)
        unknown2 = stream.read(bytes, allocated_length=10)
        shirt_color = stream.read(c_uint32)
        shirt_style = stream.read(c_uint32)
        pants_color = stream.read(c_uint32)
        hair_style = stream.read(c_uint32)
        hair_color = stream.read(c_uint32)
        lh = stream.read(c_uint32)
        rh = stream.read(c_uint32)
        eyebrows = stream.read(c_uint32)
        eyes = stream.read(c_uint32)
        mouth = stream.read(c_uint32)
        unknown3 = stream.read(c_uint32)
        last_zone = stream.read(c_uint16)
        last_instance = stream.read(c_uint16)
        last_clone = stream.read(c_uint32)
        last_login = stream.read(c_uint64)
        item_count = stream.read(c_uint16)
        items = []
        for item in range(item_count):
            items.append(stream.read(c_uint32))

        return cls(character_id, unknown1, character_name, character_unapproved_name, is_name_rejected, free_to_play,
                     unknown2, shirt_color, shirt_style, pants_color, hair_style, hair_color, lh, rh, eyebrows, eyes, mouth,
                     unknown3, last_zone, last_instance, last_clone, last_login, items)


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
