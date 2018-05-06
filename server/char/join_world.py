"""
Join world
"""

from pyraknet.bitstream import WriteStream, c_int, c_int64, c_uint, c_uint8, c_uint16, c_uint32, c_float, c_bool

from char.list import CharacterListResponse, Character as Minifigure
from replica.player import Player
from plugin import Plugin, Action
from enums import ZONE_CHECKSUMS, GameMessageID
from structs import GameMessage, Packet


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

        char = self.server.handle_until_return('char:get_character', char_id)

        res = WorldInfo(char.last_zone,
                        0,
                        0,
                        ZONE_CHECKSUMS[char.last_zone],
                        0,
                        0,
                        1,
                        0,
                        0)

        char_info = DetailedUserInfo(char_id)
        obj_load = GameMessage(char_id, GameMessageID.DONE_LOADING_OBJECTS.value)
        player_ready = GameMessage(char_id, GameMessageID.PLAYER_READY.value)

        self.server.rnserver.send(res, address)
        self.server.rnserver.send(char_info, address)
        self.server.repman.add_participant(address)
        self.server.repman.construct(Player(char_id, char.name))
        self.server.rnserver.send(obj_load, address)
        self.server.rnserver.send(player_ready, address)


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

class DetailedUserInfo(Packet):
    """
    Character data packet
    """
    packet_name = 'detailed_user_info'

    def __init__(self, objid):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)

        ldf = WriteStream()

        ldf.write(c_uint(2))

        ldf.write('objid', length_type=c_uint8)
        ldf.write(c_uint8(9))
        ldf.write(c_int64(self.objid))

        ldf.write('template', length_type=c_uint8)
        ldf.write(c_uint8(1))
        ldf.write(c_int(1))

        ldf_bytes = bytes(ldf)

        stream.write(c_uint32(len(ldf_bytes) + 5))
        stream.write(c_bool(False))
        stream.write(ldf_bytes)
