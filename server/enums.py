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
        0x01: 'client_character_list_request',
    },
    # Server
    0x05: {
        0x00: 'login_response',
        0x06: 'character_list_response',
    }
}

PACKET_IDS = {name:(type,id) for type, types in PACKET_NAMES.items() for id,name in types.items()}
