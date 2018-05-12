"""
Join world
"""

import zlib

from xml.etree import ElementTree
from pyraknet.bitstream import WriteStream, c_int, c_int32, c_int64, c_uint, c_uint8, c_uint16, c_uint32, c_float, c_bool, c_bit

from char.list import CharacterListResponse, Character as Minifigure
from replica.player import Player
from plugin import Plugin, Action
from enums import ZONE_CHECKSUMS, ZONE_SPAWNPOINTS, GameMessageID
from structs import ServerGameMessage, Packet, LegoData, Vector3


class JoinWorld(Plugin):
    """
    Create character plugin
    """
    def actions(self):
        """
        Returns list of actions
        """
        return [
            Action('pkt:join_world_request', self.join_world_request, 10),
            Action('pkt:client_load_complete', self.client_load_complete, 10),
        ]

    def packets(self):
        """
        Returns list of packets
        """
        return [
            JoinWorldRequest,
            ClientLoadComplete,
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

        self.server.rnserver.send(res, address)

    def client_load_complete(self, packet, address):
        """
        Handles the clientside load complete packet
        """
        uid = self.server.handle_until_return('auth:get_user_id', address)
        front_char = self.server.handle_until_return('char:front_char_index', uid)
        char = self.server.handle_until_return('char:characters', uid)[front_char]

        char_info = DetailedUserInfo(char.account.user.id, char.name, packet.zone_id, char.id)
        self.server.rnserver.send(char_info, address)

        player = Player(char, Vector3.from_array(ZONE_SPAWNPOINTS[packet.zone_id]))
        self.server.repman.add_participant(address)
        self.server.repman.construct(player, True)

        obj_load = ServerGameMessage(char.id, GameMessageID.DONE_LOADING_OBJECTS.value)
        self.server.rnserver.send(obj_load, address)

        player_ready = ServerGameMessage(char.id, GameMessageID.PLAYER_READY.value)
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


class ClientLoadComplete(Packet):
    """
    Clientside load complete packet
    """
    packet_name = 'client_load_complete'

    def __init__(self, zone_id, map_instance, map_clone):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    @classmethod
    def deserialize(cls, stream):
        """
        Deserializes the packet
        """
        zone_id = stream.read(c_uint16)
        map_instance = stream.read(c_uint16)
        map_clone = stream.read(c_uint32)

        return cls(zone_id, map_instance, map_clone)


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

    def __init__(self, account_id, name, zone_id, objid, inventory_space=8, currency=0, level=1):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)

        ldf = LegoData()

        ldf.write('accountID', self.account_id, data_type=c_int64)
        ldf.write('chatmode', 0, data_type=c_int32)
        ldf.write('editor_enabled', False, data_type=c_bool)
        ldf.write('editor_level', 0, data_type=c_int32)
        ldf.write('gmlevel', 0, data_type=c_int32)
        ldf.write('levelid', self.zone_id, data_type=c_int64)
        ldf.write('objid', self.objid, data_type=c_int64, data_num=9)
        ldf.write('reputation', 100, data_type=c_int64)
        ldf.write('template', 1, data_type=c_int32)

        xml = ElementTree.TreeBuilder()

        xml.start('obj', {'v': '1'})
        xml.start('buff', {})
        xml.end('buff')
        xml.start('skill', {})
        xml.end('skill')
        xml.start('inv', {})
        xml.start('bag', {})
        xml.start('b', {'t': '0', 'm': str(self.inventory_space)})
        xml.end('b')
        xml.end('bag')
        xml.start('items', {})
        xml.start('in', {})
        # TODO: inventory stuff here
        xml.end('in')
        xml.end('items')
        xml.end('inv')
        xml.start('mf', {})
        xml.end('mf')
        xml.start('char', {'cc': str(self.currency)})
        xml.end('char')
        xml.start('lvl', {'l': str(self.level)})
        xml.end('lvl')
        xml.start('flag', {})
        xml.end('flag')
        xml.start('pet', {})
        xml.end('pet')
        xml.start('mis', {})
        # TODO: missions here
        xml.end('mis')
        xml.start('mnt', {})
        xml.end('mnt')
        xml.start('dest', {})
        xml.end('dest')
        xml.end('obj')

        ldf.write('xmlData', xml.close())

        ldf.write('name', self.name, data_type=str)

        ldf_stream = WriteStream()
        ldf_stream.write(ldf)

        ldf_bytes = bytes(ldf_stream)
        compressed = zlib.compress(ldf_bytes)

        stream.write(c_uint32(len(compressed) + 9))
        stream.write(c_bool(True))
        stream.write(c_uint32(len(ldf_bytes)))
        stream.write(c_uint32(len(compressed)))

        stream.write(compressed)
