"""
Handles world entry
"""

import zlib
from xml.etree import ElementTree

from pyraknet.bitstream import WriteStream, c_uint16, c_uint32, c_int32, c_int64, c_float, c_bool

from server.plugin import Plugin, Action
from server.structs import Packet, LegoData
from server.enums import ZONE_IDS, ZONE_CHECKSUMS

from server.replica.player import Player

from server.structs import ServerGameMessage, Vector3, Vector4
from server.enums import GameMessageID, ZONE_SPAWNPOINTS
from cms.game.models import Mission

class WorldJoin(Plugin):
    """
    World entry plugin
    """

    def actions(self):
        """
        Returns list of actions
        """
        return [
            Action('session:verify_success', self.load_world, 10),
            Action('pkt:client_load_complete', self.client_load_complete, 10),
        ]

    def load_world(self, session):
        zone_id = ZONE_IDS[self.server.type]
        self.server.handle('world:zone_entered', session, zone_id)

        res = WorldInfo(zone_id,
                        0, # Instance
                        0, # Clone
                        ZONE_CHECKSUMS[zone_id],
                        Vector3(*ZONE_SPAWNPOINTS[zone_id]),
                        0) # Activity

        self.server.rnserver.send(res, (session.ip, session.port))

    def client_load_complete(self, packet, address):
        session = self.server.handle_until_return('session:get_session', address)

        char_info = DetailedUserInfo(
            session.account.user.pk,
            session.character.name,
            ZONE_IDS[self.server.type],
            session.character.pk,
            missions=[Mission(mission=1727, character=session.character, state=8, times_completed=1, last_completion=0)]
        )
        self.server.rnserver.send(char_info, address)

        self.server.repman.add_participant(address)

        player = Player(session.character, Vector3(*ZONE_SPAWNPOINTS[ZONE_IDS[self.server.type]]), Vector4(0,0,0))
        self.server.repman.construct(player, True)

        obj_load = ServerGameMessage(session.character.pk, GameMessageID.DONE_LOADING_OBJECTS)
        self.server.rnserver.send(obj_load, address)

        player_ready = ServerGameMessage(session.character.pk, GameMessageID.PLAYER_READY)
        self.server.rnserver.send(player_ready, address)

class WorldInfo(Packet):
    """
    World info packet
    """
    packet_name = 'world_info'

    def __init__(self, zone_id, map_instance, map_clone, map_checksum, pos, is_activity, unknown1=0):
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
        stream.write(c_float(self.pos.x))
        stream.write(c_float(self.pos.y))
        stream.write(c_float(self.pos.z))
        stream.write(c_uint32(self.is_activity))

class DetailedUserInfo(Packet):
    """
    Character data packet
    """
    packet_name = 'detailed_user_info'

    def __init__(self, account_id, name, zone_id, objid, inventory_space=8, currency=0, level=1, missions=[]):
        super().__init__(**{k: v for k, v in locals().items() if k != 'self'})

    def serialize(self, stream):
        """
        Serializes the packet
        """
        super().serialize(stream)

        # TODO: Make this stuff dynamic instead of just empty

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

        xml.start('cur', {})
        for mission in [mission for mission in self.missions if mission.state == 2]:
            xml.start('m', {'id': str(mission.mission), 'o': '1'})
            xml.start('sv', {'v': str(mission.progress)})
            xml.end('sv')
            xml.end('m')
        xml.end('cur')

        xml.start('done', {})
        for mission in [mission for mission in self.missions if mission.state == 8]:
            xml.start('m', {'cct': str(mission.times_completed), 'id': str(mission.mission),
                            'cts': str(mission.last_completion)})
            xml.end('m')
        xml.end('done')

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
