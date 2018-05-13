"""
Enums
"""

from pyraknet.bitstream import c_int32, c_float, c_double, c_uint32, c_bool, c_int64


LDF_VALUE_TYPES = {
    0: str,
    1: int,
    2: int,
    3: float,
    4: int,
    5: int,
    6: int,
    7: bool,
    8: int,
    9: int,
    10: str,
    11: str,
    12: str,
    13: str,
    14: str,
}


ZONE_LUZ = {
    0: 'luz/nd_space_ship.luz',
    1000: 'luz/nd_space_ship.luz',
    1100: 'luz/nd_avant_gardens.luz',
    1200: 'luz/nd_nimbus_station.luz',
}


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
    0: 0x20b8087c,
    1000: 0x20b8087c,
    1001: 0x26680a3c,
    1100: 0x49525511,
    1101: 0x538214e2,
    1102: 0x0fd403da,
    1150: 0x0fd403da,
    1151: 0x0a890303,
    1200: 0xda1e6b30,
    1201: 0x476e1330,
    1203: 0x10fc0502,
    1204: 0x07d40258,
}


ZONE_SPAWNPOINTS = {
    0: [-627.1862, 613.326233, -47.2231674],
    1000: [-627.1862, 613.326233, -47.2231674],
    1001: [-187.2391, 608.2743, 54.5554352],
    1100: [522.9949, 406.040375, 129.992722],
    1101: [35.0297, 365.780426, -201.578369],
    1102: [-18.7062054, 440.20932, 37.5326424],
    1150: [-18.7062054, 440.20932, 37.5326424],
    1151: [25.0526543, 472.215027, -24.318882],
    1200: [-40.0, 293.047, -16.0],
    1201: [111.670906, 229.282776, 179.87793],
    1203: [0.0, 0.0, 0.0],
    1204: [-12.1019106, 212.900024, 191.147964],
}


class GameMessageID:
    """
    Game messages
    """
    DONE_LOADING_OBJECTS = 0x066a
    NOTIFY_CLIENT_FLAG_CHANGE = 0x1d8
    PLAYER_READY = 0x01fd
    OFFER_MISSION = 0x00f8
    READY_FOR_UPDATES = 0x0378
    REQUEST_USE = 0x016c
    RESPOND_TO_MISSION = 0x00f9
    NOTIFY_MISSION = 0x00fe
    NOTIFY_MISSION_TASK = 0x00ff
    MISSION_DIALOGUE_OK = 0x0208
    MISSION_DIALOGUE_CANCELLED = 0x0469
    REQUEST_LINKED_MISSION = 0x0203


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
        0x05: 'client_game_message',
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
