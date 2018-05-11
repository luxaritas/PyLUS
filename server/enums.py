"""
Enums
"""

from enum import IntEnum

from pyraknet.bitstream import c_int32, c_float, c_double, c_uint32, c_bool, c_int64


LEGO_DATA_TYPES = {
    str: 0,
    c_int32: 1,
    c_float: 3,
    c_double: 4,
    c_uint32: 5,
    c_bool: 7,
    c_int64: 8,
}


ZONE_CHECKSUMS = {
    1000: 0x20b8087c,
    1001: 0x26680a3c,
    1002: 0x49525511,
    1003: 0x538214e2,
    1004: 0x0fd403da,
}


class GameMessageID(IntEnum):
    """
    Game messages
    """
    DONE_LOADING_OBJECTS = 0x066a
    NOTIFY_CLIENT_FLAG_CHANGE = 0x1d8
    PLAYER_READY = 0x01fd


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
        0x13: 'client_load_complete',
        0x15: 'routed_packet',
        0x16: 'position_update',
    },
    # Server
    0x05: {
        0x00: 'login_response',
        0x02: 'world_info',
        0x04: 'detailed_user_info',
        0x06: 'character_list_response',
        0x07: 'minifig_create_response',
        0x0c: 'server_game_message',
    }
}

PACKET_IDS = {name: (p_type, id) for p_type, types in PACKET_NAMES.items() for id, name in types.items()}
