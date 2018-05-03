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
    # Client World
    0x04: {
        0x01: 'session_info'
    },
    # Server
    0x05: {
        0x00: 'login_response',
    }
}

PACKET_IDS = {name:(type,id) for type, types in PACKET_NAMES.items() for id,name in types.items()}