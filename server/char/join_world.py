"""
Join
"""

from pyraknet.bitstream import Serializable, c_int64, c_uint16, c_uint32, c_float

from char.list import CharacterListResponse, Character as Minifigure
from replica.player import Player
from plugin import Plugin, Action, Packet
from structs import CString


class JoinWorld(Plugin):
    """
    Create character plugin
    """
    def actions(self):
        """
        Returns list of actions
        """
        return [
            Action('pkt:join_world_request', self.join_world_request, 10)
        ]

    def packets(self):
        """
        Returns list of packets
        """
        return [
            JoinWorldRequest
        ]

    def join_world_request(self, packet, address):
        """
        Handles the packet
        """
        char_id = packet.character_id

        char = self.server.handle_until_return('char:characters', 1)[0]  # TODO: make this not just get the first character of the first user

        res = WorldInfo(1000,
                        0,
                        0,
                        0x7c08b820,
                        0,
                        0,
                        1,
                        0,
                        0)

        self.server.rnserver.send(res, address)
        self.server.repman.add_participant(address)
        self.server.repman.construct(Player(char.name))


class JoinWorldRequest(Packet):
    """
    Join world request packet
    """
    packet_name = 'join_world_request'

    def __init__(self, character_id):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    @classmethod
    def deserialize(cls, stream):
        """
        Deserializes the packet
        """
        char_id = stream.read(c_int64)

        return cls(char_id)


class WorldInfo(Packet):
    """
    World info packet
    """
    packet_name = 'world_info'

    def __init__(self, zone_id, map_instance, map_clone, map_checksum, unknown1, pos_x, pos_y, pos_z, is_activity):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)

        stream.write(c_uint16(self.zone_id))
        stream.write(c_uint16(self.map_instance))
        stream.write(c_uint32(self.map_clone))
        stream.write(c_uint32(self.map_checksum))
        stream.write(c_uint16(self.unknown1))
        stream.write(c_float(self.pos_x))
        stream.write(c_float(self.pos_y))
        stream.write(c_float(self.pos_z))
        stream.write(c_uint32(self.is_activity))
