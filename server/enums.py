"""
Enums
"""

from enum import IntEnum


class ZoneChecksum(IntEnum):
    VENTURE_EXPLORER = 0x20b8087c
    RETURN_TO_VENTURE_EXPLORER = 0x26680a3c
    AVANT_GARDENS = 0x49525511
    AVANT_GARDENS_SURVIVAL = 0x538214e2
    SPIDER_QUEEN_BATTLE = 0x0fd403da
    BLOCK_YARD = 0x0fd403da
    AVANT_GROVE = 0x0a890303
    NIMBUS_STATION = 0xda1e6b30
    PET_COVE = 0x476e1330
    VERTIGO_LOOP = 0x10fc0502
    BATTLE_OF_NIMBUS_STATION = 0x07d40258
    NIMBUS_ROCK = 0x058d0191
    NIMBUS_ISLE = 0x094f045d
    GNARLED_FOREST = 0x12eac290
    CANYON_COVE = 0x0b7702ef
    KEELHAUL_CANYON = 0x152e078a
    CHANTEY_SHANTEY = 0x04b6015c
    FORBIDDEN_VALLEY = 0x8519760d
    FORBIDDEN_VALLEY_DRAGON = 0x02f50187
    DRAGONMAW_CHASM = 0x81850f4e
    RAVEN_BLUFF = 0x03f00126
    STARBASE_3001 = 0x07c202ee
    DEEP_FREEZE = 0x02320106
    ROBOT_CITY = 0x0793037f
    MOON_BASE = 0x043b01ad
    PORTABELLO = 0x181507dd
    LEGO_CLUB = 0x02040138
    CRUX_PRIME = 0x4b17a399
    NEXUS_TOWER = 0x9e4af43c
    NINJAGO = 0x4d692c74
    FRAKJAW_BATTLE = 0x09eb00ef


PACKET_NAMES = {
    # General
    0x00: {
        0x00: 'handshake',
        0x01: 'disconnect',
    },
    # Client Auth
    0x01: {
        0x00: 'login_request',
    },
    # Chat
    0x02: {

    },
    # Client World/Char
    0x04: {
        0x01: 'session_info',
        0x02: 'character_list_request',
        0x03: 'minifig_create_request',
        0x04: 'join_world_request',
    },
    # Server
    0x05: {
        0x00: 'login_response',
        0x02: 'world_info',
        0x06: 'character_list_response',
        0x07: 'minifig_create_response',
    }
}

PACKET_IDS = {name: (p_type, id) for p_type, types in PACKET_NAMES.items() for id, name in types.items()}
