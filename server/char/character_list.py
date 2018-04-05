from pyraknet.bitstream import Serializable, c_uint8, c_uint16, c_uint32, c_uint64, c_bool
from plugin import Plugin, Action, Packet
from structs import LUHeader, CString, GameVersion, Character

class CharacterList(Plugin):
    def actions(self):
        return [
            Action('pkt:client_character_list_request', self.character_list, 10)
        ]

    def packets(self):
        return [
            ClientCharacterListRequest,
            CharacterListResponse
        ]

    def character_list(self, packet, address):
        

        res = LoginResponse(auth_status, token, char_ip, chat_ip, char_port, chat_port, new_subscriber, ftp, permission_error)

        self.server.rnserver.send(res, address)

class ClientCharacterListRequest(Packet):
    packet_name = 'client_character_list_request'

    @classmethod
    def deserialize(cls, stream):
        return cls()

class CharacterListResponse(Packet):
    packet_name = 'character_list_response'

    def __init__(self, characters):
        super().__init__(**{k:v for k,v in locals().items() if k != 'self'})

    def serialize(self, stream):
        super().serialize(stream)
        front_char = self.server.handle_until_value('user:front_char', True, self.characters[0].user_id)
        stream.write(c_uint8(front_char))
        stream.write(len(self.characters))
        for character in self.characters:
            character.serialize(stream)
